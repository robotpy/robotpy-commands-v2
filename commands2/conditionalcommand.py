from .command import Command
from .commandgroup import *

from typing import Callable

class ConditionalCommand(Command):

    selectedCommand: Command

    def __init__(
        self,
        onTrue: Command,
        onFalse: Command,
        condition: Callable[[], bool]
    ):
        super().__init__()

        requireUngrouped(onTrue, onFalse)
        registerGroupedCommands(onTrue, onFalse)

        self.onTrue = onTrue
        self.onFalse = onFalse
        self.condition = condition

        self.addRequirements(*onTrue.getRequirements())
        self.addRequirements(*onFalse.getRequirements())

    def initialize(self):
        if self.condition():
            self.selectedCommand = self.onTrue
        else:
            self.selectedCommand = self.onFalse

        self.selectedCommand.initialize()

    def execute(self):
        self.selectedCommand.execute()

    def isFinished(self) -> bool:
        return self.selectedCommand.isFinished()
    
    def end(self, interrupted: bool):
        self.selectedCommand.end(interrupted)

    def runsWhenDisabled(self) -> bool:
        return (
            self.onTrue.runsWhenDisabled()
            and self.onFalse.runsWhenDisabled()
        )