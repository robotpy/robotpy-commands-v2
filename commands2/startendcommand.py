from commands2.command import Command, InterruptionBehavior
from .command import Command, InterruptionBehavior
from .commandgroup import *
from .functionalcommand import FunctionalCommand
from .subsystem import Subsystem

from typing import Callable, Dict

class StartEndCommand(FunctionalCommand):

    def __init__(
        self,
        onInit: Callable[[], None],
        onEnd: Callable[[bool], None],
        *requirements: Subsystem
    ):
        super().__init__(
            onInit,
            lambda: None,
            onEnd,
            lambda: False,
            *requirements
        )

