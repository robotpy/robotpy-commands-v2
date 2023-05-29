from commands2.command import Command, InterruptionBehavior
from .command import Command, InterruptionBehavior
from .commandgroup import *
from .commandscheduler import CommandScheduler

from typing import Callable, Dict, List

class SequentialCommandGroup(CommandGroup):

    def __init__(self, *commands: Command):
        super().__init__()
        self._commands: List[Command] = []
        self._runsWhenDisabled = True
        self._interruptBehavior = InterruptionBehavior.kCancelIncoming
        self._currentCommandIndex = -1
        self.addCommands(*commands)
    
    def addCommands(self, *commands: Command):
        if self._currentCommandIndex != -1:
            raise IllegalCommandUse(
                "Commands cannot be added to a composition while it is running"
            )
        
        CommandScheduler.getInstance().registerComposedCommands(*commands)

        for command in commands:
            self._commands.append(command)
            self.requirements.update(command.getRequirements())
            self._runsWhenDisabled = self._runsWhenDisabled and command.runsWhenDisabled()
            if command.getInterruptionBehavior() == InterruptionBehavior.kCancelSelf:
                self._interruptBehavior = InterruptionBehavior.kCancelSelf
    
    def initialize(self):
        self._currentCommandIndex = 0
        if self._commands:
            self._commands[0].initialize()
    
    def execute(self):
        if not self._commands:
            return
        
        currentCommand = self._commands[self._currentCommandIndex]

        currentCommand.execute()
        if currentCommand.isFinished():
            currentCommand.end(False)
            self._currentCommandIndex += 1
            if self._currentCommandIndex < len(self._commands):
                self._commands[self._currentCommandIndex].initialize()
        
    def end(self, interrupted: bool):
        self._currentCommandIndex = -1

        if not interrupted: return
        if not self._commands: return
        if not self._currentCommandIndex > -1: return
        if not self._currentCommandIndex < len(self._commands): return

        self._commands[self._currentCommandIndex].end(True)