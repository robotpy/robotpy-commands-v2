from wpilib import Joystick

from .button import Button


class JoystickButton(Button):
    def __init__(self, joystick: Joystick, button: int) -> None:
        super().__init__(lambda: joystick.getRawButton(button))
