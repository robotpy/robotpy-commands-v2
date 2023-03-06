from commands2 import Command, CommandScheduler
from commands2.cmd import nothing, run_once
from tests.CommandTestBase import ValueHolderRequirement


def test_none(scheduler: CommandScheduler):
    cmd = nothing()
    assert isinstance(cmd, Command)
    scheduler.schedule(cmd)
    # Should end immediately
    assert not scheduler.is_scheduled(cmd)


def test_run_once(scheduler: CommandScheduler):
    req = ValueHolderRequirement()
    cmd = run_once(lambda: req.set_value(req.value + 1), {req})
    assert isinstance(cmd, Command)
    scheduler.schedule(cmd)
    # Should end immediately
    assert 1 == req.value
    assert not scheduler.is_scheduled(cmd)
    scheduler.run()
    assert not scheduler.is_scheduled(cmd)
    assert 1 == req.value

