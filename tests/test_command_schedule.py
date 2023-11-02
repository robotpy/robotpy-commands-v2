from typing import TYPE_CHECKING

import commands2
from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

from ntcore import NetworkTableInstance
from wpilib import SmartDashboard

import pytest

def test_instantSchedule(scheduler: commands2.CommandScheduler):
    command = commands2.Command()
    command.isFinished = lambda: True
    start_spying_on(command)

    scheduler.schedule(command)
    assert scheduler.isScheduled(command)
    verify(command).initialize()

    scheduler.run()

    verify(command).execute()
    verify(command).end(False)
    assert not scheduler.isScheduled(command)


def test_singleIterationSchedule(scheduler: commands2.CommandScheduler):
    command = commands2.Command()
    start_spying_on(command)

    scheduler.schedule(command)
    assert scheduler.isScheduled(command)

    scheduler.run()
    command.isFinished = lambda: True
    scheduler.run()

    verify(command).initialize()
    verify(command, times(2)).execute()
    verify(command).end(False)
    assert not scheduler.isScheduled(command)


def test_multiSchedule(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command2 = commands2.Command()
    command3 = commands2.Command()

    scheduler.schedule(command1, command2, command3)
    assert scheduler.isScheduled(command1, command2, command3)
    scheduler.run()
    assert scheduler.isScheduled(command1, command2, command3)

    command1.isFinished = lambda: True
    scheduler.run()
    assert scheduler.isScheduled(command2, command3)
    assert not scheduler.isScheduled(command1)

    command2.isFinished = lambda: True
    scheduler.run()
    assert scheduler.isScheduled(command3)
    assert not scheduler.isScheduled(command1, command2)

    command3.isFinished = lambda: True
    scheduler.run()
    assert not scheduler.isScheduled(command1, command2, command3)


def test_schedulerCancel(scheduler: commands2.CommandScheduler):
    command = commands2.Command()
    start_spying_on(command)

    scheduler.schedule(command)

    scheduler.run()
    scheduler.cancel(command)
    scheduler.run()

    verify(command).execute()
    verify(command).end(True)
    verify(command, never()).end(False)

    assert not scheduler.isScheduled(command)


def test_notScheduledCancel(scheduler: commands2.CommandScheduler):
    command = commands2.Command()

    scheduler.cancel(command)


def test_smartDashboardCancelTest(scheduler: commands2.CommandScheduler, nt_instance: NetworkTableInstance):
    SmartDashboard.putData("Scheduler", scheduler)
    SmartDashboard.updateValues()

    command = commands2.Command()
    scheduler.schedule(command)
    scheduler.run()
    SmartDashboard.updateValues()
    assert scheduler.isScheduled(command)

    table = nt_instance.getTable("SmartDashboard")
    table.getEntry("Scheduler/Cancel").setIntegerArray([id(command)])
    SmartDashboard.updateValues()
    scheduler.run()
    assert not scheduler.isScheduled(command)

