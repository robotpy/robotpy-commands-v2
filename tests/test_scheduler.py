from typing import TYPE_CHECKING

import commands2
from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

import pytest


def test_schedulerLambdaTestNoInterrupt(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    scheduler.onCommandInitialize(lambda _: counter.incrementAndGet())
    scheduler.onCommandExecute(lambda _: counter.incrementAndGet())
    scheduler.onCommandFinish(lambda _: counter.incrementAndGet())

    scheduler.schedule(commands2.InstantCommand())
    scheduler.run()

    assert counter == 3


def test_schedulerInterruptLambda(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    scheduler.onCommandInterrupt(lambda _: counter.incrementAndGet())

    command = commands2.WaitCommand(10)

    scheduler.schedule(command)
    scheduler.cancel(command)

    assert counter == 1


def test_schedulerInterruptNoCauseLambda(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    @scheduler.onCommandInterrupt
    def _(interrupted, cause):
        assert cause is None
        counter.incrementAndGet()

    command = commands2.cmd.run(lambda: None)

    scheduler.schedule(command)
    scheduler.cancel(command)

    assert counter == 1


def schedulerInterruptCauseLambda(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    subsystem = commands2.Subsystem()
    command = commands2.cmd.run(lambda: None)
    interruptor = subsystem.runOnce(lambda: None)

    @scheduler.onCommandInterrupt
    def _(interrupted, cause):
        assert cause is not None
        assert cause == interruptor
        counter.incrementAndGet()

    scheduler.schedule(command)
    scheduler.schedule(interruptor)

    assert counter == 1


def test_schedulerInterruptCauseLambdaInRunLoop(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    subsystem = commands2.Subsystem()
    command = commands2.cmd.run(lambda: None)
    interruptor = subsystem.runOnce(lambda: None)

    interruptorScheduler = commands2.cmd.runOnce(
        lambda: scheduler.schedule(interruptor)
    )

    @scheduler.onCommandInterrupt
    def _(interrupted, cause):
        assert cause is not None
        assert cause == interruptor
        counter.incrementAndGet()

    scheduler.schedule(command)
    scheduler.schedule(interruptorScheduler)

    scheduler.run()

    assert counter == 1


def test_registerSubsystem(scheduler: commands2.CommandScheduler):
    counter = OOInteger()
    subsystem = commands2.Subsystem()
    subsystem.periodic = lambda: [None, counter.incrementAndGet()][0]

    scheduler.registerSubsystem(subsystem)

    scheduler.run()
    assert counter == 1


def test_unregisterSubsystem(scheduler: commands2.CommandScheduler):
    counter = OOInteger()
    subsystem = commands2.Subsystem()
    subsystem.periodic = lambda: [None, counter.incrementAndGet()][0]

    scheduler.registerSubsystem(subsystem)
    scheduler.unregisterSubsystem(subsystem)

    scheduler.run()
    assert counter == 0


def test_schedulerCancelAll(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    scheduler.onCommandInterrupt(lambda _: counter.incrementAndGet())

    @scheduler.onCommandInterrupt
    def _(command, interruptor):
        assert interruptor is None

    command = commands2.WaitCommand(10)
    command2 = commands2.WaitCommand(10)

    scheduler.schedule(command)
    scheduler.schedule(command2)
    scheduler.cancelAll()

    assert counter == 2


def test_scheduleScheduledNoOp(scheduler: commands2.CommandScheduler):
    counter = OOInteger()

    command = commands2.cmd.startEnd(counter.incrementAndGet, lambda: None)

    scheduler.schedule(command)
    scheduler.schedule(command)

    assert counter == 1
