


from .command import InterruptionBehavior
from .subsystem import Subsystem

from typing import Optional, Set, Dict, List, Callable, overload, TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING:
    from .command import Command


from wpilib.event import EventLoop
from wpilib import TimedRobot
from wpilib import Watchdog
from wpilib import DriverStation
from wpilib import RobotState
from wpilib import RobotBase

import hal

from .commandgroup import *
class CommandScheduler:

    _instance: Optional[Self] = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def getInstance() -> "CommandScheduler":
        return CommandScheduler()
    
    @staticmethod
    def resetInstance() -> None:
        CommandScheduler._instance = None
    
    def __init__(self) -> None:
        self._composedCommands: Set[Command] = set()
        self._scheduledCommands: Set[Command] = set()
        self._requirements: Dict[Subsystem, Command] = {}
        self._subsystems: Dict[Subsystem, Optional[Command]] = {}

        self._defaultButtonLoop = EventLoop()
        self._activeButtonLoop = self._defaultButtonLoop

        self._disabled = False

        self._initActions: List[Callable[[Command], None]] = []
        self._executeActions: List[Callable[[Command], None]] = []
        self._interruptActions: List[Callable[[Command], None]] = []
        self._finishActions: List[Callable[[Command], None]] = []

        self._inRunLoop = False
        self._toSchedule: Set[Command] = set()
        self._toCancel: Set[Command] = set()

        self._watchdog = Watchdog(TimedRobot.kDefaultPeriod, lambda: None)

        hal.report(hal.tResourceType.kResourceType_Command.value, hal.tInstances.kCommand2_Scheduler.value)

    def setPeriod(self, period: float) -> None:
        self._watchdog.setTimeout(period)
    
    def getDefaultButtonLoop(self) -> EventLoop:
        return self._defaultButtonLoop
    
    def getActiveButtonLoop(self) -> EventLoop:
        return self._activeButtonLoop
    
    def setActiveButtonLoop(self, loop: EventLoop) -> None:
        self._activeButtonLoop = loop

    def initCommand(self, command: Command, *requirements: Subsystem) -> None:
        self._scheduledCommands.add(command)
        for requirement in requirements:
            self._requirements[requirement] = command
        command.initialize()
        for action in self._initActions:
            action(command)
        # self._watchdog.addEpoch()

    @overload
    def schedule(self, command: Command, /) -> None:
        pass

    @overload
    def schedule(self, *commands: Command) -> None:
        pass

    def schedule(self, *commands) -> None:
        if len(commands) > 1:
            for command in commands:
                self.schedule(command)
            return
        
        command = commands[0]

        if command is None:
            # DriverStation.reportWarning("CommandScheduler tried to schedule a null command!", True)
            return
        
        if self._inRunLoop:
            self._toSchedule.add(command)
            return
        
        if command in getGroupedCommands():
            raise IllegalCommandUse("A command that is part of a CommandGroup cannot be independently scheduled")
        
        if self._disabled:
            return
        
        if RobotState.isDisabled() and not command.runsWhenDisabled():
            return
        
        if self.isScheduled(command):
            return
        
        requirements = command.getRequirements()

        if self._requirements.keys().isdisjoint(requirements):
            self.initCommand(command, *requirements)
        else:
            for requirement in requirements:
                requiringCommand = self.requiring(requirement)
                if requiringCommand is not None and requiringCommand.getInterruptionBehavior() == InterruptionBehavior.kCancelIncoming:
                    return
            
            for requirement in requirements:
                requiringCommand = self.requiring(requirement)
                if requiringCommand is not None:
                    self.cancel(requiringCommand)
            
            self.initCommand(command, *requirements)
        
    def run(self):
        if self._disabled:
            return
        self._watchdog.reset()
    
        for subsystem in self._subsystems:
            subsystem.periodic()
            if RobotBase.isSimulation():
                subsystem.simulationPeriodic()
            # self._watchdog.addEpoch()
        
        loopCache = self._activeButtonLoop
        loopCache.poll()
        self._watchdog.addEpoch("buttons.run()")

        self._inRunLoop = True

        for command in self._scheduledCommands.copy():
            if not command.runsWhenDisabled() and RobotState.isDisabled():
                command.end(True)
                for action in self._interruptActions:
                    action(command)
                for requirement in command.getRequirements():
                    self._requirements.pop(requirement)
                self._scheduledCommands.remove(command)
                continue

            command.execute()
            for action in self._executeActions:
                action(command)
            # self._watchdog.addEpoch()
            if command.isFinished():
                command.end(False)
                for action in self._finishActions:
                    action(command)
                self._scheduledCommands.remove(command)
                for requirement in command.getRequirements():
                    self._requirements.pop(requirement)
        
        self._inRunLoop = False

        for command in self._toSchedule:
            self.schedule(command)
        
        for command in self._toCancel:
            self.cancel(command)
        
        self._toSchedule.clear()
        self._toCancel.clear()

        for subsystem, command in self._subsystems.items():
            if subsystem not in self._requirements and command is not None:
                self.schedule(command)
        
        self._watchdog.disable()
        if self._watchdog.isExpired():
            print("CommandScheduler loop overrun")
            self._watchdog.printEpochs()
                
    def registerSubsystem(self, *subsystems: Subsystem) -> None:
        for subsystem in subsystems:
            if subsystem in self._subsystems:
                # DriverStation.reportWarning("Tried to register an already-registered subsystem", True)
                continue
            self._subsystems[subsystem] = None

    def unregisterSubsystem(self, *subsystems: Subsystem) -> None:
        for subsystem in subsystems:
            self._subsystems.pop(subsystem)

    def setDefaultCommand(self, subsystem: Subsystem, defaultCommand: Command) -> None:
        self.requireNotComposed(defaultCommand)
        if not subsystem in defaultCommand.getRequirements():
            raise IllegalCommandUse("Default commands must require their subsystem!")
        if defaultCommand.getInterruptionBehavior() != InterruptionBehavior.kCancelIncoming:
            # DriverStation.reportWarning("Registering a non-interruptible default command\nThis will likely prevent any other commands from requiring this subsystem.", True)
            pass
        self._subsystems[subsystem] = defaultCommand
    
    def removeDefaultCommand(self, subsystem: Subsystem) -> None:
        self._subsystems[subsystem] = None
    
    def getDefaultCommand(self, subsystem: Subsystem) -> Optional[Command]:
        return self._subsystems[subsystem]
    
    def cancel(self, *commands: Command) -> None:
        if self._inRunLoop:
            self._toCancel.update(commands)
            return
        
        for command in commands:
            if not self.isScheduled(command):
                continue
        
            self._scheduledCommands.remove(command)
            for requirement in command.getRequirements():
                del self._requirements[requirement]
            command.end(True)
            for action in self._interruptActions:
                action(command)
    
    def cancelAll(self) -> None:
        self.cancel(*self._scheduledCommands)
    
    def isScheduled(self, *commands: Command) -> bool:
        return all(command in self._scheduledCommands for command in commands)

    def requiring(self, subsystem: Subsystem) -> Command:
        return self._requirements[subsystem]

    def disable(self) -> None:
        self._disabled = True
    
    def enable(self) -> None:
        self._disabled = False
    
    def onCommandInitialize(self, action: Callable[[Command], None]) -> None:
        self._initActions.append(action)
    
    def onCommandExecute(self, action: Callable[[Command], None]) -> None:
        self._executeActions.append(action)
    
    def onCommandInterrupt(self, action: Callable[[Command], None]) -> None:
        self._interruptActions.append(action)
    
    def onCommandFinish(self, action: Callable[[Command], None]) -> None:
        self._finishActions.append(action)
    
    def registerComposedCommands(self, *commands: Command) -> None:
        self.requireNotComposed(*commands)
        self._composedCommands.update(commands)
    
    def clearComposedCommands(self) -> None:
        self._composedCommands.clear()
    
    def removeComposedCommands(self, *commands: Command) -> None:
        self._composedCommands.difference_update(commands)

    def requireNotComposed(self, *commands: Command) -> None:
        if not self._composedCommands.isdisjoint(commands):
            raise IllegalCommandUse("Commands that have been composed may not be added to another composition or scheduled individually")
    
    def isComposed(self, command: Command) -> bool:
        return command in self.getComposedCommands()

    def getComposedCommands(self) -> Set[Command]:
        return self._composedCommands
