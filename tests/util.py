from typing import Any
import commands2
from wpilib.simulation import DriverStationSim, pauseTiming, resumeTiming, stepTiming

# from unittest.mock import MagicMock


class ManualSimTime:
    def __enter__(self) -> "ManualSimTime":
        pauseTiming()
        return self

    def __exit__(self, *args):
        resumeTiming()

    def step(self, delta: float):
        stepTiming(delta)


# class CommandTestHelper:
#     def __init__(self) -> None:
#         self.scheduler = commands2.CommandScheduler.getInstance()

#     def __enter__(self):
#         commands2.CommandScheduler.resetInstance()
#         DriverStationSim.setEnabled(True)
#         return self

#     def __exit__(self, *args):
#         pass


# class Counter:
#     def __init__(self) -> None:
#         self.value = 0

#     def increment(self):
#         self.value += 1


# class ConditionHolder:
#     def __init__(self, cond: bool = False) -> None:
#         self.cond = cond

#     def getCondition(self) -> bool:
#         return self.cond

#     def setTrue(self):
#         self.cond = True


# class TestSubsystem(commands2.Subsystem):
#     pass


class OOInteger:
    def __init__(self, value: int = 0) -> None:
        self.value = value

    def get(self) -> int:
        return self.value

    def set(self, value: int):
        self.value = value

    def incrementAndGet(self) -> int:
        self.value += 1
        return self.value
    
    def addAndGet(self, value: int) -> int:
        self.value += value
        return self.value

    def __eq__(self, value: float) -> bool:
        return self.value == value
    
    def __lt__(self, value: float) -> bool:
        return self.value < value
    
    def __call__(self) -> int:
        return self.value
    
class OOBoolean:
    def __init__(self, value: bool = False) -> None:
        self.value = value

    def get(self) -> bool:
        return self.value

    def set(self, value: bool):
        self.value = value

    def __eq__(self, value: object) -> bool:
        return self.value == value

    def __bool__(self) -> bool:
        return self.value
    
    def __call__(self) -> bool:
        return self.value
    

class InternalButton(commands2.button.Trigger):
    def __init__(self):
        super().__init__(self.isPressed)
        self.pressed = False

    def isPressed(self) -> bool:
        return self.pressed

    def setPressed(self, value: bool):
        self.pressed = value

def asNone(*args, **kwargs):
    return None

class MethodWrapper:
    def __init__(self, method):
        self.method = method
        self.times_called = 0
        self._call_log = []
    
    def __call__(self, *args, **kwargs):
        self.times_called += 1
        import inspect
        method_args = inspect.getcallargs(self.method, *args, **kwargs)
        
        method_arg_names = list(inspect.signature(self.method).parameters.keys())

        for idx, arg in enumerate(args):
            method_args[method_arg_names[idx]] = arg

        del method_args["self"]

        self._call_log.append(method_args)

        return self.method(*args, **kwargs)
    
    def called_with(self, **kwargs):
        return kwargs in self._call_log

def mock_object(obj: Any) -> None:
    """
    Mocks all methods on an object, so that that call info can be used in asserts.
    
    Example:
    obj = SomeClass()
    mock_object(obj)
    obj.method.times_called == 2
    obj.method.called_with(arg1=1, arg2=2)
    """
    for name in dir(obj):
        value = getattr(obj, name)
        if callable(value) and not name.startswith("_"):
            setattr(obj, name, MethodWrapper(value))
