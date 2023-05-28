from .command import Command
from .commandgroup import *

from typing import Callable

class ScheduleCommand(Command):

    def __init__(self, *commands: Command):
        super().__init__()
        self.toSchedule = set(commands)
    
    def initialize(self):
        for command in self.toSchedule:
            command.schedule()
    
    def isFinished(self) -> bool:
        return True
    
    def runsWhenDisabled(self) -> bool:
        return True