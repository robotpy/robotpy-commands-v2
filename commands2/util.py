from typing import Callable

from commands2.command import Command
from commands2.requirement import InterruptBehavior, Requirement


class CommandIllegalUse(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

    @staticmethod
    def commands_cant_be_composed_twice() -> 'CommandIllegalUse':
        return CommandIllegalUse("Commands may not be added to two compositions!")

    @staticmethod
    def composed_commands_may_not_be_scheduled_individually() -> 'CommandIllegalUse':
        return CommandIllegalUse(
            "Commands added to a compositions may not be scheduled individually!")


def require_uncomposed(*commands: Command,
                       exception: Callable[[], CommandIllegalUse]) -> tuple[Command]:
    for command in commands:
        if command.is_composed:
            raise exception()
    return commands


def compose(*commands: Command) -> tuple[tuple[Command], set[Requirement], bool, InterruptBehavior]:
    commands = require_uncomposed(*commands,
                                  exception=CommandIllegalUse.commands_cant_be_composed_twice)
    for command in commands:
        command.mark_composed()
    requirements = set.union(*(command.requirements for command in commands))
    runs_when_disabled = False not in {command.runs_when_disabled for command in commands}
    interrupt_behavior: InterruptBehavior = (
        InterruptBehavior.CANCEL_SELF
        if InterruptBehavior.CANCEL_SELF in {command.interruption_behavior for command in commands}
        else InterruptBehavior.CANCEL_INCOMING
    )
    return commands, requirements, runs_when_disabled, interrupt_behavior
