from wpilib.interfaces import GenericHID
from wpilib.event import EventLoop
from .trigger import Trigger
from ..commandscheduler import CommandScheduler

from typing import overload, Optional

class CommandGenericHID:

    def __init__(self, port: int):
        self._hid = GenericHID(port)

    def getHID(self):
        return self._hid
    
    def button(self, button: int, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getRawButtonPressed(button))

    @overload
    def pov(self, angle: int) -> Trigger:
        ...

    @overload
    def pov(self, pov: int, angle: int, loop: Optional[EventLoop] = None) -> Trigger:
        ...

    def pov(self, *args, **kwargs) -> Trigger:
        pov, angle, loop, *_ = args + (None, None, None)
        if "pov" in kwargs:
            pov = kwargs["pov"]
        if "angle" in kwargs:
            angle = kwargs["angle"]
        if "loop" in kwargs:
            loop = kwargs["loop"]
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()

        return Trigger(loop, lambda: self._hid.getPOV(pov) == angle)

    def povUp(self) -> Trigger:
        return self.pov(0)
    
    def povUpRight(self) -> Trigger:
        return self.pov(45)
    
    def povRight(self) -> Trigger:
        return self.pov(90)
    
    def povDownRight(self) -> Trigger:
        return self.pov(135)
    
    def povDown(self) -> Trigger:
        return self.pov(180)
    
    def povDownLeft(self) -> Trigger:
        return self.pov(225)
    
    def povLeft(self) -> Trigger:
        return self.pov(270)
    
    def povUpLeft(self) -> Trigger:
        return self.pov(315)
    
    def povCenter(self) -> Trigger:
        return self.pov(-1)
    
    def axisLessThan(self, axis: int, threshold: float, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getRawAxis(axis) < threshold)
    
    def axisGreaterThan(self, axis: int, threshold: float, loop: Optional[EventLoop] = None) -> Trigger:
        if loop is None:
            loop = CommandScheduler().getDefaultButtonLoop()
        return Trigger(loop, lambda: self._hid.getRawAxis(axis) > threshold)
