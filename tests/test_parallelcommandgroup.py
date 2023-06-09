import commands2
# from tests.compositiontestbase import T

from typing import TYPE_CHECKING
from util import * # type: ignore
from compositiontestbase import MultiCompositionTestBase # type: ignore
if TYPE_CHECKING:
    from .util import *
    from .compositiontestbase import MultiCompositionTestBase

import pytest

class TestParallelCommandGroupComposition(MultiCompositionTestBase):
    def compose(self, *members: commands2.Command):
        return commands2.ParallelCommandGroup(*members)
    
def test_parallelGroupSchedule(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)

    group = commands2.ParallelCommandGroup(command1, command2)

    scheduler.schedule(group)

    assert command1.initialize.times_called == 1
    assert command2.initialize.times_called == 1

    command1.isFinished = lambda: True
    scheduler.run()
    command2.isFinished = lambda: True
    scheduler.run()

    assert command1.execute.times_called == 1
    assert command1.end.times_called == 1
    assert command1.end.called_with(interrupted=False)
    assert command2.execute.times_called == 2
    assert command2.end.times_called == 1
    assert command2.end.called_with(interrupted=False)

    assert not scheduler.isScheduled(group)


def test_parallelGroupInterrupt(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)

    group = commands2.ParallelCommandGroup(command1, command2)

    scheduler.schedule(group)

    command1.isFinished = lambda: True
    scheduler.run()
    scheduler.run()
    scheduler.cancel(group)

    assert command1.execute.times_called == 1
    assert command1.end.called_with(interrupted=False)
    assert not command1.end.called_with(interrupted=True)

    assert command2.execute.times_called == 2
    assert not command2.end.called_with(interrupted=False)
    assert command2.end.called_with(interrupted=True)

    assert not scheduler.isScheduled(group)


def test_notScheduledCancel(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    group = commands2.ParallelCommandGroup(command1, command2)

    scheduler.cancel(group)


def test_parallelGroupRequirement(scheduler: commands2.CommandScheduler):
    system1 = commands2.Subsystem()
    system2 = commands2.Subsystem()
    system3 = commands2.Subsystem()
    system4 = commands2.Subsystem()

    command1 = commands2.Command()
    command1.addRequirements(system1, system2)
    command2 = commands2.Command()
    command2.addRequirements(system3)
    command3 = commands2.Command()
    command3.addRequirements(system3, system4)

    group = commands2.ParallelCommandGroup(command1, command2)

    scheduler.schedule(group)
    scheduler.schedule(command3)

    assert not scheduler.isScheduled(group)
    assert scheduler.isScheduled(command3)

def test_parallelGroupRequirementError():
    system1 = commands2.Subsystem()
    system2 = commands2.Subsystem()
    system3 = commands2.Subsystem()

    command1 = commands2.Command()
    command1.addRequirements(system1, system2)
    command2 = commands2.Command()
    command2.addRequirements(system2, system3)

    with pytest.raises(commands2.IllegalCommandUse):
        commands2.ParallelCommandGroup(command1, command2)




