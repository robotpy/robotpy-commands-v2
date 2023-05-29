
from .commandgenerichid import CommandGenericHID
from wpilib import Joystick
from ..commandscheduler import CommandScheduler
from typing import Optional
from wpilib.event import EventLoop
from .trigger import Trigger
from wpilib import PS4Controller



class CommandPS4Controller(CommandGenericHID):

    def __init__(self, port: int):
        super().__init__(port)
        self._hid = PS4Controller(port)

    def getHID(self):
        return self._hid

    def L2(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getL2Button())

    def R2(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getR2Button())
    
    def L1(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getL1Button())
    
    def R1(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getR1Button())
    
    def L3(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getL3Button())
    
    def R3(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getR3Button())
    
    def square(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getSquareButton())
    
    def cross(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getCrossButton())
    
    def triangle(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getTriangleButton())
    
    def circle(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getCircleButton())
    
    def share(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getShareButton())
    
    def PS(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getPSButton())
    
    def options(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getOptionsButton())
    
    def touchpad(self, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getTouchpad())
    
    def getLeftX(self) -> float:
        return self._hid.getLeftX()
    
    def getRightX(self) -> float:
        return self._hid.getRightX()
    
    def getLeftY(self) -> float:
        return self._hid.getLeftY()
    
    def getRightY(self) -> float:
        return self._hid.getRightY()
    
    def getL2Axis(self) -> float:
        return self._hid.getL2Axis()
    
    def getR2Axis(self) -> float:
        return self._hid.getR2Axis()