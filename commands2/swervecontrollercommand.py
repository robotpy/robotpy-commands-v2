# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
from __future__ import annotations
from typing import Callable, Optional, Union

from wpimath.controller import (
    HolonomicDriveController,
    PIDController,
    ProfiledPIDControllerRadians,
)
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.kinematics import (
    SwerveDrive2Kinematics,
    SwerveDrive3Kinematics,
    SwerveDrive4Kinematics,
    SwerveDrive6Kinematics,
    SwerveModuleState,
)
from wpimath.trajectory import Trajectory
from wpilib import Timer

from .command import Command
from .subsystem import Subsystem


class SwerveControllerCommand(Command):
    """
    A command that uses two PID controllers (PIDController) and a ProfiledPIDController
    (ProfiledPIDController) to follow a trajectory (Trajectory) with a swerve drive.

    This command outputs the raw desired Swerve Module States (SwerveModuleState) in an
    array. The desired wheel and module rotation velocities should be taken from those and used in
    velocity PIDs.

    The robot angle controller does not follow the angle given by the trajectory but rather goes
    to the angle given in the final state of the trajectory.

    This class is provided by the NewCommands VendorDep
    """

    def __init__(
        self,
        trajectory: Trajectory,
        pose: Callable[[], Pose2d],
        kinematics: Union[
            SwerveDrive2Kinematics,
            SwerveDrive3Kinematics,
            SwerveDrive4Kinematics,
            SwerveDrive6Kinematics,
        ],
        outputModuleStates: Callable[[SwerveModuleState], None],
        *requirements: Subsystem,
        controller: Optional[HolonomicDriveController] = None,
        xController: Optional[PIDController] = None,
        yController: Optional[PIDController] = None,
        thetaController: Optional[ProfiledPIDControllerRadians] = None,
        desiredRotation: Optional[Callable[[], Rotation2d]] = None,
    ):
        """Constructs a new SwerveControllerCommand that when executed will follow the provided
        trajectory. This command will not return output voltages but rather raw module states from the
        position controllers which need to be put into a velocity PID.

        Note: The controllers will *not* set the outputVolts to zero upon completion of the path.
        This is left to the user since it is not appropriate for paths with nonstationary endstates.

        Note 2: The final rotation of the robot will be set to the rotation of the final pose in the
        trajectory. The robot will not follow the rotations from the poses at each timestep. If
        alternate rotation behavior is desired, the other constructor with a supplier for rotation
        should be used.

        Note 3: The constructor requires 5 arguments: Trajectory, Pose, Kinematics, OutputConsumer, and
        the Subsystem. For functionality, a sixth component is required: `HolonomicDriveController`. To satisfy
        this sixth requirement, the caller can pass in a `HolonomicDriveController` object, or pass in the
        combination of X, Y, Theta PID controllers with a Supplier of `Rotation2d` objects representing the
        desired rotation at the end of the trajectory. If the caller doesn't supply a constructed controller
        or PID controllers such that a `HolonomicDriveController` can be constructed a `RuntimeError` will
        be raised.

        :param trajectory:         The trajectory to follow.
        :param pose:               A function that supplies the robot pose - use one of the odometry classes to
                                   provide this.
        :param kinematics:         The kinematics for the robot drivetrain. Can be kinematics for 2/3/4/6
                                   SwerveKinematics.
        :param outputModuleStates: The raw output module states from the position controllers.
        :param requirements:       The subsystems to require.

        Optional Requirements
        :param controller:          HolonomicDriveController for the drivetrain
        :param xController:         Trajectory Tracker PID controller for the robot's x position
        :param yController:         Trajectory Tracker PID controller for the robot's y position
        :param thetaController:     Trajectory Tracker PID controller for the angle for the robot
        :param desiredRotation:     The angle that the drivetrain should be facing. This is sampled at
                                    each time step
        """
        super().__init__()
        self._trajectory = trajectory
        self._pose = pose
        self._kinematics = kinematics
        self._outputModuleStates = outputModuleStates

        # Parse the controller parameters combination. If the controller is passed in constructed,
        # ignore the PID controllers. If it's None, parse them.
        if controller is not None:
            self._controller = controller
        else:
            # Verify the PID controller combination
            if (xController and yController and thetaController) is None:
                raise RuntimeError(
                    f"Failed to instantiate the Swerve2ControllerCommand: Could not create HolonomicDriveController from PID requirements"
                )

            # re-type variables to fix MyPy error:
            # Argument 1 to "HolonomicDriveController" has incompatible type "PIDController | None"; expected "PIDController"  [arg-type]
            x: PIDController = xController
            y: PIDController = yController
            theta: ProfiledPIDControllerRadians = thetaController
            self._controller = HolonomicDriveController( x, y, theta )

        # If the desired rotation isn't provided, just take the final rotation from the trajectory
        if desiredRotation is not None:
            self._desiredRotation = desiredRotation
        else:
            self._desiredRotation = self._trajectory.states()[-1].pose.rotation
        self.addRequirements(*requirements)
        self._timer = Timer()

    def initialize(self):
        self._timer.restart()

    def execute(self):
        curTime = self._timer.get()
        desiredState = self._trajectory.sample(curTime)

        targetChassisSpeeds = self._controller.calculate(
            self._pose(), desiredState, self._desiredRotation()
        )
        targetModuleStates = self._kinematics.toSwerveModuleStates(targetChassisSpeeds)

        self._outputModuleStates(targetModuleStates)

    def end(self, interrupted):
        self._timer.stop()

    def isFinished(self):
        return self._timer.hasElapsed(self._trajectory.totalTime())
