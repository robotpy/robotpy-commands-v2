import commands2
from util import Counter


def test_disable(scheduler: commands2.CommandScheduler):
    counter = Counter()
    cmd = commands2.RunCommand(counter.increment)

    scheduler.schedule(cmd)
    scheduler.run()
    assert counter.value == 1

    scheduler.disable()

    scheduler.run()
    assert counter.value == 1
