from typing import TYPE_CHECKING

import commands2
from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

import pytest

#parameterized on true and false
@pytest.mark.parametrize(
    "interrupted",
    [
        True,
        False,
    ],
)
def test_deferredFunctions(interrupted):
    inner_command = commands2.Command()
    start_spying_on(inner_command)
    command = commands2.DeferredCommand(lambda: inner_command)

    command.initialize()
    verify(inner_command).initialize()

    command.execute()
    verify(inner_command).execute()

    assert not command.isFinished()
    verify(inner_command).isFinished()

    inner_command.isFinished = lambda: True
    assert command.isFinished()
    verify(inner_command, times(2)).isFinished()

    command.end(interrupted)
    verify(inner_command).end(interrupted)

def test_deferredSupplierOnlyCalledDuringInit(scheduler: commands2.CommandScheduler):
    class Supplier:
        def get(self):
            return commands2.cmd.none()
    supplier = Supplier()
    start_spying_on(supplier)

    command = commands2.DeferredCommand(supplier)
    verify(supplier, never()).get()

    scheduler.schedule(command)
    verify(supplier, times(1)).get()
    scheduler.run()

    scheduler.schedule(command)
    verify(supplier, times(2)).get()

def test_deferredRequirements():
    subsystem = commands2.Subsystem()
    command = commands2.DeferredCommand(commands2.cmd.none(), subsystem)

    assert subsystem in command.getRequirements()

def test_deferredNullCommand():
    command = commands2.DeferredCommand(lambda: None)

    command.initialize()
    command.execute()
    command.isFinished()
    command.end(False)
