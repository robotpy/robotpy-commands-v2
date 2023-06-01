from .commandscheduler import CommandScheduler

from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .command import Command
class Subsystem:

    def __new__(cls, *arg, **kwargs) -> 'Subsystem':
        instance = super().__new__(cls, *arg, **kwargs)
        # add to the scheduler
        CommandScheduler.getInstance().registerSubsystem(instance)
        return instance

    def __init__(self) -> None:
        pass

    def periodic(self) -> None:
        pass

    def simulationPeriodic(self) -> None:
        pass

    def getDefaultCommand(self) -> Optional[Command]:
        return CommandScheduler.getInstance().getDefaultCommand(self)
    
    def setDefaultCommand(self, command: Command) -> None:
        CommandScheduler.getInstance().setDefaultCommand(self, command)

    def getCurrentCommand(self) -> Optional[Command]:
        return CommandScheduler.getInstance().requiring(self)
    
