import commands2

from util import * # type: ignore
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .util import *

import pytest

def test_instantCommandSchedule(scheduler: commands2.CommandScheduler):
    cond = OOBoolean()

    command = commands2.InstantCommand(lambda: cond.set(True))

    scheduler.schedule(command)
    scheduler.run()

    assert cond
    assert not scheduler.isScheduled(command)