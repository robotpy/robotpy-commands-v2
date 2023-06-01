from enum import Enum
from typing import Set, Callable, overload, TYPE_CHECKING
from typing_extensions import Self

if TYPE_CHECKING:
    from .subsystem import Subsystem

from .commandscheduler import CommandScheduler

from .wrappercommand import WrapperCommand
from .waitcommand import WaitCommand
from .waituntilcommand import WaitUntilCommand
from .sequentialcommandgroup import SequentialCommandGroup
from .paralleldeadlinegroup import ParallelDeadlineGroup
from .parallelracegroup import ParallelRaceGroup
from .parallelcommandgroup import ParallelCommandGroup
from .notifiercommand import NotifierCommand
from .perpetualcommand import PerpetualCommand
from .instantcommand import InstantCommand
from .functionalcommand import FunctionalCommand
from .repeatcommand import RepeatCommand
from .proxycommand import ProxyCommand
from .conditionalcommand import ConditionalCommand

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
    
    def withTimeout(self, seconds: float) -> "Command":
        return self.raceWith(WaitCommand(seconds))
    
    def until(self, condition: Callable[[], bool]) -> "Command":
        return self.raceWith(WaitUntilCommand(condition))
    
    def onlyWhile(self, condition: Callable[[], bool]) -> "Command":
        return self.until(lambda: not condition())
    
    def withInterrupt(self, condition: Callable[[], bool]) -> "Command":
        return self.until(condition)
    
    def beforeStarting(self, before: "Command") -> "Command":
        return SequentialCommandGroup(before, self)
    
    def andThen(self, *next: "Command") -> "Command":
        return SequentialCommandGroup(self, *next)
    
    def deadlineWith(self, *parallel: "Command") -> "Command":
        return ParallelDeadlineGroup(self, *parallel)
    
    def alongWith(self, *parallel: "Command") -> "Command":
        return ParallelCommandGroup(self, *parallel)
    
    def raceWith(self, *parallel: "Command") -> "Command":
        return ParallelRaceGroup(self, *parallel)
    
    def perpetually(self) -> "Command":
        return PerpetualCommand(self)
    
    def repeatedly(self) -> "Command":
        return RepeatCommand(self)
    
    def asProxy(self) -> "Command":
        return ProxyCommand(self)
    
    def unless(self, condition: Callable[[], bool]) -> "Command":
        return ConditionalCommand(InstantCommand(), self, condition)

    def onlyIf(self, condition: Callable[[], bool]) -> "Command":
        return self.unless(lambda: not condition())
    
    def ignoringDisable(self, doesRunWhenDisabled: bool) -> "Command":
        class W(WrapperCommand):
            def runsWhenDisabled(self) -> bool:
                return doesRunWhenDisabled
        return W(self)
    
    def withInteruptBehavior(self, behavior: InterruptionBehavior) -> "Command":
        class W(WrapperCommand):
            def getInterruptionBehavior(self) -> InterruptionBehavior:
                return behavior
        return W(self)
