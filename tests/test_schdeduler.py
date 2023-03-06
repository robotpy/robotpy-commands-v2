import re

import pytest

from commands2 import Command, commandify, CommandIllegalUse, CommandScheduler
from commands2.cmd import sequence
from tests.CommandTestBase import CommandTestBase, ValueHolderRequirement


@commandify()
def decorator_command(requirement: ValueHolderRequirement, increment):
    count = 0
    while count < 3:
        requirement.value += increment
        count += 1
        yield


def test_schedule(scheduler: CommandScheduler):
    req = ValueHolderRequirement()
    # print(test_decorator_command)
    cmd: Command = decorator_command(req, 12)
    assert isinstance(cmd, Command)
    assert {req} == cmd.requirements
    assert 0 == req.value
    scheduler.schedule(cmd)
    assert 12 == req.value
    scheduler.run()
    assert 24 == req.value
    # Reschedule, see if count restarts
    scheduler.schedule(cmd)
    scheduler.run()
    assert 36 == req.value
    # Command shouldn't be running anymore after 3 iterations
    scheduler.run()
    assert 36 == req.value
    scheduler.run()
    # Reschedule, this time it should run again for 3 iterations
    scheduler.schedule(cmd)
    assert 48 == req.value
    scheduler.run()
    assert 60 == req.value
    scheduler.run()
    assert 72 == req.value
    # Should end now
    scheduler.run()
    assert 72 == req.value


def test_cancel(scheduler: CommandScheduler):
    req = ValueHolderRequirement()
    # print(test_decorator_command)
    cmd: Command = decorator_command(req, 12)
    assert isinstance(cmd, Command)
    assert {req} == cmd.requirements
    assert 0 == req.value
    scheduler.schedule(cmd)
    assert scheduler.is_scheduled(cmd)
    assert 12 == req.value
    scheduler.run()
    assert 24 == req.value
    # Reschedule, see if count restarts
    scheduler.cancel(cmd)
    assert not scheduler.is_scheduled(cmd)
    scheduler.run()
    # Command shouldn't be running anymore after 3 iterations
    assert 24 == req.value
    # Reschedule, this time it should run again for 3 iterations
    scheduler.schedule(cmd)
    assert 36 == req.value
    scheduler.run()
    assert 48 == req.value
    scheduler.run()
    assert 60 == req.value
    # Should end now
    scheduler.run()
    assert 60 == req.value


def test_composed_errors(scheduler: CommandScheduler):
    req = ValueHolderRequirement()
    cmd = decorator_command(req, 1)
    seq = sequence(cmd, decorator_command(req, 3))

    with pytest.raises(
            CommandIllegalUse,
            match=re.escape("Commands added to a compositions may not be scheduled individually!")):
        scheduler.schedule(cmd)

    with pytest.raises(
            CommandIllegalUse,
            match=re.escape("Commands may not be added to two compositions!")):
        sequence(cmd, decorator_command(req, 4))


def test_requirement_detection(scheduler: CommandScheduler):
    scheduler.run()
    req1, req2 = ValueHolderRequirement(), ValueHolderRequirement()

    @commandify()
    def command(req1, req2, x):
        pass

    cmd = command(req1, req2, 10)
    assert isinstance(cmd, Command)
    assert {req1, req2} == cmd.requirements
