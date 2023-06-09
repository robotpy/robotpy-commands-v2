import commands2

from util import * # type: ignore
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .util import *

import pytest

def test_requirementInterrupt(scheduler: commands2.CommandScheduler):
    requirement = commands2.Subsystem()
    interrupted = commands2.Command()
    interrupted.addRequirements(requirement)
    interrupter = commands2.Command()
    interrupter.addRequirements(requirement)
    start_spying_on(interrupted)
    start_spying_on(interrupter)

    scheduler.schedule(interrupted)
    scheduler.run()
    scheduler.schedule(interrupter)
    scheduler.run()

    assert interrupted.initialize.times_called == 1
    assert interrupted.execute.times_called == 1
    assert interrupted.end.called_with(interrupted=True)

    assert interrupter.initialize.times_called == 1
    assert interrupter.execute.times_called == 1

    assert not interrupted.isScheduled()
    assert interrupter.isScheduled()

def test_requirementUninterruptible(scheduler: commands2.CommandScheduler):
    requirement = commands2.Subsystem()
    notInterrupted = commands2.RunCommand(lambda: None, requirement).withInterruptBehavior(commands2.InterruptionBehavior.kCancelIncoming)
    interrupter = commands2.Command()
    interrupter.addRequirements(requirement)
    start_spying_on(notInterrupted)

    scheduler.schedule(notInterrupted)
    scheduler.schedule(interrupter)

    assert scheduler.isScheduled(notInterrupted)
    assert not scheduler.isScheduled(interrupter)

def test_defaultCommandRequirementError(scheduler: commands2.CommandScheduler):
    system = commands2.Subsystem()
    missingRequirement = commands2.WaitUntilCommand(lambda: False)

    with pytest.raises(commands2.IllegalCommandUse):
        scheduler.setDefaultCommand(system, missingRequirement)