from commands2.command import Command, InterruptionBehavior
from .commandgroup import *

from typing import Callable, Dict, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .command import Command, InterruptionBehavior

class WrapperCommand(Command):

    def __init__(self, command: Command):
        super().__init__()
        
        requireUngrouped(command)
        registerGroupedCommands(command)
        self._command = command

    def initialize(self):
        self._command.initialize()

    def execute(self):
        self._command.execute()
    
    def end(self, interrupted: bool):
        self._command.end(interrupted)

    def isFinished(self) -> bool:
        return self._command.isFinished()
    
    def getRequirements(self) -> Set:
        return self._command.getRequirements()
    
    def runsWhenDisabled(self) -> bool:
        return self._command.runsWhenDisabled()
    
    def getInterruptionBehavior(self) -> InterruptionBehavior:
        return self._command.getInterruptionBehavior()