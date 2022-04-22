from ..trigger import Trigger

class Button(Trigger):
	whenPressed = Trigger.whenActive
	whenReleased = Trigger.whenInactive



