
from .trigger import Trigger
from wpilib.interfaces import GenericHID

class POVButton(Trigger):

    def __init__(self, joystick: GenericHID, angle: int, povNumber: int=0):
        super().__init__(lambda: joystick.getPOV(povNumber) == angle)