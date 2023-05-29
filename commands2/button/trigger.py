from typing import Any, Callable, Optional, overload
from typing_extensions import Self
from wpilib.event import EventLoop
from ..command import Command
from ..commandscheduler import CommandScheduler
from types import SimpleNamespace
from wpilib.event import BooleanEvent
from wpimath.filter import Debouncer

class Trigger:

    _loop: EventLoop
    _condition: Callable[[], bool]

    @overload
    def __init__(self, condition: Callable[[], bool] = lambda: False):
        ...

    @overload
    def __init__(self, loop: EventLoop, condition: Callable[[], bool]):
        ...
    
    def __init__(self, *args, **kwargs):
        if len(args) + len(kwargs) == 1:
            self._loop = CommandScheduler().getDefaultButtonLoop()
            if args:
                self._condition = args[0]
            else:
                self._condition = kwargs["condition"]
        else:
            if "loop" in kwargs:
                self._loop = kwargs["loop"]
                got_loop_from_args = False
            else:
                self._loop = args[0]
                got_loop_from_args = True
            
            if "condition" in kwargs:
                self._condition = kwargs["condition"]
            else:
                if got_loop_from_args:
                    self._condition = args[1]
                else:
                    self._condition = args[0]
            
    def onTrue(self, command: Command) -> Self:
        @self._loop.bind
        def _(state=SimpleNamespace(pressed_last=self._condition())):
            pressed = self._condition()
            if not state.pressed_last and pressed:
                command.schedule()
            state.pressed_last = pressed
        return self
    
    def onFalse(self, command: Command) -> Self:
        @self._loop.bind
        def _(state=SimpleNamespace(pressed_last=self._condition())):
            pressed = self._condition()
            if state.pressed_last and not pressed:
                command.schedule()
            state.pressed_last = pressed
        return self
    
    def whileTrue(self, command: Command) -> Self:
        @self._loop.bind
        def _(state=SimpleNamespace(pressed_last=self._condition())):
            pressed = self._condition()
            if not state.pressed_last and pressed:
                command.schedule()
            elif state.pressed_last and not pressed:
                command.cancel()
            state.pressed_last = pressed
        return self
    
    def whileFalse(self, command: Command) -> Self:
        @self._loop.bind
        def _(state=SimpleNamespace(pressed_last=self._condition())):
            pressed = self._condition()
            if state.pressed_last and not pressed:
                command.schedule()
            elif not state.pressed_last and pressed:
                command.cancel()
            state.pressed_last = pressed
        return self
    
    def toggleOnTrue(self, command: Command) -> Self:
        @self._loop.bind
        def _(state=SimpleNamespace(pressed_last=self._condition())):
            pressed = self._condition()
            if not state.pressed_last and pressed:
                if command.isScheduled():
                    command.cancel()
                else:
                    command.schedule()
            state.pressed_last = pressed
        return self
    
    def toggleOnFalse(self, command: Command) -> Self:
        @self._loop.bind
        def _(state=SimpleNamespace(pressed_last=self._condition())):
            pressed = self._condition()
            if state.pressed_last and not pressed:
                if command.isScheduled():
                    command.cancel()
                else:
                    command.schedule()
            state.pressed_last = pressed
        return self
    
    def __call__(self) -> bool:
        return self._condition()
    
    def getAsBoolean(self) -> bool:
        return self._condition()
    
    def __and__(self, other: "Trigger") -> "Trigger":
        return Trigger(lambda: self() and other())
    
    def and_(self, other: "Trigger") -> "Trigger":
        return self & other
    
    def __or__(self, other: "Trigger") -> "Trigger":
        return Trigger(lambda: self() or other())
    
    def or_(self, other: "Trigger") -> "Trigger":
        return self | other
    
    def __invert__(self) -> "Trigger":
        return Trigger(lambda: not self())
    
    def negate(self) -> "Trigger":
        return ~self
    
    def debounce(self, seconds: float, debounce_type: Debouncer.DebounceType = Debouncer.DebounceType.kRising) -> "Trigger":
        debouncer = Debouncer(seconds, debounce_type)
        return Trigger(lambda: debouncer.calculate(self()))