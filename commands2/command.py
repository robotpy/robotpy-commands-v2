from abc import abstractmethod
from typing import Generator, Callable, Set, Optional

from .requirement import Requirement, InterruptBehavior


class Command:
    requirements: Set[Requirement] = {}
    runs_when_disabled: bool = False
    interruption_behavior: InterruptBehavior = InterruptBehavior.CANCEL_SELF

    @abstractmethod
    def initialize(self) -> Optional[Generator[None, None, None]]:
        pass

    def end(self, interrupted: bool):
        pass

    @property
    def is_composed(self) -> bool:
        return getattr(self, "_composed", False)

    def mark_composed(self):
        setattr(self, "_composed", True)


def commandify(
        end: Callable[[bool, tuple, dict], None] = (lambda interrupted, *args, **kwargs: None),
        requirements: Set[Requirement] = None,
        runs_when_disabled: bool = False,
        interruption_behavior: InterruptBehavior = InterruptBehavior.CANCEL_SELF
) -> Callable:
    """
    Transform a generator function into a command
    :param end: a callable to be called when the command ends or is interrupted
    :param requirements: the command's requirements
    :param runs_when_disabled: whether the command may run when the robot is disabled
    :param interruption_behavior: whether the command may be interrupted
    """

    def if_you_see_this_you_didnt_call_commandify_correctly(func):
        def inner(*args, **kwargs):
            class DecoratedCommand(Command):
                def __init__(self):
                    self.requirements = requirements if requirements else {
                        arg for arg in args if isinstance(arg, Requirement)
                    }
                    self.runs_when_disabled = runs_when_disabled
                    self.interruption_behavior = interruption_behavior

                def initialize(self) -> Optional[Generator[None, None, None]]:
                    return func(*args, **kwargs)

                def end(self, interrupted: bool):
                    end(interrupted, *args, *kwargs)

            return DecoratedCommand()

        return inner

    return if_you_see_this_you_didnt_call_commandify_correctly
