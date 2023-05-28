from .command import Command
from .commandgroup import *
from .functionalcommand import FunctionalCommand
from .subsystem import Subsystem

from typing import Callable

class RunCommand(FunctionalCommand):

    def __init__(
        self,
        toRun: Callable[[], None],
        *requirements: Subsystem
    ):
        super().__init__(
            lambda: None,
            toRun,
            lambda interrupted: None,
            lambda: False,
            *requirements
        )