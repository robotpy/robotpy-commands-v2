# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
from __future__ import annotations
from typing import Set, Callable, Union, List, Optional

from wpimath.controller import (
    HolonomicDriveController,
    PIDController,
    ProfiledPIDControllerRadians,
    SimpleMotorFeedforwardMeters,
)
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.kinematics import (
    ChassisSpeeds,
    MecanumDriveKinematics,
    MecanumDriveWheelSpeeds,
)
from wpimath.trajectory import Trajectory
from wpilib import Timer

from .subsystem import Subsystem
from .command import Command


class MecanumControllerCommand(Command):
    """
    A command that uses two PID controllers (PIDController) and a ProfiledPIDController
    (ProfiledPIDController) to follow a trajectory Trajectory with a mecanum drive.

    The command handles trajectory-following, Velocity PID calculations, and feedforwards
    internally. This is intended to be a more-or-less "complete solution" that can be used by teams
    without a great deal of controls expertise.

    Advanced teams seeking more flexibility (for example, those who wish to use the onboard PID
    functionality of a "smart" motor controller) may use the secondary constructor that omits the PID
    and feedforward functionality, returning only the raw wheel speeds from the PID controllers.

    The robot angle controller does not follow the angle given by the trajectory but rather goes
    to the angle given in the final state of the trajectory.
    """

    def __init__(
        self,
        trajectory: Trajectory,
        pose: Callable[[], Pose2d],
        kinematics: MecanumDriveKinematics,
        xController: PIDController,
        yController: PIDController,
        thetaController: ProfiledPIDControllerRadians,
        # rotationSupplier: Callable[[], Rotation2d],
        maxWheelVelocityMetersPerSecond: float,
        outputConsumer: Callable[[MecanumDriveWheelSpeeds], None],
        *requirements: Subsystem,
        feedforward: Optional[SimpleMotorFeedforwardMeters] = None,
        frontLeftController: Optional[PIDController] = None,
        rearLeftController: Optional[PIDController] = None,
        frontRightController: Optional[PIDController] = None,
        rearRightController: Optional[PIDController] = None,
        currentWheelSpeedsSupplier: Optional[
            Callable[[], MecanumDriveWheelSpeeds]
        ] = None,
    ):
        super().__init__()

        self._trajectory: Trajectory = trajectory
        self._pose = pose
        self._kinematics = kinematics
        self._controller = HolonomicDriveController(
            xController, yController, thetaController
        )
        # self.rotationSupplier = rotationSupplier
        self._maxWheelVelocityMetersPerSecond = maxWheelVelocityMetersPerSecond
        self._outputConsumer = outputConsumer

        # Member to track time of last loop execution
        self._prevTime = 0
        self._usePID = False

        # Optional requirements checks.  If any one of the feedforward, pidcontrollers, or wheelspeedsuppliers
        # are not None, then all should be non-null.  Raise RuntimeError if they are. The List of PID controllers
        # should be equal to each corner of the robot being commanded.
        if (
            feedforward
            or frontLeftController
            or rearLeftController
            or frontRightController
            or rearRightController
            or currentWheelSpeedsSupplier is not None
        ):
            if (
                feedforward
                or frontLeftController
                or rearLeftController
                or frontRightController
                or rearRightController
                or currentWheelSpeedsSupplier is None
            ):
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, one of the arguments passed in was None "
                )

            self._frontLeftController = frontLeftController
            self._rearLeftController = rearLeftController
            self._frontRightController = frontRightController
            self._rearRightController = rearRightController

            if currentWheelSpeedsSupplier is None:
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, no WheelSpeedSupplierProvided."
                )

            self._currentWheelSpeeds = currentWheelSpeedsSupplier

            if feedforward is None:
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, no SimpleMotorFeedforwardMeters supplied."
                )

            self._feedforward = feedforward

            # All the optional requirements verify, set usePid flag to True
            self._usePID = True

        # Set the requirements for the command
        self.addRequirements(*requirements)

        self._timer = Timer()

    def initialize(self):
        initialState = self._trajectory.sample(0)
        initialXVelocity = initialState.velocity * initialState.pose.rotation().cos()
        initialYVelocity = initialState.velocity * initialState.pose.rotation().sin()
        self.m_prevSpeeds = self._kinematics.toWheelSpeeds(
            ChassisSpeeds(initialXVelocity, initialYVelocity, 0.0)
        )
        self._timer.restart()

    def execute(self):
        curTime = self._timer.get()
        dt = curTime - self._prevTime
        desiredState = self._trajectory.sample(curTime)
        targetChassisSpeeds = self._controller.calculate(
            self._pose(), desiredState, desiredState.pose.rotation()
        )
        targetWheelSpeeds = self._kinematics.toWheelSpeeds(targetChassisSpeeds)
        targetWheelSpeeds.desaturate(self._maxWheelVelocityMetersPerSecond)
        frontLeftSpeedSetpoint = targetWheelSpeeds.frontLeft
        rearLeftSpeedSetpoint = targetWheelSpeeds.rearLeft
        frontRightSpeedSetpoint = targetWheelSpeeds.frontRight
        rearRightSpeedSetpoint = targetWheelSpeeds.rearRight

        if not self._usePID:
            self._outputConsumer(
                MecanumDriveWheelSpeeds(
                    frontLeftSpeedSetpoint,
                    frontRightSpeedSetpoint,
                    rearLeftSpeedSetpoint,
                    rearRightSpeedSetpoint,
                )
            )
        else:
            frontLeftFeedforward = self._feedforward.calculate(
                frontLeftSpeedSetpoint,
                (frontLeftSpeedSetpoint - self.m_prevSpeeds.frontLeft) / dt,
            )
            rearLeftFeedforward = self._feedforward.calculate(
                rearLeftSpeedSetpoint,
                (rearLeftSpeedSetpoint - self.m_prevSpeeds.rearLeft) / dt,
            )
            frontRightFeedforward = self._feedforward.calculate(
                frontRightSpeedSetpoint,
                (frontRightSpeedSetpoint - self.m_prevSpeeds.frontRight) / dt,
            )
            rearRightFeedforward = self._feedforward.calculate(
                rearRightSpeedSetpoint,
                (rearRightSpeedSetpoint - self.m_prevSpeeds.rearRight) / dt,
            )
            frontLeftOutput = (
                frontLeftFeedforward
                + self._frontLeftController.calculate(
                    self._currentWheelSpeeds().frontLeft,
                    frontLeftSpeedSetpoint,
                )
            )
            rearLeftOutput = rearLeftFeedforward + self._rearLeftController.calculate(
                self._currentWheelSpeeds().rearLeft,
                rearLeftSpeedSetpoint,
            )
            frontRightOutput = (
                frontRightFeedforward
                + self._frontRightController.calculate(
                    self._currentWheelSpeeds().frontRight,
                    frontRightSpeedSetpoint,
                )
            )
            rearRightOutput = (
                rearRightFeedforward
                + self._rearRightController.calculate(
                    self._currentWheelSpeeds().rearRight,
                    rearRightSpeedSetpoint,
                )
            )
            self._outputConsumer(
                frontLeftOutput, frontRightOutput, rearLeftOutput, rearRightOutput
            )

        # Store current call information for next call
        self._prevTime = curTime
        self.m_prevSpeeds = targetWheelSpeeds

    def end(self, interrupted):
        self._timer.stop()

    def isFinished(self):
        return self._timer.hasElapsed(self._trajectory.totalTime())
