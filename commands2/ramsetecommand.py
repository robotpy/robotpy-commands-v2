# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
from __future__ import annotations

from typing import Callable, Union, Optional, Tuple
from typing_extensions import overload
from overtake import overtake
from wpimath.controller import (
    PIDController,
    RamseteController,
    SimpleMotorFeedforwardMeters,
)
from wpimath.geometry import Pose2d
from wpimath.kinematics import (
    ChassisSpeeds,
    DifferentialDriveKinematics,
    DifferentialDriveWheelSpeeds,
)
from wpimath.trajectory import Trajectory
from wpimath import units as units
from wpiutil import SendableBuilder
from wpilib import Timer


from .command import Command
from .subsystem import Subsystem


class RamseteCommand(Command):
    """
    A command that uses a RAMSETE controller (RamseteController) to follow a trajectory
    (Trajectory) with a differential drive.

    The command handles trajectory-following, PID calculations, and feedforwards internally. This
    is intended to be a more-or-less "complete solution" that can be used by teams without a great
    deal of controls expertise.

    Advanced teams seeking more flexibility (for example, those who wish to use the onboard PID
    functionality of a "smart" motor controller) may use the secondary constructor that omits the PID
    and feedforward functionality, returning only the raw wheel speeds from the RAMSETE controller.
    """

    @overload
    def __init__(
        self,
        trajectory: Trajectory,
        pose: Callable[[], Pose2d],
        controller: RamseteController,
        kinematics: DifferentialDriveKinematics,
        requirements: Tuple[Subsystem],
        output: Callable[[float, float], None],
    ):
        """Constructs a new RamseteCommand that, when executed, will follow the provided trajectory. PID
        control and feedforward are handled internally, and outputs are scaled -12 to 12 representing
        units of volts.

        Note: The controller will *not* set the outputVolts to zero upon completion of the path -
        this is left to the user, since it is not appropriate for paths with nonstationary endstates.

        :param trajectory:      The trajectory to follow.
        :param pose:            A function that supplies the robot pose - use one of the odometry classes to
                                provide this.
        :param controller:      The RAMSETE controller used to follow the trajectory.
        :param kinematics:      The kinematics for the robot drivetrain.
        :param requirements:    The subsystems to require.
        :param output        A function that consumes the computed left and right outputs in `units.meters_per_second`
        """
        super().__init__()

        self._timer = Timer()
        self._trajectory = trajectory
        self._pose = pose
        self._follower = controller
        self._kinematics = kinematics
        self._output = output
        self._usePID = False
        # All the parameter checks pass, inform scheduler.  Type ignoring is set explictitly for the linter because this
        # implementation declares the tuple explicitly, whereas the general implementations use the unpack operator (*)
        # to pass the requirements to the scheduler.
        self.addRequirements(requirements)  # type: ignore

    @overload
    def __init__(
        self,
        trajectory: Trajectory,
        pose: Callable[[], Pose2d],
        controller: RamseteController,
        kinematics: DifferentialDriveKinematics,
        requirements: Tuple[Subsystem],
        output: Callable[[float, float], None],
        feedforward: SimpleMotorFeedforwardMeters,
        leftController: PIDController,
        rightController: PIDController,
        wheelSpeeds: Callable[[], DifferentialDriveWheelSpeeds],
    ):
        """Constructs a new RamseteCommand that, when executed, will follow the provided trajectory. PID
        control and feedforward are handled internally, and outputs are scaled -12 to 12 representing
        units of volts.

        Note: The controller will *not* set the outputVolts to zero upon completion of the path -
        this is left to the user, since it is not appropriate for paths with nonstationary endstates.

        :param trajectory:      The trajectory to follow.
        :param pose:            A function that supplies the robot pose - use one of the odometry classes to
                                provide this.
        :param controller:      The RAMSETE controller used to follow the trajectory.
        :param kinematics:      The kinematics for the robot drivetrain.
        :param requirements:    The subsystems to require.
        :param output      A function that consumes the computed left and right outputs in `units.volts`
        :param feedforward      The feedforward to use for the drive
        :param leftController:  The PIDController for the left side of the robot drive.
        :param rightController: The PIDController for the right side of the robot drive.
        :param wheelSpeeds:     A function that supplies the speeds of the left and right sides of the robot
                                drive.
        """
        super().__init__()

        self._timer = Timer()

        # Store all the requirements that are required
        self._trajectory = trajectory
        self._pose = pose
        self._follower = controller
        self._kinematics = kinematics
        self._output = output
        self._leftController = leftController
        self._rightController = rightController
        self._wheelspeeds = wheelSpeeds
        self._feedforward = feedforward
        self._prevSpeeds = DifferentialDriveWheelSpeeds()
        self._prevTime = -1.0
        self._usePID = True
        # All the parameter checks pass, inform scheduler.  Type ignoring is set explictitly for the linter because this
        # implementation declares the tuple explicitly, whereas the general implementations use the unpack operator (*)
        # to pass the requirements to the scheduler.
        self.addRequirements(requirements)  # type: ignore

    @overtake(runtime_type_checker="beartype")
    def __init__(
        self,
        *,
        trajectory: Trajectory,
        pose: Callable[[], Pose2d],
        controller: RamseteController,
        kinematics: DifferentialDriveKinematics,
        requirements: Tuple[Subsystem],
        output: Callable[[float, float], None],
        feedforward: Optional[SimpleMotorFeedforwardMeters] = None,
        leftController: Optional[PIDController] = None,
        rightController: Optional[PIDController] = None,
        wheelSpeeds: Optional[Callable[[], DifferentialDriveWheelSpeeds]] = None,
    ):
        ...

    def initialize(self):
        self._prevTime = -1
        initial_state = self._trajectory.sample(0)
        self._prevSpeeds = self._kinematics.toWheelSpeeds(
            ChassisSpeeds(
                initial_state.velocity,
                0,
                initial_state.curvature * initial_state.velocity,
            )
        )
        self._timer.restart()
        if self._usePID:
            self._leftController.reset()
            self._rightController.reset()

    def execute(self):
        curTime = self._timer.get()
        dt = curTime - self._prevTime

        if self._prevTime < 0:
            self._output(0.0, 0.0)
            self._prevTime = curTime
            return

        targetWheelSpeeds = self._kinematics.toWheelSpeeds(
            self._follower.calculate(self._pose(), self._trajectory.sample(curTime))
        )

        leftSpeedSetpoint = targetWheelSpeeds.left
        rightSpeedSetpoint = targetWheelSpeeds.right

        if self._usePID:
            leftFeedforward = self._feedforward.calculate(
                leftSpeedSetpoint, (leftSpeedSetpoint - self._prevSpeeds.left) / dt
            )

            rightFeedforward = self._feedforward.calculate(
                rightSpeedSetpoint,
                (rightSpeedSetpoint - self._prevSpeeds.right) / dt,
            )

            leftOutput = leftFeedforward + self._leftController.calculate(
                self._wheelspeeds().left, leftSpeedSetpoint
            )

            rightOutput = rightFeedforward + self._rightController.calculate(
                self._wheelspeeds().right, rightSpeedSetpoint
            )
            self._output(leftOutput, rightOutput)
        else:
            leftOutput = leftSpeedSetpoint
            rightOutput = rightSpeedSetpoint
            self._output(leftOutput, rightOutput)

        self._prevSpeeds = targetWheelSpeeds
        self._prevTime = curTime

    def end(self, interrupted: bool):
        self._timer.stop()

        if interrupted:
            self._output(0.0, 0.0)

    def isFinished(self):
        return self._timer.hasElapsed(self._trajectory.totalTime())

    def initSendable(self, builder: SendableBuilder):
        super().initSendable(builder)
        builder.addDoubleProperty(
            "leftVelocity", lambda: self._prevSpeeds.left, lambda *float: None
        )
        builder.addDoubleProperty(
            "rightVelocity", lambda: self._prevSpeeds.right, lambda *float: None
        )
