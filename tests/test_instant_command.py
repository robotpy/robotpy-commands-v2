import commands2
from CommandTestBase import ConditionHolderRequirement
from commands2.cmd import run_once


def test_instant_command(scheduler: commands2.CommandScheduler):
    cond = ConditionHolderRequirement()

    cmd = run_once(cond.set_true, {cond})

    scheduler.schedule(cmd)
    scheduler.run()

    assert cond.get_condition()
    assert not scheduler.is_scheduled(cmd)
