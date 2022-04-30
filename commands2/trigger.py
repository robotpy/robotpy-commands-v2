from typing import Callable, Optional, overload, List, Union

from ._impl import Command, Subsystem, _Trigger

from .coroutinecommand import CoroutineCommand, Coroutineable, Coroutine

from wpimath.filter import Debouncer


class Trigger:
    """
    A class used to bind command scheduling to events.  The
    Trigger class is a base for all command-event-binding classes, and so the
    methods are named fairly abstractly; for purpose-specific wrappers, see
    Button.

    @see Button
    """

    @overload
    def __init__(self, is_active: Callable[[], bool] = lambda: False) -> None:
        """
        Create a new trigger that is active when the given condition is true.

        :param is_active: Whether the trigger is active.

        Create a new trigger that is never active (default constructor) - activity
        can be further determined by subclass code.
        """

    @overload
    def __init__(self, is_active: _Trigger) -> None:
        """
        Create a new trigger from an existing c++ trigger.
        Robot code does not need to use this constructor.

        :param is_active: The c++ trigger to wrap.
        """

    def __init__(
        self, is_active: Union[Callable[[], bool], _Trigger] = lambda: False
    ) -> None:
        if isinstance(is_active, _Trigger):
            self._trigger = is_active
        else:
            self._trigger = _Trigger(is_active)

    def __bool__(self) -> bool:
        """
        Returns whether or not the trigger is currently active
        """
        return bool(self._trigger)

    def get(self) -> bool:
        """
        Returns whether or not the trigger is currently active
        """
        return bool(self)

    def __call__(self) -> bool:
        """
        Returns whether or not the trigger is currently active
        """
        return bool(self)

    def __and__(self, other: "Trigger") -> "Trigger":
        """
        Composes this trigger with another trigger, returning a new trigger that is active when both
        triggers are active.

        :param trigger: the trigger to compose with

        :returns: the trigger that is active when both triggers are active
        """
        return Trigger(lambda: self() and other())

    def __or__(self, other: "Trigger") -> "Trigger":
        """
        Composes this trigger with another trigger, returning a new trigger that is active when either
        triggers are active.

        :param trigger: the trigger to compose with

        :returns: the trigger that is active when both triggers are active
        """
        return Trigger(lambda: self() or other())

    def __invert__(self) -> "Trigger":
        """
        Creates a new trigger that is active when this trigger is inactive, i.e. that acts as the
        negation of this trigger.

        :param trigger: the trigger to compose with

        :returns: the trigger that is active when both triggers are active
        """
        return Trigger(lambda: not self())

    and_ = __and__
    or_ = __or__
    not_ = __invert__

    def debounce(self, debounceTime: float, type: Debouncer.DebounceType) -> "Trigger":
        """
        Creates a new debounced trigger from this trigger - it will become active
        when this trigger has been active for longer than the specified period.

        :param debounceTime: The debounce period.
        :param type:         The debounce type.

        :returns: The debounced trigger.
        """
        return Trigger(self._trigger.debounce(debounceTime, type))

    def cancelWhenActive(self, command: Command) -> None:
        """
        Binds a command to be canceled when the trigger becomes active.  Takes a
        raw pointer, and so is non-owning; users are responsible for the lifespan
        and scheduling of the command.

        :param command: The command to bind.
        """
        self._trigger.cancelWhenActive(command)

    @overload
    def whenActive(
        self, command_or_coroutine: Command, interruptible: bool = True
    ) -> None:
        """
        Binds a command to start when the trigger becomes active.

        :param command:       The command to bind.
        :param interruptible: Whether the command should be interruptible.
        """

    @overload
    def whenActive(
        self,
        command_or_coroutine: Union[Coroutine, Coroutineable],
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        """
        Binds a coroutine to start when the trigger becomes active.

        :param coroutine: The coroutine or coroutine function to bind.
        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    @overload
    def whenActive(
        self,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        """
        Binds a coroutine to start when the trigger becomes active (Decorator Form).
        A def should be under this.

        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    def whenActive(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]] = None,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Union[None, Callable[[Coroutineable], None]]:
        if command_or_coroutine is None:

            def wrapper(coroutine: Coroutineable) -> None:
                self.whenActive(
                    coroutine,
                    interruptible=interruptible,
                    requirements=requirements,
                    runs_when_disabled=runs_when_disabled,
                )

            return wrapper

        if isinstance(command_or_coroutine, Command):
            self._trigger.whenActive(command_or_coroutine, interruptible)
            return

        self._trigger.whenActive(
            CoroutineCommand(command_or_coroutine, requirements, runs_when_disabled),
            interruptible,
        )
        return

    @overload
    def whenInactive(
        self, command_or_coroutine: Command, interruptible: bool = True
    ) -> None:
        """
        Binds a command to start when the trigger becomes inactive.

        :param command:       The command to bind.
        :param interruptible: Whether the command should be interruptible.
        """

    @overload
    def whenInactive(
        self,
        command_or_coroutine: Union[Coroutine, Coroutineable],
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        """
        Binds a coroutine to start when the trigger becomes inactive.

        :param coroutine: The coroutine or coroutine function to bind.
        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    @overload
    def whenInactive(
        self,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        """
        Binds a coroutine to start when the trigger becomes active (Decorator Form).
        A def should be under this.

        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    def whenInactive(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]] = None,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Union[None, Callable[[Coroutineable], None]]:
        if command_or_coroutine is None:

            def wrapper(coroutine: Coroutineable) -> None:
                self.whenInactive(
                    coroutine,
                    interruptible=interruptible,
                    requirements=requirements,
                    runs_when_disabled=runs_when_disabled,
                )

            return wrapper

        if isinstance(command_or_coroutine, Command):
            self._trigger.whenInactive(command_or_coroutine, interruptible)
            return

        self._trigger.whenInactive(
            CoroutineCommand(command_or_coroutine, requirements, runs_when_disabled),
            interruptible,
        )
        return

    @overload
    def whileActiveContinous(
        self, command_or_coroutine: Command, interruptible: bool = True
    ) -> None:
        """
        Binds a command to be started repeatedly while the trigger is active, and
        canceled when it becomes inactive.

        :param command:       The command to bind.
        :param interruptible: Whether the command should be interruptible.
        """

    @overload
    def whileActiveContinous(
        self,
        command_or_coroutine: Union[Coroutine, Coroutineable],
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        """
        Binds a command to be started repeatedly while the trigger is active, and
        canceled when it becomes inactive.

        :param coroutine: The coroutine or coroutine function to bind.
        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    @overload
    def whileActiveContinous(
        self,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        """
        Binds a command to be started repeatedly while the trigger is active, and
        canceled when it becomes inactive (Decorator Form).
        A def should be under this.

        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    def whileActiveContinous(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]] = None,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Union[None, Callable[[Coroutineable], None]]:
        if command_or_coroutine is None:

            def wrapper(coroutine: Coroutineable) -> None:
                self.whileActiveContinous(
                    coroutine,
                    interruptible=interruptible,
                    requirements=requirements,
                    runs_when_disabled=runs_when_disabled,
                )

            return wrapper

        if isinstance(command_or_coroutine, Command):
            self._trigger.whileActiveContinous(command_or_coroutine, interruptible)
            return

        self._trigger.whileActiveContinous(
            CoroutineCommand(command_or_coroutine, requirements, runs_when_disabled),
            interruptible,
        )
        return

    @overload
    def whileActiveOnce(
        self, command_or_coroutine: Command, interruptible: bool = True
    ) -> None:
        """
        Binds a command to be started when the trigger becomes active, and
        canceled when it becomes inactive.

        :param command:       The command to bind.
        :param interruptible: Whether the command should be interruptible.
        """

    @overload
    def whileActiveOnce(
        self,
        command_or_coroutine: Union[Coroutine, Coroutineable],
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        """
        Binds a command to be started when the trigger becomes active, and
        canceled when it becomes inactive.

        :param coroutine: The coroutine or coroutine function to bind.
        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    @overload
    def whileActiveOnce(
        self,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        """
        Binds a command to be started when the trigger becomes active, and
        canceled when it becomes inactive (Decorator Form).
        A def should be under this.

        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    def whileActiveOnce(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]] = None,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Union[None, Callable[[Coroutineable], None]]:
        if command_or_coroutine is None:

            def wrapper(coroutine: Coroutineable) -> None:
                self.whileActiveOnce(
                    coroutine,
                    interruptible=interruptible,
                    requirements=requirements,
                    runs_when_disabled=runs_when_disabled,
                )

            return wrapper

        if isinstance(command_or_coroutine, Command):
            self._trigger.whileActiveOnce(command_or_coroutine, interruptible)
            return

        self._trigger.whileActiveOnce(
            CoroutineCommand(command_or_coroutine, requirements, runs_when_disabled),
            interruptible,
        )
        return

    @overload
    def toggleWhenActive(
        self, command_or_coroutine: Command, interruptible: bool = True
    ) -> None:
        """
        Binds a command to start when the trigger becomes active, and be canceled
        when it again becomes active.

        :param command:       The command to bind.
        :param interruptible: Whether the command should be interruptible.
        """
        ...

    @overload
    def toggleWhenActive(
        self,
        command_or_coroutine: Union[Coroutine, Coroutineable],
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        """
        Binds a command to start when the trigger becomes active, and be canceled
        when it again becomes active.

        :param coroutine: The coroutine or coroutine function to bind.
        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    @overload
    def toggleWhenActive(
        self,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        """
        Binds a command to start when the trigger becomes active, and be canceled
        when it again becomes active (Decorator Form).
        A def should be under this.

        :param interruptible: Whether the command should be interruptible.
        :param requirements: The subsystems required to run the coroutine.
        :param runs_when_disabled: Whether the coroutine should run when the subsystem is disabled.
        """

    def toggleWhenActive(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]] = None,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Union[None, Callable[[Coroutineable], None]]:
        if command_or_coroutine is None:

            def wrapper(coroutine: Coroutineable) -> None:
                self.toggleWhenActive(
                    coroutine,
                    interruptible=interruptible,
                    requirements=requirements,
                    runs_when_disabled=runs_when_disabled,
                )

            return wrapper

        if isinstance(command_or_coroutine, Command):
            self._trigger.toggleWhenActive(command_or_coroutine, interruptible)
            return

        self._trigger.toggleWhenActive(
            CoroutineCommand(command_or_coroutine, requirements, runs_when_disabled),
            interruptible,
        )
        return
