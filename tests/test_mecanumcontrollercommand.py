# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

from typing import TYPE_CHECKING, List
import math

import wpimath.controller as controller
import wpimath.trajectory as trajectory
import wpimath.geometry as geometry
import wpimath.kinematics as kinematics
from wpilib import Timer

from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

import pytest

import commands2


class MecanumControllerCommandTestDataFixtures:
    def __init__(self):
        self.timer = Timer()
        self.angle: geometry.Rotation2d = geometry.Rotation2d(0)

        # Track speeds and distances
        self.frontLeftSpeed = 0
        self.frontLeftDistance = 0
        self.rearLeftSpeed = 0
        self.rearLeftDistance = 0
        self.frontRightSpeed = 0
        self.frontRightDistance = 0
        self.rearRightSpeed = 0
        self.rearRightDistance = 0

        # Profile Controller and constraints
        trapProfileConstraints: trajectory.TrapezoidProfileRadians.Constraints = (
            trajectory.TrapezoidProfileRadians.Constraints(3 * math.pi, math.pi)
        )
        self.rotationController: controller.ProfiledPIDControllerRadians = (
            controller.ProfiledPIDControllerRadians(
                1.0, 0.0, 0.0, trapProfileConstraints
            )
        )

        # Chassis/Drivetrain constants
        self.kxTolerance = 1 / 12.0
        self.kyTolerance = 1 / 12.0
        self.kAngularTolerance = 1 / 12.0
        self.kWheelBase = 0.5
        self.kTrackWidth = 0.5

        self.command_kinematics: kinematics.MecanumDriveKinematics = (
            kinematics.MecanumDriveKinematics(
                geometry.Translation2d(self.kWheelBase / 2, self.kTrackWidth / 2),
                geometry.Translation2d(self.kWheelBase / 2, -self.kTrackWidth / 2),
                geometry.Translation2d(self.kWheelBase / 2, self.kTrackWidth / 2),
                geometry.Translation2d(self.kWheelBase / 2, -self.kTrackWidth / 2),
            )
        )

        self.command_odometry: kinematics.MecanumDriveOdometry = (
            kinematics.MecanumDriveOdometry(
                self.command_kinematics,
                geometry.Rotation2d(0),
                kinematics.MecanumDriveWheelPositions(),
                geometry.Pose2d(0, 0, geometry.Rotation2d(0)),
            )
        )

    def setWheelSpeeds(self, wheelSpeeds: kinematics.MecanumDriveWheelSpeeds) -> None:
        self.frontLeftSpeed = wheelSpeeds.frontLeft
        self.rearLeftSpeed = wheelSpeeds.rearLeft
        self.frontRightSpeed = wheelSpeeds.frontRight
        self.rearRightSpeed = wheelSpeeds.rearRight

    def getCurrentWheelDistances(self) -> kinematics.MecanumDriveWheelPositions:
        positions = kinematics.MecanumDriveWheelPositions()
        positions.frontLeft = self.frontLeftDistance
        positions.frontRight = self.frontRightDistance
        positions.rearLeft = self.rearLeftDistance
        positions.rearRight = self.rearRightDistance

        return positions

    def getRobotPose(self) -> geometry.Pose2d:
        self.command_odometry.update(self.angle, self.getCurrentWheelDistances())
        return self.command_odometry.getPose()


@pytest.fixture()
def get_mec_controller_data() -> MecanumControllerCommandTestDataFixtures:
    return MecanumControllerCommandTestDataFixtures()


def test_mecanumControllerCommand(
    scheduler: commands2.CommandScheduler, get_mec_controller_data
):
    with ManualSimTime() as sim:
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(1, 5, geometry.Rotation2d(3)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())

        fixture_data = get_mec_controller_data

        mecContCommand = commands2.MecanumControllerCommand(
            new_trajectory,
            fixture_data.getRobotPose,
            fixture_data.command_kinematics,
            controller.PIDController(0.6, 0, 0),
            controller.PIDController(0.6, 0, 0),
            fixture_data.rotationController,
            8.8,
            fixture_data.setWheelSpeeds,
            subsystem,
        )

        fixture_data.timer.restart()

        mecContCommand.initialize()

        while not mecContCommand.isFinished():
            mecContCommand.execute()
            fixture_data.angle = new_trajectory.sample(
                fixture_data.timer.get()
            ).pose.rotation()

            fixture_data.frontLeftDistance += fixture_data.frontLeftSpeed * 0.005
            fixture_data.rearLeftDistance += fixture_data.rearLeftSpeed * 0.005
            fixture_data.frontRightDistance += fixture_data.frontRightSpeed * 0.005
            fixture_data.rearRightDistance += fixture_data.rearRightSpeed * 0.005

            sim.step(0.005)

        fixture_data.timer.stop()
        mecContCommand.end(True)

        assert end_state.pose.X() == pytest.approx(
            fixture_data.getRobotPose().X(), fixture_data.kxTolerance
        )
        assert end_state.pose.Y() == pytest.approx(
            fixture_data.getRobotPose().Y(), fixture_data.kyTolerance
        )
        assert end_state.pose.rotation().radians() == pytest.approx(
            fixture_data.getRobotPose().rotation().radians(),
            fixture_data.kAngularTolerance,
        )
