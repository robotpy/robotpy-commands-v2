from typing import Set
from .command import Command

class IllegalCommandUse(Exception):
    pass

grouped_commands: Set[Command] = set()

# The next 4 functions are just wrappers around a set for cross-language consistency

def registerGroupedCommands(*commands: Command):
    grouped_commands.update(commands)

def clearGroupedCommands():
    grouped_commands.clear()

def clearGroupedCommand(command: Command):
    grouped_commands.remove(command)

def getGroupedCommands() -> Set[Command]:
    return grouped_commands

def requireUngrouped(*requirements: Command):
    bad_requirements = []
    for requirement in requirements:
        if requirement in grouped_commands:
            bad_requirements.append(requirement)

    if bad_requirements:
        raise IllegalCommandUse(
            "Commands cannot be added to more than one CommandGroup."
            f" The following commands are already in a CommandGroup: {bad_requirements}"
        )
    

class CommandGroup(Command):

    def addCommands(self, *commands: Command):
        raise NotImplementedError