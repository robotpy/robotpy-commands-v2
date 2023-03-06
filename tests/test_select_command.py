import enum
import commands2
from CommandTestBase import ConditionHolderRequirement


def test_select_command_int(scheduler: commands2.CommandScheduler):
    c = ConditionHolderRequirement()

    def _assert_false():
        assert False

    cmd1 = commands2.cmd.run(_assert_false)
    cmd2 = commands2.cmd.run(c.set_true)
    cmd3 = commands2.cmd.run(_assert_false)

    sc = commands2.cmd.select({1: cmd1, 2: cmd2, 3: cmd3}, lambda: 2)

    scheduler.schedule(sc)
    scheduler.run()

    assert c.cond


def test_select_command_str(scheduler: commands2.CommandScheduler):
    c = ConditionHolderRequirement()

    def _assert_false():
        assert False

    cmd1 = commands2.cmd.run(_assert_false)
    cmd2 = commands2.cmd.run(c.set_true)
    cmd3 = commands2.cmd.run(_assert_false)

    sc = commands2.cmd.select({"1": cmd1, "2": cmd2, "3": cmd3}, lambda: "2")

    scheduler.schedule(sc)
    scheduler.run()

    assert c.cond


def test_select_command_enum(scheduler: commands2.CommandScheduler):
    c = ConditionHolderRequirement()

    def _assert_false():
        assert False

    class Selector(enum.Enum):
        ONE = enum.auto()
        TWO = enum.auto()
        THREE = enum.auto()

    cmd1 = commands2.cmd.run(_assert_false)
    cmd2 = commands2.cmd.run(c.set_true)
    cmd3 = commands2.cmd.run(_assert_false)

    sc = commands2.cmd.select(
        {
            Selector.ONE: cmd1,
            Selector.TWO: cmd2,
            Selector.THREE: cmd3,
        },
        lambda: Selector.TWO,
    )

    scheduler.schedule(sc)
    scheduler.run()

    assert c.cond
