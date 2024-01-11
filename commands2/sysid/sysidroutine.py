from dataclasses import dataclass

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

    class Mechanism:
        def __init__(
            self,
            drive: Callable[[Measure[Voltage]], None],
            log: Optional[Callable[["SysIdRoutineLog"], None]] = None,
            subsystem=None,
            name: Optional[str] = None,
        ):
            self.m_drive = drive
            self.m_log = log or (lambda l: None)
            self.m_subsystem = subsystem
            self.m_name = name or subsystem.getName()

    class Direction:
        kForward = "kForward"
        kReverse = "kReverse"

    def __init__(self, config: Config, mechanism: Mechanism):
        super().__init__(mechanism.m_subsystem.getName())
        self.m_config = config
        self.m_mechanism = mechanism
        self.m_outputVolts = Volts(0)
        self.m_recordState = config.m_recordState or self.recordState

    def quasistatic(self, direction: Direction) -> Command:
        timer = Timer()
        output_sign = 1.0 if direction == self.Direction.kForward else -1.0
        state = {"kForward": "kQuasistaticForward", "kReverse": "kQuasistaticReverse"}[
            direction
        ]

        def command():
            timer.start()

        def execute():
            self.m_outputVolts.mut_replace(
                output_sign
                * timer.get()
                * self.m_config.m_rampRate.in_(Volts.per(Seconds(1))),
                Volts,
            )
            self.m_mechanism.m_drive(self.m_outputVolts)
            self.m_mechanism.m_log(self)
            self.m_recordState(state)

        def end():
            self.m_mechanism.m_drive(Volts.of(0))
            self.m_recordState("kNone")
            timer.stop()

        return (
            self.m_mechanism.m_subsystem.runOnce(command)
            .andThen(self.m_mechanism.m_subsystem.run(execute))
            .finallyDo(end)
            .withName(f"sysid-{state}-{self.m_mechanism.m_name}")
            .withTimeout(self.m_config.m_timeout.in_(Seconds))
        )

    def dynamic(self, direction: Direction) -> Command:
        output_sign = 1.0 if direction == self.Direction.kForward else -1.0
        state = {"kForward": "kDynamicForward", "kReverse": "kDynamicReverse"}[
            direction
        ]

        def command():
            self.m_outputVolts.mut_replace(
                self.m_config.m_stepVoltage.in_(Volts) * output_sign, Volts
            )

        def execute():
            self.m_mechanism.m_drive(self.m_outputVolts)
            self.m_mechanism.m_log(self)
            self.m_recordState(state)

        def end():
            self.m_mechanism.m_drive(Volts.of(0))
            self.m_recordState("kNone")

        return (
            self.m_mechanism.m_subsystem.runOnce(command)
            .andThen(self.m_mechanism.m_subsystem.run(execute))
            .finallyDo(end)
            .withName(f"sysid-{state}-{self.m_mechanism.m_name}")
            .withTimeout(self.m_config.m_timeout.in_(Seconds))
        )
