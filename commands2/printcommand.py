from .instantcommand import InstantCommand

from typing import Callable

class PrintCommand(InstantCommand):

    def __init__(self, message: str):
        super().__init__(lambda: print(message))

    def runsWhenDisabled(self) -> bool:
        return True
