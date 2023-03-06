from typing import Callable, Generator, Optional, TypeVar, Dict

from commands2.command import Command
from commands2.util import compose
from commands2.cmd import print_cmd


Key = TypeVar("Key")


def select(commands: Dict[Key, Command], selector: Callable[[], Key]) -> Command:
    class SelectCommand(Command):
        def __init__(self):
            self._commands: dict[Key, Command] = commands
            command_tuple: tuple[Command]
            (command_tuple,
             self.requirements,
             self.runs_when_disabled,
             self.interruption_behavior
             ) = compose(*commands.values())
            self._selected: Optional[Command] = None

        def initialize(self) -> Optional[Generator[None, None, None]]:
            self._selected = commands.get(selector(), print_cmd(
                "SelectCommand selector value does not correspond to any command!"))
            return self._selected.initialize()

        def end(self, interrupted: bool):
            self._selected.end(interrupted)

    return SelectCommand()


def either(command_on_true: Command,
           command_on_false: Command,
           selector: Callable[[], bool]) -> Command:
    return select({
        True: command_on_true,
        False: command_on_false
    }, selector=selector)
