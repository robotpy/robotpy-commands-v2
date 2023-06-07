import commands2
from ntcore import NetworkTableInstance

from util import * # type: ignore
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .util import *

def test_networkbutton(scheduler: commands2.CommandScheduler, nt_instance: NetworkTableInstance):
    # command = commands2.Command()
    command = commands2.Command()
    mock_object(command)
    
    pub = nt_instance.getTable("TestTable").getBooleanTopic("Test").publish()

    button = commands2.button.NetworkButton(nt_instance, "TestTable", "Test")

    pub.set(False)
    button.onTrue(command)
    scheduler.run()
    # assert not command.isScheduled()
    assert command.schedule.times_called == 0
    pub.set(True)
    scheduler.run()
    scheduler.run()
    assert command.schedule.times_called > 0