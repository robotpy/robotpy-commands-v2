from dataclasses import dataclass
from enum import Enum

from wpilib.sysid import SysIdRoutineLog
from ..command import Command
from wpilib import Timer

from wpimath.units import seconds, volts
from wpilib.units import (
    Volts,
    Seconds,
    Voltage,
    Velocity,
    Measure,
    Time,
)
from typing import Callable, Dict, Optional


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
        self.outputVolts = Volts(0)
        self.recordState = config.recordState or self.recordState

    def quasistatic(self, direction: Direction) -> Command:
        timer = Timer()
        output_sign = 1.0 if direction == self.Direction.kForward else -1.0
        state = {"kForward": "kQuasistaticForward", "kReverse": "kQuasistaticReverse"}[
            direction
        ]

        def command():
            timer.start()

        def execute():
            self.outputVolts.mut_replace(
                output_sign
                * timer.get()
                * self.config.rampRate.in_(Volts.per(Seconds(1))),
                Volts,
            )
            self.mechanism.drive(self.outputVolts)
            self.mechanism.log(self)
            self.recordState(state)

        def end():
            self.mechanism.drive(Volts.of(0))
            self.recordState("kNone")
            timer.stop()

        return (
            self.mechanism.subsystem.runOnce(command)
            .andThen(self.mechanism.subsystem.run(execute))
            .finallyDo(end)
            .withName(f"sysid-{state}-{self.mechanism.name}")
            .withTimeout(self.config.timeout.in_(Seconds))
        )

    def dynamic(self, direction: Direction) -> Command:
        output_sign = 1.0 if direction == self.Direction.kForward else -1.0
        state = {"kForward": "kDynamicForward", "kReverse": "kDynamicReverse"}[
            direction
        ]

        def command():
            self.outputVolts.mut_replace(
                self.config.stepVoltage.in_(Volts) * output_sign, Volts
            )

        def execute():
            self.mechanism.drive(self.outputVolts)
            self.mechanism.log(self)
            self.recordState(state)

        def end():
            self.mechanism.drive(Volts.of(0))
            self.recordState("kNone")

        return (
            self.mechanism.subsystem.runOnce(command)
            .andThen(self.mechanism.subsystem.run(execute))
            .finallyDo(end)
            .withName(f"sysid-{state}-{self.mechanism.name}")
            .withTimeout(self.config.timeout.in_(Seconds))
        )
