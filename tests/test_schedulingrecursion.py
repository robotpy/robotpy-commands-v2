from typing import TYPE_CHECKING

import commands2
from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

import pytest


@pytest.mark.parametrize(
    "interruptionBehavior",
    [
        commands2.InterruptionBehavior.kCancelIncoming,
        commands2.InterruptionBehavior.kCancelSelf,
    ],
)
def test_cancelFromInitialize(
    interruptionBehavior: commands2.InterruptionBehavior,
    scheduler: commands2.CommandScheduler,
):
    hasOtherRun = OOBoolean()
    requirement = commands2.Subsystem()

    selfCancels = commands2.Command()
    start_spying_on(selfCancels)
    selfCancels.addRequirements(requirement)
    selfCancels.getInterruptionBehavior = lambda: interruptionBehavior
    selfCancels.initialize = lambda: scheduler.cancel(selfCancels)

    other = commands2.RunCommand(lambda: hasOtherRun.set(True), requirement)

    scheduler.schedule(selfCancels)
    scheduler.run()
    scheduler.schedule(other)

    assert not scheduler.isScheduled(selfCancels)
    assert scheduler.isScheduled(other)
    assert selfCancels.end.times_called == 1
    scheduler.run()
    assert hasOtherRun == True


@pytest.mark.parametrize(
    "interruptionBehavior",
    [
        commands2.InterruptionBehavior.kCancelIncoming,
        commands2.InterruptionBehavior.kCancelSelf,
    ],
)
def test_cancelFromInitializeAction(
    interruptionBehavior: commands2.InterruptionBehavior,
    scheduler: commands2.CommandScheduler,
):
    hasOtherRun = OOBoolean()
    requirement = commands2.Subsystem()

    selfCancels = commands2.Command()
    start_spying_on(selfCancels)
    selfCancels.addRequirements(requirement)
    selfCancels.getInterruptionBehavior = lambda: interruptionBehavior

    other = commands2.RunCommand(lambda: hasOtherRun.set(True), requirement)

    scheduler.onCommandInitialize(lambda _: scheduler.cancel(selfCancels))
    scheduler.schedule(selfCancels)
    scheduler.run()
    scheduler.schedule(other)

    assert not scheduler.isScheduled(selfCancels)
    assert scheduler.isScheduled(other)
    assert selfCancels.end.times_called == 1
    scheduler.run()
    assert hasOtherRun == True


@pytest.mark.parametrize(
    "interruptionBehavior",
    [
        commands2.InterruptionBehavior.kCancelIncoming,
        commands2.InterruptionBehavior.kCancelSelf,
    ],
)
def test_defaultCommandGetsRescheduledAfterSelfCanceling(
    interruptionBehavior: commands2.InterruptionBehavior,
    scheduler: commands2.CommandScheduler,
):
    hasOtherRun = OOBoolean()
    requirement = commands2.Subsystem()

    selfCancels = commands2.Command()
    start_spying_on(selfCancels)
    selfCancels.addRequirements(requirement)
    selfCancels.getInterruptionBehavior = lambda: interruptionBehavior
    selfCancels.initialize = lambda: scheduler.cancel(selfCancels)

    other = commands2.RunCommand(lambda: hasOtherRun.set(True), requirement)
    scheduler.setDefaultCommand(requirement, other)

    scheduler.schedule(selfCancels)
    scheduler.run()

    scheduler.run()
    assert not scheduler.isScheduled(selfCancels)
    assert scheduler.isScheduled(other)
    assert selfCancels.end.times_called == 1
    scheduler.run()
    assert hasOtherRun == True


def test_cancelFromEnd(scheduler: commands2.CommandScheduler):
    selfCancels = commands2.Command()
    start_spying_on(selfCancels)

    selfCancels.end = lambda interrupted: scheduler.cancel(selfCancels)

    scheduler.schedule(selfCancels)

    scheduler.cancel(selfCancels)
    assert selfCancels.end.times_called == 1
    assert not scheduler.isScheduled(selfCancels)


def test_cancelFromInterruptAction(scheduler: commands2.CommandScheduler):
    selfCancels = commands2.RunCommand(lambda: None)
    counter = OOInteger()

    @scheduler.onCommandInterrupt
    def _(command):
        counter.incrementAndGet()
        scheduler.cancel(selfCancels)

    scheduler.schedule(selfCancels)

    scheduler.cancel(selfCancels)
    assert counter == 1
    assert not scheduler.isScheduled(selfCancels)


def test_cancelFromEndLoop(scheduler: commands2.CommandScheduler):
    dCancelsAll = commands2.Command()
    dCancelsAll.end = lambda interrupted: scheduler.cancelAll()
    dCancelsAll.isFinished = lambda: True

    cCancelsD = commands2.Command()
    cCancelsD.end = lambda interrupted: scheduler.cancel(dCancelsAll)
    cCancelsD.isFinished = lambda: True

    bCancelsC = commands2.Command()
    bCancelsC.end = lambda interrupted: scheduler.cancel(cCancelsD)
    bCancelsC.isFinished = lambda: True

    aCancelsB = commands2.Command()
    aCancelsB.end = lambda interrupted: scheduler.cancel(bCancelsC)
    aCancelsB.isFinished = lambda: True

    start_spying_on(aCancelsB)
    start_spying_on(bCancelsC)
    start_spying_on(cCancelsD)
    start_spying_on(dCancelsAll)

    scheduler.schedule(aCancelsB)
    scheduler.schedule(bCancelsC)
    scheduler.schedule(cCancelsD)
    scheduler.schedule(dCancelsAll)

    scheduler.cancel(aCancelsB)
    assert aCancelsB.end.times_called == 1
    assert bCancelsC.end.times_called == 1
    assert cCancelsD.end.times_called == 1
    assert dCancelsAll.end.times_called == 1
    assert not scheduler.isScheduled(aCancelsB)
    assert not scheduler.isScheduled(bCancelsC)
    assert not scheduler.isScheduled(cCancelsD)
    assert not scheduler.isScheduled(dCancelsAll)


def test_cancelFromEndLoopWhileInRunLoop(scheduler: commands2.CommandScheduler):
    dCancelsAll = commands2.Command()
    dCancelsAll.end = lambda interrupted: scheduler.cancelAll()
    dCancelsAll.isFinished = lambda: True

    cCancelsD = commands2.Command()
    cCancelsD.end = lambda interrupted: scheduler.cancel(dCancelsAll)
    cCancelsD.isFinished = lambda: True

    bCancelsC = commands2.Command()
    bCancelsC.end = lambda interrupted: scheduler.cancel(cCancelsD)
    bCancelsC.isFinished = lambda: True

    aCancelsB = commands2.Command()
    aCancelsB.end = lambda interrupted: scheduler.cancel(bCancelsC)
    aCancelsB.isFinished = lambda: True

    start_spying_on(aCancelsB)
    start_spying_on(bCancelsC)
    start_spying_on(cCancelsD)
    start_spying_on(dCancelsAll)

    scheduler.schedule(aCancelsB)
    scheduler.schedule(bCancelsC)
    scheduler.schedule(cCancelsD)
    scheduler.schedule(dCancelsAll)

    scheduler.run()
    assert aCancelsB.end.times_called == 1
    assert bCancelsC.end.times_called == 1
    assert cCancelsD.end.times_called == 1
    assert dCancelsAll.end.times_called == 1
    assert not scheduler.isScheduled(aCancelsB)
    assert not scheduler.isScheduled(bCancelsC)
    assert not scheduler.isScheduled(cCancelsD)
    assert not scheduler.isScheduled(dCancelsAll)


def test_multiCancelFromEnd(scheduler: commands2.CommandScheduler):
    b = commands2.Command()
    b.isFinished = lambda: True
    start_spying_on(b)

    aCancelB = commands2.Command()

    @patch_via_decorator(aCancelB)
    def end(self, interrupted):
        scheduler.cancel(b)
        scheduler.cancel(self)

    scheduler.schedule(aCancelB)
    scheduler.schedule(b)

    scheduler.cancel(aCancelB)
    assert aCancelB.end.times_called == 2
    assert not scheduler.isScheduled(aCancelB)
    assert not scheduler.isScheduled(b)


def test_scheduleFromEndCancel(scheduler: commands2.CommandScheduler):
    requirement = commands2.Subsystem()
    other = commands2.InstantCommand(lambda: None, requirement)
    selfCancels = commands2.Command()
    start_spying_on(selfCancels)
    selfCancels.addRequirements(requirement)
    selfCancels.end = lambda interrupted: scheduler.schedule(other)
    selfCancels.isFinished = lambda: False

    scheduler.schedule(selfCancels)
    scheduler.cancel(selfCancels)
    assert selfCancels.end.times_called == 1
    assert not scheduler.isScheduled(selfCancels)


def test_scheduleFromEndInterrupt(scheduler: commands2.CommandScheduler):
    counter = OOInteger()
    requirement = commands2.Subsystem()
    other = commands2.InstantCommand(lambda: None, requirement)

    selfCancels = commands2.Command()
    selfCancels.addRequirements(requirement)

    @patch_via_decorator(selfCancels)
    def end(self, interrupted):
        scheduler.schedule(other)

    scheduler.schedule(selfCancels)

    scheduler.schedule(other)
    assert counter == 1
    assert not scheduler.isScheduled(selfCancels)
    assert scheduler.isScheduled(other)


def test_scheduleFromEndInterruptAction(scheduler: commands2.CommandScheduler):
    counter = OOInteger()
    requirement = commands2.Subsystem()
    other = commands2.InstantCommand(lambda: None, requirement)
    selfCancels = commands2.InstantCommand(lambda: None, requirement)

    @scheduler.onCommandInterrupt
    def _(command):
        counter.incrementAndGet()
        scheduler.schedule(other)

    scheduler.schedule(selfCancels)

    scheduler.schedule(other)
    assert counter == 1
    assert not scheduler.isScheduled(selfCancels)
    assert scheduler.isScheduled(other)


@pytest.mark.parametrize(
    "interruptionBehavior",
    [
        commands2.InterruptionBehavior.kCancelIncoming,
        commands2.InterruptionBehavior.kCancelSelf,
    ],
)
def test_scheduleInitializeFromDefaultCommand(
    interruptionBehavior: commands2.InterruptionBehavior,
    scheduler: commands2.CommandScheduler,
):
    counter = OOInteger()
    requirement = commands2.Subsystem()
    other = commands2.InstantCommand(lambda: None, requirement).withInterruptBehavior(
        interruptionBehavior
    )

    defaultCommand = commands2.Command()
    defaultCommand.addRequirements(requirement)

    @patch_via_decorator(defaultCommand)
    def initialize(self):
        counter.incrementAndGet()
        scheduler.schedule(other)

    scheduler.setDefaultCommand(requirement, defaultCommand)

    scheduler.run()
    scheduler.run()
    scheduler.run()

    assert counter == 3
    assert not scheduler.isScheduled(defaultCommand)
    assert scheduler.isScheduled(other)


def test_cancelDefaultCommandFromEnd(
    scheduler: commands2.CommandScheduler,
):
    counter = OOInteger()
    requirement = commands2.Subsystem()
    defaultCommand = commands2.Command()
    defaultCommand.addRequirements(requirement)
    defaultCommand.end = lambda interrupted: counter.incrementAndGet()  # type: ignore

    other = commands2.InstantCommand(lambda: None, requirement)

    cancelDefaultCommand = commands2.Command()

    @patch_via_decorator(cancelDefaultCommand)
    def end(self, interrupted):
        counter.incrementAndGet()
        scheduler.schedule(other)

    scheduler.schedule(cancelDefaultCommand)
    scheduler.setDefaultCommand(requirement, defaultCommand)

    scheduler.run()
    scheduler.cancel(cancelDefaultCommand)

    assert counter == 2
    assert not scheduler.isScheduled(defaultCommand)
    assert scheduler.isScheduled(other)
