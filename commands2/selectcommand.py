from commands2.command import InterruptionBehavior
from .command import Command, InterruptionBehavior
from .commandgroup import *
from .printcommand import PrintCommand
from .commandscheduler import CommandScheduler

from typing import Callable, overload, Dict, Any, Hashable

class SelectCommand(Command):

    def __init__(
        self,
        selector: Callable[[], Hashable],
        commands: Dict[Hashable, Command],
    ):
        super().__init__()

        self._commands = commands
        self._selector = selector

        CommandScheduler.getInstance().registerComposedCommands(*commands.values())

        self._runsWhenDisabled = True
        self._interruptBehavior = InterruptionBehavior.kCancelIncoming
        for command in commands.values():
            self.addRequirements(*command.getRequirements())
            self._runsWhenDisabled = self._runsWhenDisabled and command.runsWhenDisabled()
            if command.getInterruptionBehavior() == InterruptionBehavior.kCancelSelf:
                self._interruptBehavior = InterruptionBehavior.kCancelSelf

    def initialize(self):
        if self._selector() not in self._commands:
            self._selectedCommand = PrintCommand("SelectCommand selector value does not correspond to any command!")
            return
        self._selectedCommand = self._commands[self._selector()]
        self._selectedCommand.initialize()

    def execute(self):
        self._selectedCommand.execute()
    
    def end(self, interrupted: bool):
        self._selectedCommand.end(interrupted)
    
    def isFinished(self) -> bool:
        return self._selectedCommand.isFinished()
    
    def runsWhenDisabled(self) -> bool:
        return self._runsWhenDisabled
    
    def getInterruptionBehavior(self) -> InterruptionBehavior:
        return self._interruptBehavior