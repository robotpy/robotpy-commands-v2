from wpilib import Joystick

from .button import Button


class JoystickButton(Button):
    """
    A class used to bind command scheduling to joystick button presses.
    Can be composed with other buttons with the operators in Trigger.

    @see Trigger
    """

    def __init__(self, joystick: Joystick, button: int) -> None:
        """
        Creates a JoystickButton that commands can be bound to.

        :param joystick: The joystick on which the button is located.
        :param button: The number of the button on the joystick.
        """
        if not isinstance(joystick, Joystick) or not isinstance(button, int):
            raise TypeError(
                "JoystickButton.__init__(): incompatible constructor arguments. The following argument types are supported:\n"
                "\t1. commands2.button.JoystickButton(joystick: Joystick, button: int)\n"
                f"Invoked with: {joystick}, {button}"
            )
        super().__init__(lambda: joystick.getRawButton(button))
