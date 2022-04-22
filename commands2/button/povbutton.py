from wpilib import Joystick

from .button import Button


class POVButton(Button):
    def __init__(self, joystick: Joystick, angle: int, povNumber: int = 0) -> None:
        super().__init__(lambda: joystick.getPOV(povNumber) == angle)
