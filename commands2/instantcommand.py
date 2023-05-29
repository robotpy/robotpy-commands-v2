from .functionalcommand import FunctionalCommand
from .subsystem import Subsystem

from typing import Callable, Optional

class InstantCommand(FunctionalCommand):

    def __init__(
        self,
        toRun: Optional[Callable[[], None]] = None,
        *requirements: Subsystem
    ):
        super().__init__(
            lambda: None,
            toRun or (lambda: None),
            lambda _: None,
            lambda: True,
            *requirements
        )