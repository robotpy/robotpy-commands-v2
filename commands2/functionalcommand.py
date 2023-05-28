from .command import Command
from .commandgroup import *
from .subsystem import Subsystem

from typing import Callable

class FunctionalCommand(Command):

    def __init__(
        self,
        onInit: Callable[[], None],
        onExecute: Callable[[], None],
        onEnd: Callable[[bool], None],
        isFinished: Callable[[], bool],
        *requirements: Subsystem
    ):
        super().__init__()

        self.onInit = onInit
        self.onExecute = onExecute
        self.onEnd = onEnd

        self.addRequirements(*requirements)

    def initialize(self):
        self.onInit()

    def execute(self):
        self.onExecute()

    def end(self, interrupted: bool):
        self.onEnd(interrupted)

    def isFinished(self) -> bool:
        return self.isFinished()