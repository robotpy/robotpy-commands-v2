from typing import Dict, Generator

import hal
from wpilib import Watchdog, TimedRobot
from wpilib.event import EventLoop

from commands2.command import Command
from commands2.requirement import Requirement
from commands2.util import CommandIllegalUse, require_uncomposed


class CommandScheduler:
    def __init__(self):
        hal.report(hal.tResourceType.kResourceType_Command, hal.tInstances.kCommand2_Scheduler)
        self._watchdog = Watchdog(TimedRobot.kDefaultPeriod,
                                  lambda: print("CommandScheduler loop time overrun."))

        self._default_button_loop = EventLoop()
        self._active_button_loop = self._default_button_loop
        self._scheduled_commands: Dict[Command, Generator[None, None, None]] = {}
        self._requirements: Dict[Requirement, Command] = {}

    def run(self) -> None:
        to_remove = []
        for (command, generator) in self._scheduled_commands.items():
            try:
                generator.__next__()
            except StopIteration:
                command.end(False)
                to_remove.append(command)

        for command in to_remove:
            self._scheduled_commands.pop(command)
            for req in command.requirements:
                self._requirements.pop(req)

    def schedule(self, command: Command):

        if command in self._scheduled_commands:
            return

        require_uncomposed(command,
                           exception=CommandIllegalUse.
                           composed_commands_may_not_be_scheduled_individually)

        # Find intersect with occupied requirements
        intersect = []
        for requirement in command.requirements:
            if requirement in self._requirements:
                intersect.append(requirement)

        # Try requiring them
        gens = []
        for req in intersect:
            gen = req.require()
            if not gen:
                # Requirement already held by uninterruptible command
                return
            gens.append(gen)

        # Interrupt all commands
        for req in intersect:
            interrupted_command = self._requirements.pop(req)
            interrupted_command.end(True)
            self._scheduled_commands.pop(interrupted_command)

        # Require them
        for req in gens:
            req.send(command.interruption_behavior.value)

        for req in command.requirements:
            self._requirements[req] = command

        # Run first iteration
        generator = command.initialize()
        self._scheduled_commands[command] = generator
        # TODO: do we want to accept non-generator functions as commands?
        if generator is None or next(generator, StopIteration) is StopIteration:
            command.end(False)
            self._scheduled_commands.pop(command)
            for req in command.requirements:
                self._requirements.pop(req)

    def is_scheduled(self, command: Command):
        return command in self._scheduled_commands

    def cancel(self, command: Command):
        if not self.is_scheduled(command):
            return

        command.end(True)
        self._scheduled_commands.pop(command)
        for req in command.requirements:
            self._requirements.pop(req)

    def enable(self):
        pass

    def disable(self):
        pass

    def cancel_all(self):
        pass

    @property
    def active_button_loop(self):
        return self._active_button_loop

    @active_button_loop.setter
    def active_button_loop(self, loop: EventLoop):
        self._active_button_loop = loop
