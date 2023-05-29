from .command import Command
from .commandgroup import *

from typing import Callable

from wpilib import Notifier
from .subsystem import Subsystem

class NotifierCommand(Command):
    
    def __init__(self, toRun: Callable[[], None], period: float, *requirements: Subsystem):
        super().__init__()
        
        self.notifier = Notifier(toRun)
        self.period = period
        self.addRequirements(*requirements)

    def initialize(self):
        self.notifier.startPeriodic(self.period)

    def end(self, interrupted: bool):
        self.notifier.stop()