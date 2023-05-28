from commands2.command import Command, InterruptionBehavior
from .command import Command, InterruptionBehavior
from .commandgroup import *

from typing import Callable, Dict

from wpilib import Timer

class WaitCommand(Command):

    def __init__(self, seconds: float):
        super().__init__()
        self._duration = seconds
        self._timer = Timer()
    
    def initialize(self):
        self._timer.reset()
        self._timer.start()
    
    def end(self, interrupted: bool):
        self._timer.stop()
    
    def isFinished(self) -> bool:
        return self._timer.hasElapsed(self._duration)
    
    def runsWhenDisabled(self) -> bool:
        return True