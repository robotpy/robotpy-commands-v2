from ..trigger import Trigger


class Button(Trigger):
    whenPressed = Trigger.whenActive
    whenReleased = Trigger.whenInactive
    whileHeld = Trigger.whileActiveContinous
    whenHeld = Trigger.whileActiveOnce
    toggleWhenPressed = Trigger.toggleWhenActive
    cancelWhenPressed = Trigger.cancelWhenActive