from ..trigger import Trigger


class Button(Trigger):
    """
    A class used to bind command scheduling to button presses.
    Can be composed with other buttons with the operators in Trigger.

    @see Trigger
    """
    whenPressed = Trigger.whenActive
    whenReleased = Trigger.whenInactive
    whileHeld = Trigger.whileActiveContinous
    whenHeld = Trigger.whileActiveOnce
    toggleWhenPressed = Trigger.toggleWhenActive
    cancelWhenPressed = Trigger.cancelWhenActive