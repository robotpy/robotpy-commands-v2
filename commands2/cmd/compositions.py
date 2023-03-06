from typing import Generator, Optional

from commands2.command import Command
from commands2.util import compose


def sequence(*commands: Command) -> Command:
    class SequentialCommandGroup(Command):
        def __init__(self):
            (self._commands,
             self.requirements,
             self.runs_when_disabled,
             self.interruption_behavior
             ) = compose(*commands)
            self._commands = list(self._commands)
            self._current_index = -1

        def initialize(self) -> Optional[Generator[None, None, None]]:
            self._current_index = 0
            for command in self._commands:
                print(self._current_index)
                gen = command.initialize()
                if gen:
                    yield from gen
                command.end(False)
                self._current_index += 1

            self._current_index = -1

        def end(self, interrupted: bool):
            print(len(self._commands), self._current_index)
            if self._current_index != -1:
                self._commands[self._current_index].end(interrupted)

    return SequentialCommandGroup()


def parallel(*commands: Command) -> Command:
    class ParallelCommandGroup(Command):
        _commands: dict[Command, Optional[Generator[None, None, None]]]

        def __init__(self):
            (self._commands,
             self.requirements,
             self.runs_when_disabled,
             self.interruption_behavior
             ) = compose(*commands)
            self._commands = {command: None for command in self._commands}

        def initialize(self) -> Optional[Generator[None, None, None]]:
            self._commands = {command: command.initialize() for command in self._commands}
            for (command, generator) in self._commands.items():
                if not generator:
                    command.end(False)
            running: bool = True
            while running:
                running = False
                for (command, generator) in self._commands.items():
                    if generator:
                        running = True
                        if next(generator, StopIteration) is StopIteration:
                            command.end(False)
                            self._commands[command] = None
                yield

        def end(self, interrupted: bool):
            for (command, generator) in self._commands.items():
                if generator:
                    command.end(interrupted)

    return ParallelCommandGroup()


def race(*commands: Command) -> Command:
    class ParallelRaceGroup(Command):
        _commands: dict[Command, Optional[Generator[None, None, None]]]

        def __init__(self):
            (self._commands,
             self.requirements,
             self.runs_when_disabled,
             self.interruption_behavior
             ) = compose(*commands)
            self._commands = {command: None for command in self._commands}

        def initialize(self) -> Optional[Generator[None, None, None]]:
            self._commands = {command: command.initialize() for command in self._commands}
            while True:
                for (command, generator) in self._commands.items():
                    if generator is None or next(generator, StopIteration) is StopIteration:
                        self._commands[command] = None
                        command.end(False)
                        return
                yield

        def end(self, interrupted: bool):
            for (command, generator) in self._commands.items():
                command.end(generator is not None)

    return ParallelRaceGroup()
