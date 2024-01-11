from dataclasses import dataclass
from enum import Enum

from wpilib.sysid import SysIdRoutineLog
from ..command import Command
from wpilib import Timer

from wpimath.units import seconds, volts

from typing import Callable, Optional


volts_per_second = float


class SysIdRoutine(SysIdRoutineLog):
    @dataclass
    class Config:
        rampRate: volts_per_second = 1.0
        stepVoltage: volts = 7.0
        timeout: seconds = 10.0
        recordState: Callable[["SysIdRoutineLog.State"], None] = None

    @dataclass
    class Mechanism:
        drive: volts
        log: Optional[Callable[["SysIdRoutineLog", None]]] = None
        subsystem = None
        name: Optional[str] = None

    class Direction(Enum):
        kForward = 0
        kReverse = 1

    def __init__(self, config: Config, mechanism: Mechanism):
        super().__init__(mechanism.subsystem.getName())
        self.config = config
        self.mechanism = mechanism
        self.outputVolts = 0.0
        self.recordState = config.recordState or self.recordState

    def quasistatic(self, direction: Direction) -> Command:
        timer = Timer()
        output_sign = 1.0 if direction == self.Direction.kForward else -1.0
        state = {
            self.Direction.kForward: SysIdRoutineLog.State.kQuasistaticForward,
            self.Direction.kReverse: SysIdRoutineLog.State.kQuasistaticReverse,
        }[direction]

        def command():
            timer.start()

        def execute():
            self.outputVolts = output_sign * timer.get() * self.config.rampRate
            self.mechanism.drive(self.outputVolts)
            self.mechanism.log(self)
            self.recordState(state)

        def end():
            self.mechanism.drive(0.0)
            self.recordState(SysIdRoutineLog.State.kNone)
            timer.stop()

        return (
            self.mechanism.subsystem.runOnce(command)
            .andThen(self.mechanism.subsystem.run(execute))
            .finallyDo(end)
            .withName(f"sysid-{state}-{self.mechanism.name}")
            .withTimeout(self.config.timeout)
        )

    def dynamic(self, direction: Direction) -> Command:
        output_sign = 1.0 if direction == self.Direction.kForward else -1.0
        state = {
            self.Direction.kForward: SysIdRoutineLog.State.kDynamicForward,
            self.Direction.kReverse: SysIdRoutineLog.State.kDynamicReverse,
        }[direction]

        def command():
            self.outputVolts = self.config.stepVoltage * output_sign

        def execute():
            self.mechanism.drive(self.outputVolts)
            self.mechanism.log(self)
            self.recordState(state)

        def end():
            self.mechanism.drive(0.0)
            self.recordState(SysIdRoutineLog.State.kNone)

        return (
            self.mechanism.subsystem.runOnce(command)
            .andThen(self.mechanism.subsystem.run(execute))
            .finallyDo(end)
            .withName(f"sysid-{state}-{self.mechanism.name}")
            .withTimeout(self.config.timeout)
        )
