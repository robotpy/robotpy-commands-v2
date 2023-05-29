
from .trigger import Trigger
from typing import overload
from wpilib.interfaces import GenericHID

class JoystickButton(Trigger):

    def __init__(self, joystick: GenericHID, buttonNumber: int):
        super().__init__(lambda: joystick.getRawButton(buttonNumber))