from typing import Callable, Set, Dict, List, Generator, Optional

from commands2 import Requirement, InterruptBehavior
from commands2.Command import commandify, Command


def none() -> Command:
    @commandify(requirements={})
    def none_impl():
        pass

    return none_impl()


def run_once(action: Callable[[], None], requirements: Set[Requirement] = None) -> Command:
    @commandify(requirements=requirements if requirements is not None else {})
    def run_once_impl():
        action()

    return run_once_impl()


def sequence(*commands: Command) -> Command:
    class SequentialCommandGroup(Command):
        def __init__(self):
            self._commands: List[Command] = list(commands)
            self._current_index = -1
            self.requirements: Set[Requirement] = set({})
            self.runs_when_disabled = True
            self.interruption_behavior = InterruptBehavior.CANCEL_INCOMING
            for command in commands:
                self.requirements.update(command.requirements)
                self.runs_when_disabled &= command.runs_when_disabled
                if command.interruption_behavior is InterruptBehavior.CANCEL_SELF:
                    self.interruption_behavior = InterruptBehavior.CANCEL_SELF

        def initialize(self) -> Optional[Generator[None, None, None]]:
            self._current_index = 0
            for command in self._commands:
                gen = command.initialize()
                if gen:
                    yield from gen
                command.end(False)
                self._current_index += 1

        def end(self, interrupted: bool):
            self._commands[self._current_index].end(interrupted)

    return SequentialCommandGroup()
