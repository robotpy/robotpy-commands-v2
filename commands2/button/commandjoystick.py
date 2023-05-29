
from .commandgenerichid import CommandGenericHID
from wpilib import Joystick
from ..commandscheduler import CommandScheduler
from typing import Optional
from wpilib.event import EventLoop
from .trigger import Trigger

class CommandJoystick(CommandGenericHID):

    def __init__(self, port: int):
        super().__init__(port)
        self._hid = Joystick(port)

    def getHID(self):
        return self._hid
    
    def trigger(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getTrigger())
    
    def top(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getTop())
    
    def setXChannel(self, channel: int):
        self._hid.setXChannel(channel)

    def setYChannel(self, channel: int):
        self._hid.setYChannel(channel)

    def setZChannel(self, channel: int):
        self._hid.setZChannel(channel)

    def setThrottleChannel(self, channel: int):
        self._hid.setThrottleChannel(channel)
    
    def setTwistChannel(self, channel: int):
        self._hid.setTwistChannel(channel)
    
    def getXChannel(self) -> int:
        return self._hid.getXChannel()
    
    def getYChannel(self) -> int:
        return self._hid.getYChannel()
    
    def getZChannel(self) -> int:
        return self._hid.getZChannel()
    
    def getThrottleChannel(self) -> int:
        return self._hid.getThrottleChannel()
    
    def getTwistChannel(self) -> int:
        return self._hid.getTwistChannel()
    
    def getX(self) -> float:
        return self._hid.getX()
    
    def getY(self) -> float:
        return self._hid.getY()
    
    def getZ(self) -> float:
        return self._hid.getZ()
    
    def getTwist(self) -> float:
        return self._hid.getTwist()
    
    def getThrottle(self) -> float:
        return self._hid.getThrottle()
    
    def getMagnitude(self) -> float:
        return self._hid.getMagnitude()
    
    def getDirectionRadians(self) -> float:
        return self._hid.getDirectionRadians()
    
    def getDirectionDegrees(self) -> float:
        return self._hid.getDirectionDegrees()
    