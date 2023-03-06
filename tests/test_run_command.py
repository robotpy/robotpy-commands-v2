import commands2
from CommandTestBase import ValueHolderRequirement


def test_run_command(scheduler: commands2.CommandScheduler):
    counter = ValueHolderRequirement()
    cmd = commands2.cmd.run(counter.increment)

    scheduler.schedule(cmd)
    scheduler.run()
    scheduler.run()
    scheduler.run()

    assert counter.value == 3
