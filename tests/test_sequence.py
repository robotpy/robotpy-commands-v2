import unittest

from commands2 import commandify, Command, CommandScheduler
from commands2.cmd import sequence, run_once, parallel
from tests.CommandTestBase import CommandTestBase, ValueHolderRequirement


def test_sequence(scheduler: CommandScheduler):
    req1 = ValueHolderRequirement()
    req2 = ValueHolderRequirement()

    def increment_command(requirement: ValueHolderRequirement, increment: int):
        count = 0
        while count < 3:
            requirement.value += increment
            count += 1
            yield

    cmd1: Command = commandify(lambda interrupted, *args, **kwargs: req1.set_value(-3), {req1}) \
        (increment_command)(req1, 10)
    cmd2 = run_once(lambda: req1.set_value(0), {req1})
    cmd3: Command = commandify(lambda interrupted, *args, **kwargs: req2.set_value(3), {req2}) \
        (increment_command)(req2, -5)

    cmd = sequence(cmd1, cmd2, cmd3)
    assert {req1, req2} == cmd.requirements

    scheduler.schedule(cmd)
    assert 10 == req1.value
    assert 0 == req2.value

    scheduler.run()
    assert 20 == req1.value
    assert 0 == req2.value

    scheduler.cancel(cmd)
    assert -3 == req1.value
    assert 0 == req2.value

    # Schedule again

    scheduler.schedule(cmd)
    assert 7 == req1.value
    assert 0 == req2.value

    scheduler.run()
    assert 17 == req1.value
    assert 0 == req2.value

    scheduler.run()
    assert 27 == req1.value
    assert 0 == req2.value

    scheduler.run()
    assert 0 == req1.value
    assert -5 == req2.value

    scheduler.run()
    assert 0 == req1.value
    assert -10 == req2.value

    scheduler.cancel(cmd)
    assert 0 == req1.value
    assert 3 == req2.value


def test_parallel(scheduler: CommandScheduler):
    req1 = ValueHolderRequirement()
    req2 = ValueHolderRequirement()
    req3 = ValueHolderRequirement()

    def increment_command(requirement: ValueHolderRequirement, increment: int = 10,
                          iterations: int = 3):
        count = 0
        while count < iterations:
            requirement.value += increment
            count += 1
            yield

    cmd1: Command = commandify(lambda interrupted, *args, **kwargs: req1.set_value(-5), {req1}) \
        (increment_command)(req1, iterations=0)
    cmd2: Command = commandify(lambda interrupted, *args, **kwargs: req2.set_value(-5), {req2}) \
        (increment_command)(req2)
    cmd3: Command = commandify(lambda interrupted, *args, **kwargs: req3.set_value(-5), {req3}) \
        (increment_command)(req3, iterations=1)

    cmd = parallel(cmd1, cmd2, cmd3)
    assert {req1, req2, req3} == cmd.requirements

    scheduler.schedule(cmd)
    assert -5 == req1.value
    assert 10 == req2.value
    assert 10 == req3.value

    scheduler.run()
    assert -5 == req1.value
    assert 20 == req2.value
    assert -5 == req3.value

    scheduler.cancel(cmd)
    assert -5 == req1.value
    assert -5 == req2.value
    assert -5 == req3.value

    # Schedule again

    scheduler.schedule(cmd)
    assert -5 == req1.value
    assert 5 == req2.value
    assert 5 == req3.value

    scheduler.run()
    assert -5 == req1.value
    assert 15 == req2.value
    assert -5 == req3.value

    scheduler.run()
    assert -5 == req1.value
    assert 25 == req2.value
    assert -5 == req3.value

    scheduler.run()
    assert -5 == req1.value
    assert -5 == req2.value
    assert -5 == req3.value

    scheduler.run()
    scheduler.run()
    assert not scheduler.is_scheduled(cmd)
