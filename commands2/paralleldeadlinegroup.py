from commands2.command import Command, InterruptionBehavior
from .command import Command, InterruptionBehavior
from .commandscheduler import CommandScheduler
from .commandgroup import *

from typing import Callable, Dict

class ParallelDeadlineGroup(CommandGroup):

    def __init__(self, deadline: Command, *commands: Command):
        super().__init__()
        self._commands: Dict[Command, bool] = {}
        self._runsWhenDisabled = True
        self._finished = True
        self._deadline = deadline
        self._interruptBehavior = InterruptionBehavior.kCancelIncoming
        self.addCommands(*commands)
        if deadline not in self._commands:
            self.addCommands(deadline)

    def setDeadline(self, deadline: Command):
        if deadline not in self._commands:
            self.addCommands(deadline)
        self._deadline = deadline

    def addCommands(self, *commands: Command):
        if not self._finished:
            raise IllegalCommandUse(
                "Commands cannot be added to a composition while it is running"
            )
        
        CommandScheduler.getInstance().registerComposedCommands(*commands)

        for command in commands:
            if not command.getRequirements().isdisjoint(self.requirements):
                raise IllegalCommandUse("Multiple comands in a parallel composition cannot require the same subsystems.")
            
            self._commands[command] = False
            self.requirements.update(command.getRequirements())
            self._runsWhenDisabled = self._runsWhenDisabled and command.runsWhenDisabled()

            if command.getInterruptionBehavior() == InterruptionBehavior.kCancelSelf:
                self._interruptBehavior = InterruptionBehavior.kCancelSelf
            
    def initialize(self):
        for command in self._commands:
            command.initialize()
            self._commands[command] = True
        self._finished = False

    def execute(self):
        for command, isRunning in self._commands.items():
            if not isRunning:
                continue
            command.execute()
            if command.isFinished():
                command.end(False)
                self._commands[command] = False
                if command == self._deadline:
                    self._finished = True

    def end(self, interrupted: bool):
        if interrupted:
            for command, isRunning in self._commands.items():
                if not isRunning:
                    continue
                command.end(True)
                self._commands[command] = False

    def isFinished(self) -> bool:
        return self._finished
    
    def runsWhenDisabled(self) -> bool:
        return self._runsWhenDisabled
    
    def getInterruptionBehavior(self) -> InterruptionBehavior:
        return self._interruptBehavior