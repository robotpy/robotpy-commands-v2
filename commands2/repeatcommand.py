from commands2.command import InterruptionBehavior
from .command import Command
from .commandgroup import *

from typing import Callable

class RepeatCommand(Command):
    
    def __init__(
        self,
        command: Command
    ):
        super().__init__()
        self._command = command

    def initialize(self):
        self._ended = False
        self._command.initialize()

    def execute(self):
        if self._ended:
            self._ended = False
            self._command.initialize()
        
        self._command.execute()

        if self._command.isFinished():
            self._command.end(False)
            self._ended = True

    def isFinished(self) -> bool:
        return False
    
    def end(self, interrupted: bool):
        if not self._ended:
            self._command.end(interrupted)
            self._ended = True
    
    def runsWhenDisabled(self) -> bool:
        return self._command.runsWhenDisabled()
    
    def getInterruptionBehavior(self) -> InterruptionBehavior:
        return self._command.getInterruptionBehavior()