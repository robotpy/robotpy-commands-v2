# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
from __future__ import annotations

from typing import Union, overload

from .subsystem import Subsystem
from wpimath.trajectory import TrapezoidProfile, TrapezoidProfileRadians


class TrapezoidProfileSubsystem(Subsystem):
    """
    A subsystem that generates and runs trapezoidal motion profiles automatically. The user specifies
    how to use the current state of the motion profile by overriding the `useState` method.
    """

    @overload
    def __init__(
        self,
        constraints: Union[
            TrapezoidProfile.Constraints, TrapezoidProfileRadians.Constraints
        ],
    ):
        """
        Creates a new TrapezoidProfileSubsystem.

        :param constraints: The constraints (maximum velocity and acceleration) for the profiles.
        """
        ...

    @overload
    def __init__(
        self,
        constraints: Union[
            TrapezoidProfile.Constraints, TrapezoidProfileRadians.Constraints
        ],
        initial_position: float = 0.0,
    ):
        """
        Creates a new TrapezoidProfileSubsystem.

        :param constraints: The constraints (maximum velocity and acceleration) for the profiles.
        :param initial_position: The initial position of the controlled mechanism when the subsystem is constructed.
        """
        ...

    def __init__(
        self,
        constraints: Union[
            TrapezoidProfile.Constraints, TrapezoidProfileRadians.Constraints
        ],
        initial_position: float = 0.0,
        period: float = 0.02,
    ):
        """
        Creates a new TrapezoidProfileSubsystem.

        :param constraints: The constraints (maximum velocity and acceleration) for the profiles.
        :param initial_position: The initial position of the controlled mechanism when the subsystem is constructed.
        :param period: The period of the main robot loop, in seconds.
        """
        if isinstance(constraints, TrapezoidProfile.Constraints):
            self._state: TrapezoidProfile.State = TrapezoidProfile.State(
                initial_position
            )
            self._profile: TrapezoidProfile = TrapezoidProfile(constraints)
        else:  # TrapezoidProfileradians
            self._state: TrapezoidProfileRadians.State = TrapezoidProfileRadians.State(  # type: ignore
                initial_position
            )
            self._profile: TrapezoidProfileRadians = TrapezoidProfileRadians(constraints)  # type: ignore

        self.setGoal(self._state)
        self._period = period
        self._enabled = True

    def periodic(self):
        """
        Executes the TrapezoidProfileSubsystem logic during each periodic update.

        This method is called synchronously from the subsystem's periodic() method.
        """
        self._state = self._profile.calculate(self._period, self._goal, self._state)
        if self._enabled:
            self.useState(self._state)

    def setGoal(
        self, goal: Union[TrapezoidProfile.State, TrapezoidProfileRadians.State]
    ):
        """
        Sets the goal state for the subsystem. Goal velocity assumed to be zero.

        :param goal: The goal position for the subsystem's motion profile. The goal
        can either be a `TrapezoidProfile.State` or `float`. If float is provided,
        the assumed velocity for the goal will be 0.
        """
        self._goal = goal

    def enable(self):
        """Enable the TrapezoidProfileSubsystem's output."""
        self._enabled = True

    def disable(self):
        """Disable the TrapezoidProfileSubsystem's output."""
        self._enabled = False

    def useState(
        self, state: Union[TrapezoidProfile.State, TrapezoidProfileRadians.State]
    ):
        """
        Users should override this to consume the current state of the motion profile.

        :param state: The current state of the motion profile.
        """
        raise NotImplementedError("Subclasses must implement this method")
