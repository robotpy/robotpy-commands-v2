from typing import TYPE_CHECKING

import commands2
from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

import pytest


def test_conditionalCommand(scheduler: commands2.CommandScheduler):
    command1 = commands2.Command()
    command1.isFinished = lambda: True
    command2 = commands2.Command()

    start_spying_on(command1)
    start_spying_on(command2)

    conditionalCommand = commands2.ConditionalCommand(command1, command2, lambda: True)

    scheduler.schedule(conditionalCommand)
    scheduler.run()

    verify(command1).initialize()
    verify(command1).execute()
    verify(command1).end(False)

    verify(command2, never()).initialize()
    verify(command2, never()).execute()
    verify(command2, never()).end(False)


def test_conditionalCommandRequirement(scheduler: commands2.CommandScheduler):
    system1 = commands2.Subsystem()
    system2 = commands2.Subsystem()
    system3 = commands2.Subsystem()

    command1 = commands2.Command()
    command1.addRequirements(system1, system2)
    command2 = commands2.Command()
    command2.addRequirements(system3)

    start_spying_on(command1)
    start_spying_on(command2)

    conditionalCommand = commands2.ConditionalCommand(command1, command2, lambda: True)

    scheduler.schedule(conditionalCommand)
    scheduler.schedule(commands2.InstantCommand(lambda: None, system3))

    assert not scheduler.isScheduled(conditionalCommand)

    assert command1.end.called_with(True)
    assert not command2.end.called_with(True)


@pytest.mark.parametrize(
    "name,expected,command1,command2,selector",
    [
        (
            "AllCancelSelf",
            commands2.InterruptionBehavior.kCancelSelf,
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelSelf
            ),
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelSelf
            ),
            lambda: True,
        ),
        (
            "AllCancelIncoming",
            commands2.InterruptionBehavior.kCancelIncoming,
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelIncoming
            ),
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelIncoming
            ),
            lambda: True,
        ),
        (
            "OneCancelSelfOneIncoming",
            commands2.InterruptionBehavior.kCancelSelf,
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelSelf
            ),
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelIncoming
            ),
            lambda: True,
        ),
        (
            "OneCancelIncomingOneSelf",
            commands2.InterruptionBehavior.kCancelSelf,
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelIncoming
            ),
            commands2.WaitUntilCommand(lambda: False).withInterruptBehavior(
                commands2.InterruptionBehavior.kCancelSelf
            ),
            lambda: True,
        ),
    ],
)
def test_interruptible(
    name,
    expected,
    command1,
    command2,
    selector,
):
    command = commands2.ConditionalCommand(command1, command2, selector)
    assert command.getInterruptionBehavior() == expected


@pytest.mark.parametrize(
    "name,expected,command1,command2,selector",
    [
        (
            "AllFalse",
            False,
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(False),
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(False),
            lambda: True,
        ),
        (
            "AllTrue",
            True,
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(True),
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(True),
            lambda: True,
        ),
        (
            "OneTrueOneFalse",
            False,
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(True),
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(False),
            lambda: True,
        ),
        (
            "OneFalseOneTrue",
            False,
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(False),
            commands2.WaitUntilCommand(lambda: False).ignoringDisable(True),
            lambda: True,
        ),
    ],
)
def test_runsWhenDisabled(
    name,
    expected,
    command1,
    command2,
    selector,
):
    command = commands2.ConditionalCommand(command1, command2, selector)
    assert command.runsWhenDisabled() == expected