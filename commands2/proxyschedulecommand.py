from .command import Command
from .commandgroup import *

from typing import Callable

class ProxyScheduleCommand(Command):

    def __init__(self, *toSchedule: Command):
        super().__init__()
        self.toSchedule = set(toSchedule)
        self._finished = False
    
    def initialize(self):
        for command in self.toSchedule:
            command.schedule()
    
    def end(self, interrupted: bool):
        if interrupted:
            for command in self.toSchedule:
                command.cancel()
    
    def execute(self):
        self._finished = True
        for command in self.toSchedule:
            self._finished = self._finished and not command.isScheduled()
    
    def isFinished(self) -> bool:
        return self._finished

