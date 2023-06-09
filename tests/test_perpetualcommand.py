import commands2

from util import * # type: ignore
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .util import *

import pytest

def test_perpetualCommandSchedule(scheduler: commands2.CommandScheduler):
    command = commands2.PerpetualCommand(commands2.InstantCommand())

    scheduler.schedule(command)
    scheduler.run()

    assert scheduler.isScheduled(command)