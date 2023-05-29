from .command import Command
from .commandgroup import *

from typing import Callable, overload, Union

class ProxyCommand(Command):

    _supplier: Callable[[], Command]

    @overload
    def __init__(self, supplier: Callable[[], Command]): ...

    @overload
    def __init__(self, command: Command): ...

    def __init__(self, *args, **kwargs):
        super().__init__()
        
        if "supplier" in kwargs:
            self._supplier = kwargs["supplier"]
        elif "command" in kwargs:
            self._supplier = lambda: kwargs["command"]
        elif len(args) == 1:
            if isinstance(args[0], Command):
                self._supplier = lambda: args[0]
            else:
                self._supplier = args[0]

    def initialize(self):
        self._command = self._supplier()
        self._command.schedule()

    def end(self, interrupted: bool):
        if interrupted and self._command is not None:
            self._command.cancel()
        self._command = None
    
    def execute(self):
        pass

    def isFinished(self) -> bool:
        return self._command is None or not self._command.isScheduled()
    
    def runsWhenDisabled(self) -> bool:
        return True
