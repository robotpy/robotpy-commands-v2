from functools import wraps
from typing import Any, Callable, Generator, List, Union, Optional, overload
from ._impl import CommandBase, Subsystem
import inspect
from typing_extensions import TypeGuard

Coroutine = Generator[None, None, None]
CoroutineFunction = Callable[[], Generator[None, None, None]]
Coroutineable = Union[Callable[[], None], CoroutineFunction]


def is_coroutine(func: Any) -> TypeGuard[Coroutine]:
    return inspect.isgenerator(func)


def is_coroutine_function(func: Any) -> TypeGuard[CoroutineFunction]:
    return inspect.isgeneratorfunction(func)


def is_coroutineable(func: Any) -> TypeGuard[Coroutineable]:
    return is_coroutine_function(func) or callable(func)


def ensure_generator_function(func: Coroutineable) -> Callable[..., Coroutine]:
    if is_coroutine_function(func):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        yield

    return wrapper


class CoroutineCommand(CommandBase):
    """
    A class that wraps a coroutine function into a command.
    """

    coroutine: Optional[Coroutine]
    coroutine_function: Optional[Coroutineable]
    is_finished: bool

    def __init__(
        self,
        coroutine: Union[Coroutine, Coroutineable],
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        """
        Creates a CoroutineCommand than can be used as a command.

        :param coroutine: The coroutine or coroutine function to bind.
        :param requirements: The subsystems that this command requires.
        :param runs_when_disabled: Whether or not this command runs when the robot is disabled.
        """
        self.coroutine = None
        self.coroutine_function = None
        self.runsWhenDisabled = lambda: runs_when_disabled

        if is_coroutine(coroutine):
            self.coroutine = coroutine
        elif is_coroutineable(coroutine):
            self.coroutine_function = coroutine
        else:
            raise TypeError("The coroutine must be a coroutine or a coroutine function")

        if requirements is not None:
            self.addRequirements(requirements)

        self.is_finished = False

    def initialize(self) -> None:
        if self.coroutine_function:
            self.coroutine = ensure_generator_function(self.coroutine_function)()
        elif self.coroutine and self.is_finished:
            raise RuntimeError("Generator objects cannot be reused.")

        self.is_finished = False

    def execute(self):
        try:
            if not self.is_finished:
                if not self.coroutine:
                    raise TypeError("This command was not properly initialized")
                next(self.coroutine)
        except StopIteration:
            self.is_finished = True

    def isFinished(self):
        return self.is_finished


@overload
def commandify(
    *, requirements: Optional[List[Subsystem]] = None, runs_when_disabled: bool = False
) -> Callable[[Coroutineable], Callable[..., CoroutineCommand]]:
    """
    A decorator that turns a coroutine function into a command.
    A def should be under this.

    :param requirements: The subsystems that this command requires.
    :param runs_when_disabled: Whether or not this command runs when the robot is disabled.
    """


@overload
def commandify(coroutine: Coroutineable, /) -> Callable[..., CoroutineCommand]:
    """
    A decorator that turns a coroutine function into a command.
    A def should be under this.
    """


def commandify(
    coroutine: Optional[Coroutineable] = None,
    /,
    *,
    requirements: Optional[List[Subsystem]] = None,
    runs_when_disabled: bool = False,
) -> Union[
    Callable[[Coroutineable], Callable[..., CoroutineCommand]],
    Callable[..., CoroutineCommand],
]:
    def wrapper(func: Coroutineable) -> Callable[..., CoroutineCommand]:
        @wraps(func)
        def arg_accepter(*args, **kwargs) -> CoroutineCommand:
            return CoroutineCommand(
                lambda: ensure_generator_function(func)(*args, **kwargs),
                requirements,
            )

        return arg_accepter

    if coroutine is None:
        return wrapper

    return wrapper(coroutine)
