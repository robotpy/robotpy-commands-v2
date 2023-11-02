from typing import TYPE_CHECKING

import commands2
from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

from ntcore import NetworkTableInstance
from wpilib import SmartDashboard

import pytest


def test_trueAndNotScheduledSchedules(
    scheduler: commands2.CommandScheduler, nt_instance: NetworkTableInstance
):
    schedule = OOInteger(0)
    cancel = OOInteger(0)

    command = commands2.cmd.startEnd(schedule.incrementAndGet, cancel.incrementAndGet)
    publish = nt_instance.getBooleanTopic("/SmartDashboard/command/running").publish()
    SmartDashboard.putData("command", command)
    SmartDashboard.updateValues()
    #
    commands2.CommandScheduler.getInstance().run()
    SmartDashboard.updateValues()
    assert not command.isScheduled()
    assert schedule == 0
    assert cancel == 0

    publish.set(True)
    SmartDashboard.updateValues()
    commands2.CommandScheduler.getInstance().run()
    assert command.isScheduled()
    assert schedule == 1
    assert cancel == 0


def test_trueAndScheduleNoOp(
    scheduler: commands2.CommandScheduler, nt_instance: NetworkTableInstance
):
    schedule = OOInteger(0)
    cancel = OOInteger(0)

    command = commands2.cmd.startEnd(schedule.incrementAndGet, cancel.incrementAndGet)
    publish = nt_instance.getBooleanTopic("/SmartDashboard/command/running").publish()
    SmartDashboard.putData("command", command)
    SmartDashboard.updateValues()
    #
    command.schedule()
    commands2.CommandScheduler.getInstance().run()
    SmartDashboard.updateValues()
    assert command.isScheduled()
    assert schedule == 1
    assert cancel == 0

    publish.set(True)
    SmartDashboard.updateValues()
    commands2.CommandScheduler.getInstance().run()
    assert command.isScheduled()
    assert schedule == 1
    assert cancel == 0


def test_falseAndNotScheduledNoOp(
    scheduler: commands2.CommandScheduler, nt_instance: NetworkTableInstance
):
    schedule = OOInteger(0)
    cancel = OOInteger(0)

    command = commands2.cmd.startEnd(schedule.incrementAndGet, cancel.incrementAndGet)
    publish = nt_instance.getBooleanTopic("/SmartDashboard/command/running").publish()
    SmartDashboard.putData("command", command)
    SmartDashboard.updateValues()
    #
    commands2.CommandScheduler.getInstance().run()
    SmartDashboard.updateValues()
    assert not command.isScheduled()
    assert schedule == 0
    assert cancel == 0

    publish.set(False)
    SmartDashboard.updateValues()
    commands2.CommandScheduler.getInstance().run()
    assert not command.isScheduled()
    assert schedule == 0
    assert cancel == 0


def test_falseAndScheduleCancel(
    scheduler: commands2.CommandScheduler, nt_instance: NetworkTableInstance
):
    schedule = OOInteger(0)
    cancel = OOInteger(0)

    command = commands2.cmd.startEnd(schedule.incrementAndGet, cancel.incrementAndGet)
    publish = nt_instance.getBooleanTopic("/SmartDashboard/command/running").publish()
    SmartDashboard.putData("command", command)
    SmartDashboard.updateValues()
    #
    command.schedule()
    commands2.CommandScheduler.getInstance().run()
    SmartDashboard.updateValues()
    assert command.isScheduled()
    assert schedule == 1
    assert cancel == 0

    publish.set(False)
    SmartDashboard.updateValues()
    commands2.CommandScheduler.getInstance().run()
    assert not command.isScheduled()
    assert schedule == 1
    assert cancel == 1
