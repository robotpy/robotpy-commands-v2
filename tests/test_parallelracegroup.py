import commands2
# from tests.compositiontestbase import T

from typing import TYPE_CHECKING
from util import * # type: ignore
from compositiontestbase import MultiCompositionTestBase # type: ignore
if TYPE_CHECKING:
    from .util import *
    from .compositiontestbase import MultiCompositionTestBase

import pytest

class TestParallelRaceGroupComposition(MultiCompositionTestBase):
    def compose(self, *members: commands2.Command):
        return commands2.ParallelRaceGroup(*members)

def test_parallelRaceSchedule(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)

    group = commands2.ParallelRaceGroup(command1, command2)

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
    assert command2.execute.times_called == 1
    assert command2.end.times_called == 1
    assert command2.end.called_with(interrupted=True)
    assert not command2.end.called_with(interrupted=False)

    assert not scheduler.isScheduled(group)

def test_parallelRaceInterrupt(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)

    group = commands2.ParallelRaceGroup(command1, command2)

    scheduler.schedule(group)

    scheduler.run()
    scheduler.run()
    scheduler.cancel(group)

    assert command1.execute.times_called == 2
    assert not command1.end.called_with(interrupted=False)
    assert command1.end.called_with(interrupted=True)

    assert command2.execute.times_called == 2
    assert not command2.end.called_with(interrupted=False)
    assert command2.end.called_with(interrupted=True)

    assert not scheduler.isScheduled(group)


def test_notScheduledCancel(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    group = commands2.ParallelRaceGroup(command1, command2)

    scheduler.cancel(group)

def test_parallelRaceRequirement(scheduler: commands2.CommandScheduler):
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

    group = commands2.ParallelRaceGroup(command1, command2)

    scheduler.schedule(group)
    scheduler.schedule(command3)

    assert not scheduler.isScheduled(group)
    assert scheduler.isScheduled(command3)

def test_parallelRaceRequirementError():
    system1 = commands2.Subsystem()
    system2 = commands2.Subsystem()
    system3 = commands2.Subsystem()

    command1 = commands2.Command()
    command1.addRequirements(system1, system2)
    command2 = commands2.Command()
    command2.addRequirements(system2, system3)

    with pytest.raises(commands2.IllegalCommandUse):
        commands2.ParallelRaceGroup(command1, command2)


def test_parallelRaceOnlyCallsEndOnce(scheduler: commands2.CommandScheduler):
    system1 = commands2.Subsystem()
    system2 = commands2.Subsystem()

    command1 = commands2.Command()
    command1.addRequirements(system1)
    command2 = commands2.Command()
    command2.addRequirements(system2)
    command3 = commands2.Command()

    group1 = commands2.SequentialCommandGroup(command1, command2)
    group2 = commands2.ParallelRaceGroup(group1, command3)

    scheduler.schedule(group2)
    scheduler.run()
    command1.isFinished = lambda: True
    scheduler.run()
    command2.isFinished = lambda: True
    scheduler.run()
    assert not scheduler.isScheduled(group2)

def test_parallelRaceScheduleTwiceTest(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)

    group = commands2.ParallelRaceGroup(command1, command2)

    scheduler.schedule(group)
    
    assert command1.initialize.times_called == 1
    assert command2.initialize.times_called == 1

    command1.isFinished = lambda: True
    scheduler.run()
    command2.isFinished = lambda: True
    scheduler.run()

    assert command1.execute.times_called == 1
    assert command1.end.times_called_with(interrupted=False) == 1
    assert command2.execute.times_called == 1
    assert command2.end.times_called_with(interrupted=True) == 1
    assert command2.end.times_called_with(interrupted=False) == 0

    assert not scheduler.isScheduled(group)

    command1.isFinished = lambda: False
    command2.isFinished = lambda: False

    scheduler.schedule(group)
    
    assert command1.initialize.times_called == 2
    assert command2.initialize.times_called == 2

    scheduler.run()
    scheduler.run()
    assert scheduler.isScheduled(group)
    command2.isFinished = lambda: True
    scheduler.run()

    assert not scheduler.isScheduled(group)

