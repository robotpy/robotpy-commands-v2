import commands2
# from tests.compositiontestbase import T

from typing import TYPE_CHECKING
from util import * # type: ignore
from compositiontestbase import MultiCompositionTestBase # type: ignore
if TYPE_CHECKING:
    from .util import *
    from .compositiontestbase import MultiCompositionTestBase

import pytest

class TestParallelDeadlineGroupComposition(MultiCompositionTestBase):
    def compose(self, *members: commands2.Command):
        return commands2.ParallelDeadlineGroup(members[0], *members[1:])

def test_parallelDeadlineSchedule(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()
    command2.isFinished = lambda: True
    command3 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)
    start_spying_on(command3)

    group = commands2.ParallelDeadlineGroup(command1, command2, command3)

    scheduler.schedule(group)
    scheduler.run()

    assert scheduler.isScheduled(group)

    command1.isFinished = lambda: True
    scheduler.run()

    assert not scheduler.isScheduled(group)

    assert command2.initialize.times_called == 1
    assert command2.execute.times_called == 1
    assert command2.end.called_with(interrupted=False)
    assert not command2.end.called_with(interrupted=True)

    assert command1.initialize.times_called == 1
    assert command1.execute.times_called == 2
    assert command1.end.called_with(interrupted=False)
    assert not command1.end.called_with(interrupted=True)

    assert command3.initialize.times_called == 1
    assert command3.execute.times_called == 2

    assert not command3.end.called_with(interrupted=False)
    assert command3.end.called_with(interrupted=True)

def test_parallelDeadlineInterrupt(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()
    command2.isFinished = lambda: True

    start_spying_on(command1)
    start_spying_on(command2)

    group = commands2.ParallelDeadlineGroup(command1, command2)

    scheduler.schedule(group)

    scheduler.run()
    scheduler.run()
    scheduler.cancel(group)

    assert command1.execute.times_called == 2
    assert not command1.end.called_with(interrupted=False)
    assert command1.end.called_with(interrupted=True)

    assert command2.execute.times_called == 1
    assert command2.end.called_with(interrupted=False)
    assert not command2.end.called_with(interrupted=True)

    assert not scheduler.isScheduled(group)

def test_parallelDeadlineRequirement(scheduler: commands2.CommandScheduler):
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

    group = commands2.ParallelDeadlineGroup(command1, command2)

    scheduler.schedule(group)
    scheduler.schedule(command3)

    assert not scheduler.isScheduled(group)
    assert scheduler.isScheduled(command3)

def test_parallelDeadlineRequirementError(scheduler: commands2.CommandScheduler):
    system1 = commands2.Subsystem()
    system2 = commands2.Subsystem()
    system3 = commands2.Subsystem()

    command1 = commands2.Command()
    command1.addRequirements(system1, system2)
    command2 = commands2.Command()
    command2.addRequirements(system2, system3)

    with pytest.raises(commands2.IllegalCommandUse):
        commands2.ParallelDeadlineGroup(command1, command2)
