from .command import Command
from .commandgroup import *
from .commandscheduler import CommandScheduler

from typing import Callable

class PerpetualCommand(Command):
    
    def __init__(
        self,
        command: Command
    ):
        super().__init__()

        CommandScheduler.getInstance().registerComposedCommands(command)
        self._command = command
        self.addRequirements(*command.getRequirements())

    def initialize(self):
        self._command.initialize()

    def execute(self):
        self._command.execute
    
    def end(self, interrupted: bool):
        self._command.end(interrupted)

    def runsWhenDisabled(self) -> bool:
        return self._command.runsWhenDisabled()