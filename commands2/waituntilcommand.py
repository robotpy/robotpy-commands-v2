from commands2.command import Command, InterruptionBehavior
from .command import Command, InterruptionBehavior
from .commandgroup import *

from typing import Callable, Dict, overload

from wpilib import Timer

class WaitUntilCommand(Command):

    @overload
    def __init__(self, condition: Callable[[], bool]): ...

    @overload
    def __init__(self, time: float): ...

    def __init__(self, *args, **kwargs):
        super().__init__()
        
        if "condition" in kwargs:
            self._condition = kwargs["condition"]
        elif "time" in kwargs:
            self._condition = lambda: Timer.getMatchTime() - kwargs["time"] > 0
        elif len(args) == 1:
            if isinstance(args[0], float):
                self._condition = lambda: Timer.getMatchTime() - args[0] > 0
            else:
                self._condition = args[0]
    
    def isFinished(self) -> bool:
        return self._condition()

    def runsWhenDisabled(self) -> bool:
        return True
