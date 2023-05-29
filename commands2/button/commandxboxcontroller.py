
from .commandgenerichid import CommandGenericHID
from wpilib import Joystick
from ..commandscheduler import CommandScheduler
from typing import Optional, overload
from wpilib.event import EventLoop
from .trigger import Trigger
from wpilib import XboxController

class CommandXboxController(CommandGenericHID):

    def __init__(self, port: int):
        super().__init__(port)
        self._hid = XboxController(port)
    
    def getHID(self):
        return self._hid
    
    def leftBumper(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getLeftBumper())
    
    def rightBumper(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getRightBumper())
    
    def leftStick(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getLeftStickButton())
    
    def rightStick(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getRightStickButton())
    
    def a(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getAButton())
    
    def b(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getBButton())
    
    def x(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getXButton())
    
    def y(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getYButton())
    
    def start(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getStartButton())
    
    def back(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getBackButton())
    
    @overload
    def leftTrigger(self, threshold: float=0.5) -> Trigger:
        pass

    @overload
    def leftTrigger(self, loop: Optional[EventLoop], threshold: float=0.5) -> Trigger:
        pass

    def leftTrigger(self, *args, **kwargs) -> Trigger:
        loop, threshold, *_ = args + (None, None)
        if "loop" in kwargs:
            loop = kwargs["loop"]
        if "threshold" in kwargs:
            threshold = kwargs["threshold"]
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        if threshold is None:
            threshold = 0.5
        return Trigger(loop, lambda: self._hid.getLeftTriggerAxis() > threshold)

    @overload
    def rightTrigger(self, threshold: float=0.5) -> Trigger:
        pass

    @overload
    def rightTrigger(self, loop: Optional[EventLoop], threshold: float=0.5) -> Trigger:
        pass

    def rightTrigger(self, *args, **kwargs) -> Trigger:
        loop, threshold, *_ = args + (None, None)
        if "loop" in kwargs:
            loop = kwargs["loop"]
        if "threshold" in kwargs:
            threshold = kwargs["threshold"]
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        if threshold is None:
            threshold = 0.5
        return Trigger(loop, lambda: self._hid.getRightTriggerAxis() > threshold)
    
    def getLeftX(self) -> float:
        return self._hid.getLeftX()
    
    def getRightX(self) -> float:
        return self._hid.getRightX()
    
    def getLeftY(self) -> float:
        return self._hid.getLeftY()
    
    def getRightY(self) -> float:
        return self._hid.getRightY()
    
    def getLeftTriggerAxis(self) -> float:
        return self._hid.getLeftTriggerAxis()
    
    def getRightTriggerAxis(self) -> float:
        return self._hid.getRightTriggerAxis()
    