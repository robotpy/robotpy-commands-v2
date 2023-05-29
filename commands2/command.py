from enum import Enum
from typing import Set
from typing_extensions import Self

from .subsystem import Subsystem
from .commandscheduler import CommandScheduler

class InterruptionBehavior(Enum):
    kCancelIncoming = 0
    kCancelSelf = 1

class Command:

    requirements: Set[Subsystem]

    def __new__(cls, *args, **kwargs) -> Self:
        instance = super().__new__(cls, *args, **kwargs)
        instance.requirements = set()
        return instance

    def __init__(self):
        pass

    def initialize(self):
        pass

    def execute(self):
        pass

    def isFinished(self) -> bool:
        return False

    def end(self, interrupted: bool):
        pass

    def getRequirements(self) -> Set[Subsystem]:
        return self.requirements
    
    def addRequirements(self, *requirements: Subsystem):
        self.requirements.update(requirements)

    def runsWhenDisabled(self) -> bool:
        return False
    
    def schedule(self, interruptible: bool = True) -> None:
        CommandScheduler.getInstance().schedule(self)

    def cancel(self) -> None:
        CommandScheduler.getInstance().cancel(self)

    def isScheduled(self) -> bool:
        return CommandScheduler.getInstance().isScheduled(self)
    
    def hasRequirement(self, requirement: Subsystem) -> bool:
        return requirement in self.requirements
    
    def getInterruptionBehavior(self) -> InterruptionBehavior:
        return InterruptionBehavior.kCancelSelf
    
