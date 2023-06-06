import commands2
import pytest


def test_multiple_groups():
    cmd1 = commands2.InstantCommand()
    cmd2 = commands2.InstantCommand()

    _ = commands2.ParallelCommandGroup(cmd1, cmd2)
    with pytest.raises(commands2.IllegalCommandUse):
        commands2.ParallelCommandGroup(cmd1, cmd2)


def test_externally_scheduled(scheduler: commands2.CommandScheduler):
    cmd1 = commands2.InstantCommand()
    cmd2 = commands2.InstantCommand()

    _ = commands2.SequentialCommandGroup(cmd1, cmd2)
    with pytest.raises(
        commands2.IllegalCommandUse,
    ):
        scheduler.schedule(cmd1)
