from typing import Callable, Optional, overload, List, Union

from ._impl import Command, Subsystem, _Trigger

from .coroutinecommand import CoroutineCommand, Coroutineable, Coroutine

from wpimath.filter import Debouncer

class Trigger:
    """
    A button that can be pressed or released.
    """

    @overload
    def __init__(self, is_active: Callable[[], bool] = lambda: False) -> None: ...

    @overload
    def __init__(self, is_active: _Trigger) -> None: ...

    def __init__(self, is_active: Union[Callable[[], bool], _Trigger] = lambda: False) -> None:
        if isinstance(is_active, _Trigger):
            self._trigger = is_active
        else:
            self._trigger = _Trigger(is_active)

    def __bool__(self) -> bool:
        return bool(self._trigger)

    def get(self) -> bool:
        return bool(self)

    def __call__(self) -> bool:
        return bool(self)

    def __and__(self, other: "Trigger") -> "Trigger":
        return Trigger(lambda: self() and other())

    def __or__(self, other: "Trigger") -> "Trigger":
        return Trigger(lambda: self() or other())

    def __invert__(self) -> "Trigger":
        return Trigger(lambda: not self())

    def not_(self) -> "Trigger":
        return ~self

    def or_(self, other: "Trigger") -> "Trigger":
        return self | other

    def and_(self, other: "Trigger") -> "Trigger":
        return self & other

    def debounce(self, debounce_time: float, type: Debouncer.DebounceType) -> "Trigger":
        return Trigger(_Trigger.debounce(debounce_time, type))

    def cancelWhenActive(self, command: Command) -> None:
        self._trigger.cancelWhenActive(command)

    @overload
    def whenActive(self, command: Command, /, interruptible: bool = True) -> None:
        ...

    @overload
    def whenActive(
        self,
        coroutine: Union[Coroutine, Coroutineable],
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        ...

    @overload
    def whenActive(
        self,
        coroutine: None,
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        ...

    def whenActive(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]],
        /,
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
    def whenInactive(self, command: Command, /, interruptible: bool = True) -> None:
        ...

    @overload
    def whenInactive(
        self,
        coroutine: Union[Coroutine, Coroutineable],
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        ...

    @overload
    def whenInactive(
        self,
        coroutine: None,
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        ...

    def whenInactive(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]],
        /,
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
    def whileActiveContinous(self, command: Command, /, interruptible: bool = True) -> None:
        ...

    @overload
    def whileActiveContinous(
        self,
        coroutine: Union[Coroutine, Coroutineable],
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        ...

    @overload
    def whileActiveContinous(
        self,
        coroutine: None,
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        ...

    def whileActiveContinous(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]],
        /,
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
    def whileActiveOnce(self, command: Command, /, interruptible: bool = True) -> None:
        ...

    @overload
    def whileActiveOnce(
        self,
        coroutine: Union[Coroutine, Coroutineable],
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        ...

    @overload
    def whileActiveOnce(
        self,
        coroutine: None,
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        ...

    def whileActiveOnce(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]],
        /,
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
    def toggleWhenActive(self, command: Command, /, interruptible: bool = True) -> None:
        ...

    @overload
    def toggleWhenActive(
        self,
        coroutine: Union[Coroutine, Coroutineable],
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> None:
        ...

    @overload
    def toggleWhenActive(
        self,
        coroutine: None,
        /,
        *,
        interruptible: bool = True,
        requirements: Optional[List[Subsystem]] = None,
        runs_when_disabled: bool = False,
    ) -> Callable[[Coroutineable], None]:
        ...

    def toggleWhenActive(
        self,
        command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]],
        /,
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
