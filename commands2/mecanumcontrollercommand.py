# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
from __future__ import annotations
from typing import Set, Callable, Union, List

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

    __FRONT_LEFT_INDEX = 0
    __REAR_LEFT_INDEX = 1
    __FRONT_RIGHT_INDEX = 2
    __REAR_RIGHT_INDEX = 3

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
        outputConsumer: Callable[[Union[List[float], MecanumDriveWheelSpeeds]], None],
        *requirements: Subsystem,
        feedforward: SimpleMotorFeedforwardMeters | None = None,
        chassisWheelPIDControllers: List[PIDController] | None = None,
        currentWheelSpeedsSupplier: Callable[[], MecanumDriveWheelSpeeds] | None = None,
    ):
        super().__init__()

        self.trajectory: Trajectory = trajectory
        self.pose = pose
        self.kinematics = kinematics
        self.controller = HolonomicDriveController(
            xController, yController, thetaController
        )
        # self.rotationSupplier = rotationSupplier
        self.maxWheelVelocityMetersPerSecond = maxWheelVelocityMetersPerSecond
        self.outputConsumer = outputConsumer

        # Member to track time of last loop execution
        self.prevTime = 0
        self.usePID = False

        # Optional requirements checks.  If any one of the feedforward, pidcontrollers, or wheelspeedsuppliers
        # are not None, then all should be non-null.  Raise RuntimeError if they are. The List of PID controllers
        # should be equal to each corner of the robot being commanded.
        if (
            feedforward
            or chassisWheelPIDControllers
            or currentWheelSpeedsSupplier is not None
        ):
            if (
                feedforward
                or chassisWheelPIDControllers
                or currentWheelSpeedsSupplier is None
            ):
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, one of the arguments passed in was None: \n \
                                   \t Feedforward: {feedforward} - chassisWheelPIDControllers: {chassisWheelPIDControllers} - wheelSpeedSupplier: {currentWheelSpeedsSupplier} "
                )

            # check the length of the PID controllers
            if len(chassisWheelPIDControllers != 4):
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, not enough PID controllers provided.\n \
                                   \t Required: 4 - Provided: {len(chassisWheelPIDControllers)}"
                )

            self.frontLeftController = chassisWheelPIDControllers[
                self.__FRONT_LEFT_INDEX
            ]
            self.rearLeftController = chassisWheelPIDControllers[self.__REAR_LEFT_INDEX]
            self.frontRightController = chassisWheelPIDControllers[
                self.__FRONT_RIGHT_INDEX
            ]
            self.rearRightController = chassisWheelPIDControllers[
                self.__REAR_RIGHT_INDEX
            ]

            if currentWheelSpeedsSupplier is None:
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, no WheelSpeedSupplierProvided."
                )

            self.currentWheelSpeeds = currentWheelSpeedsSupplier

            if feedforward is None:
                raise RuntimeError(
                    f"Failed to instantiate MecanumControllerCommand, no SimpleMotorFeedforwardMeters supplied."
                )

            self.feedforward: SimpleMotorFeedforwardMeters = feedforward

            # All the optional requirements verify, set usePid flag to True
            self.usePID = True

        # Set the requirements for the command
        self.addRequirements(*requirements)

        self.timer = Timer()

    def initialize(self):
        initialState: Trajectory.State = self.trajectory.sample(0)
        initialXVelocity = initialState.velocity * initialState.pose.rotation().cos()
        initialYVelocity = initialState.velocity * initialState.pose.rotation().sin()
        self.m_prevSpeeds = self.kinematics.toWheelSpeeds(
            ChassisSpeeds(initialXVelocity, initialYVelocity, 0.0)
        )
        self.timer.restart()
        self.prevTime = 0

    def execute(self):
        curTime = self.timer.get()
        dt = curTime - self.prevTime
        desiredState: Trajectory.State = self.trajectory.sample(curTime)
        targetChassisSpeeds = self.controller.calculate(
            self.pose(),
            desiredState,
            desiredState.pose.rotation()
            # self.pose.get(), desiredState, self.rotationSupplier.get()
        )
        targetWheelSpeeds = self.kinematics.toWheelSpeeds(targetChassisSpeeds)
        targetWheelSpeeds.desaturate(self.maxWheelVelocityMetersPerSecond)
        frontLeftSpeedSetpoint = targetWheelSpeeds.frontLeft
        rearLeftSpeedSetpoint = targetWheelSpeeds.rearLeft
        frontRightSpeedSetpoint = targetWheelSpeeds.frontRight
        rearRightSpeedSetpoint = targetWheelSpeeds.rearRight

        if not self.usePID:
            self.outputConsumer(
                MecanumDriveWheelSpeeds(
                    frontLeftSpeedSetpoint,
                    frontRightSpeedSetpoint,
                    rearLeftSpeedSetpoint,
                    rearRightSpeedSetpoint,
                )
            )
        else:
            frontLeftFeedforward = self.feedforward.calculate(
                frontLeftSpeedSetpoint,
                (frontLeftSpeedSetpoint - self.m_prevSpeeds.frontLeft) / dt,
            )
            rearLeftFeedforward = self.feedforward.calculate(
                rearLeftSpeedSetpoint,
                (rearLeftSpeedSetpoint - self.m_prevSpeeds.rearLeft) / dt,
            )
            frontRightFeedforward = self.feedforward.calculate(
                frontRightSpeedSetpoint,
                (frontRightSpeedSetpoint - self.m_prevSpeeds.frontRight) / dt,
            )
            rearRightFeedforward = self.feedforward.calculate(
                rearRightSpeedSetpoint,
                (rearRightSpeedSetpoint - self.m_prevSpeeds.rearRight) / dt,
            )
            frontLeftOutput = frontLeftFeedforward + self.frontLeftController.calculate(
                self.currentWheelSpeeds().frontLeft,
                frontLeftSpeedSetpoint,
            )
            rearLeftOutput = rearLeftFeedforward + self.rearLeftController.calculate(
                self.currentWheelSpeeds().rearLeft,
                rearLeftSpeedSetpoint,
            )
            frontRightOutput = (
                frontRightFeedforward
                + self.frontRightController.calculate(
                    self.currentWheelSpeeds().frontRight,
                    frontRightSpeedSetpoint,
                )
            )
            rearRightOutput = rearRightFeedforward + self.rearRightController.calculate(
                self.currentWheelSpeeds().rearRight,
                rearRightSpeedSetpoint,
            )
            self.outputConsumer(
                frontLeftOutput, frontRightOutput, rearLeftOutput, rearRightOutput
            )

        # Store current call information for next call
        self.prevTime = curTime
        self.m_prevSpeeds = targetWheelSpeeds

    def end(self, interrupted):
        self.timer.stop()

    def isFinished(self):
        return self.timer.hasElapsed(self.trajectory.totalTime())
