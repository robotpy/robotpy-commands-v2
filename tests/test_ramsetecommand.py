# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.

from typing import TYPE_CHECKING, List
import math

import wpimath.controller as controller
import wpimath.trajectory as trajectory
import wpimath.trajectory.constraint as constraints
import wpimath.geometry as geometry
import wpimath.kinematics as kinematics
import wpimath.units as units
from wpilib import Timer

from util import *  # type: ignore

if TYPE_CHECKING:
    from .util import *

import pytest

import commands2


class RamseteCommandTestDataFixtures:
    def __init__(self):
        self.timer = Timer()
        self.angle: geometry.Rotation2d = geometry.Rotation2d(0)

        # Track speeds and distances
        self.leftSpeed = 0
        self.leftDistance = 0
        self.rightSpeed = 0
        self.rightDistance = 0

        # Chassis/Drivetrain constants
        self.kxTolerance = 6.0 / 12.0
        self.kyTolerance = 6.0 / 12.0
        self.kWheelBase = 0.5
        self.kTrackWidth = 0.5
        self.kWheelDiameterMeters = 0.1524
        self.kRamseteB = 2.0
        self.kRamseteZeta = 0.7
        self.ksVolts = 0.22
        self.kvVoltSecondsPerMeter = 1.98
        self.kaVoltSecondsSquaredPerMeter = 0.2
        self.kPDriveVel = 8.5
        self.kMaxMetersPerSecond = 3.0
        self.kMaxAccelerationMetersPerSecondSquared = 1.0
        self.kEncoderCPR = 1024
        self.kEncoderDistancePerPulse = (
            self.kWheelDiameterMeters * math.pi
        ) / self.kEncoderCPR

        self.command_kinematics: kinematics.DifferentialDriveKinematics = (
            kinematics.DifferentialDriveKinematics(self.kTrackWidth)
        )

        self.command_voltage_constraint: constraints.DifferentialDriveVoltageConstraint = constraints.DifferentialDriveVoltageConstraint(
            controller.SimpleMotorFeedforwardMeters(
                self.ksVolts,
                self.kvVoltSecondsPerMeter,
                self.kaVoltSecondsSquaredPerMeter,
            ),
            self.command_kinematics,
            10,
        )

        self.command_odometry: kinematics.DifferentialDriveOdometry = (
            kinematics.DifferentialDriveOdometry(
                self.angle,
                self.leftDistance,
                self.rightDistance,
                geometry.Pose2d(0, 0, geometry.Rotation2d(0)),
            )
        )

    def setWheelSpeedsMPS(
        self, leftspeed: units.meters_per_second, rightspeed: units.meters_per_second
    ) -> None:
        self.leftSpeed = leftspeed
        self.rightSpeed = rightspeed

    def setWheelSpeedsVolts(
        self, leftVolts: units.volts, rightVolts: units.volts
    ) -> None:
        self.leftSpeed = leftVolts
        self.rightSpeed = rightVolts

    def getCurrentWheelDistances(self) -> kinematics.DifferentialDriveWheelPositions:
        positions = kinematics.DifferentialDriveWheelPositions()
        positions.right = self.rightDistance
        positions.left = self.leftDistance

        return positions

    def getRobotPose(self) -> geometry.Pose2d:
        positions = self.getCurrentWheelDistances()
        self.command_odometry.update(self.angle, positions.left, positions.right)
        return self.command_odometry.getPose()

    def getWheelSpeeds(self) -> kinematics.DifferentialDriveWheelSpeeds:
        return kinematics.DifferentialDriveWheelSpeeds(self.leftSpeed, self.rightSpeed)


@pytest.fixture()
def get_ramsete_command_data() -> RamseteCommandTestDataFixtures:
    return RamseteCommandTestDataFixtures()


def test_rameseteRaisesNoOutputRaises(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())

        with pytest.raises(Exception):
            command = commands2.RamseteCommand(
                new_trajectory,
                fixture_data.getRobotPose,
                controller.RamseteController(
                    fixture_data.kRamseteB, fixture_data.kRamseteZeta
                ),
                fixture_data.command_kinematics,
                subsystem,
            )


def test_rameseteRaisesOnlyFeedForward(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())
        feedforward_var: controller.SimpleMotorFeedforwardMeters = (
            controller.SimpleMotorFeedforwardMeters(
                fixture_data.ksVolts,
                fixture_data.kvVoltSecondsPerMeter,
                fixture_data.kaVoltSecondsSquaredPerMeter,
            )
        )

        with pytest.raises(Exception):
            command = commands2.RamseteCommand(
                new_trajectory,
                fixture_data.getRobotPose,
                controller.RamseteController(
                    fixture_data.kRamseteB, fixture_data.kRamseteZeta
                ),
                fixture_data.command_kinematics,
                subsystem,
                fixture_data.setWheelSpeedsMPS,
                feedforward_var,
            )


def test_rameseteRaisesFeedForwardAndLeft(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())
        feedforward_var: controller.SimpleMotorFeedforwardMeters = (
            controller.SimpleMotorFeedforwardMeters(
                fixture_data.ksVolts,
                fixture_data.kvVoltSecondsPerMeter,
                fixture_data.kaVoltSecondsSquaredPerMeter,
            )
        )
        left_pid: controller.PIDController = controller.PIDController(0.1, 0, 0)

        with pytest.raises(Exception):
            command = commands2.RamseteCommand(
                new_trajectory,
                fixture_data.getRobotPose,
                controller.RamseteController(
                    fixture_data.kRamseteB, fixture_data.kRamseteZeta
                ),
                fixture_data.command_kinematics,
                subsystem,
                fixture_data.setWheelSpeedsMPS,
                feedforward_var,
                left_pid,
            )


def test_rameseteRaisesFeedForwardRightAndLeft(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())
        feedforward_var: controller.SimpleMotorFeedforwardMeters = (
            controller.SimpleMotorFeedforwardMeters(
                fixture_data.ksVolts,
                fixture_data.kvVoltSecondsPerMeter,
                fixture_data.kaVoltSecondsSquaredPerMeter,
            )
        )
        left_pid: controller.PIDController = controller.PIDController(0.1, 0, 0)
        right_pid: controller.PIDController = controller.PIDController(0.1, 0, 0)

        with pytest.raises(Exception):
            command = commands2.RamseteCommand(
                new_trajectory,
                fixture_data.getRobotPose,
                controller.RamseteController(
                    fixture_data.kRamseteB, fixture_data.kRamseteZeta
                ),
                fixture_data.command_kinematics,
                subsystem,
                fixture_data.setWheelSpeedsMPS,
                feedforward_var,
                left_pid,
                right_pid,
            )


def test_ramseteCommandMPSReachesDestination(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())

        command = commands2.RamseteCommand(
            new_trajectory,
            fixture_data.getRobotPose,
            controller.RamseteController(
                fixture_data.kRamseteB, fixture_data.kRamseteZeta
            ),
            fixture_data.command_kinematics,
            subsystem,
            fixture_data.setWheelSpeedsMPS,
        )

        fixture_data.timer.restart()

        command.initialize()

        while not command.isFinished():
            command.execute()

            fixture_data.leftDistance += fixture_data.leftSpeed * 0.005
            fixture_data.rightDistance += fixture_data.rightSpeed * 0.005

            sim.step(0.005)

        fixture_data.timer.stop()
        command.end(True)

        assert end_state.pose.X() == pytest.approx(
            fixture_data.getRobotPose().X(), fixture_data.kxTolerance
        )
        assert end_state.pose.Y() == pytest.approx(
            fixture_data.getRobotPose().Y(), fixture_data.kyTolerance
        )


def test_ramseteCommandVoltsReachesDestination(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())

        command = commands2.RamseteCommand(
            new_trajectory,
            fixture_data.getRobotPose,
            controller.RamseteController(
                fixture_data.kRamseteB, fixture_data.kRamseteZeta
            ),
            fixture_data.command_kinematics,
            subsystem,
            fixture_data.setWheelSpeedsVolts,
        )

        fixture_data.timer.restart()

        command.initialize()

        while not command.isFinished():
            command.execute()

            fixture_data.leftDistance += fixture_data.leftSpeed * 0.005
            fixture_data.rightDistance += fixture_data.rightSpeed * 0.005

            sim.step(0.005)

        fixture_data.timer.stop()
        command.end(True)

        assert end_state.pose.X() == pytest.approx(
            fixture_data.getRobotPose().X(), fixture_data.kxTolerance
        )
        assert end_state.pose.Y() == pytest.approx(
            fixture_data.getRobotPose().Y(), fixture_data.kyTolerance
        )


def test_ramseteCommandPIDReachesDestination(
    scheduler: commands2.CommandScheduler, get_ramsete_command_data
):
    with ManualSimTime() as sim:
        fixture_data = get_ramsete_command_data
        subsystem = commands2.Subsystem()
        waypoints: List[geometry.Pose2d] = []
        waypoints.append(geometry.Pose2d(0, 0, geometry.Rotation2d(0)))
        waypoints.append(geometry.Pose2d(3, 0, geometry.Rotation2d(0)))
        traj_config: trajectory.TrajectoryConfig = trajectory.TrajectoryConfig(8.8, 0.1)
        traj_config.setKinematics(fixture_data.command_kinematics)
        traj_config.addConstraint(fixture_data.command_voltage_constraint)
        new_trajectory: trajectory.Trajectory = (
            trajectory.TrajectoryGenerator.generateTrajectory(waypoints, traj_config)
        )
        end_state = new_trajectory.sample(new_trajectory.totalTime())
        feedforward_var: controller.SimpleMotorFeedforwardMeters = (
            controller.SimpleMotorFeedforwardMeters(
                fixture_data.ksVolts,
                fixture_data.kvVoltSecondsPerMeter,
                fixture_data.kaVoltSecondsSquaredPerMeter,
            )
        )
        left_pid: controller.PIDController = controller.PIDController(0.001, 0, 0)
        rightt_pid: controller.PIDController = controller.PIDController(0.001, 0, 0)

        command = commands2.RamseteCommand(
            new_trajectory,
            fixture_data.getRobotPose,
            controller.RamseteController(
                fixture_data.kRamseteB, fixture_data.kRamseteZeta
            ),
            fixture_data.command_kinematics,
            subsystem,
            fixture_data.setWheelSpeedsVolts,
            feedforward_var,
            left_pid,
            rightt_pid,
            fixture_data.getWheelSpeeds,
        )

        fixture_data.timer.restart()

        command.initialize()

        while not command.isFinished():
            command.execute()

            fixture_data.leftDistance += fixture_data.leftSpeed * 0.005
            fixture_data.rightDistance += fixture_data.rightSpeed * 0.005

            sim.step(0.005)

        fixture_data.timer.stop()
        command.end(True)

        assert end_state.pose.X() == pytest.approx(
            fixture_data.getRobotPose().X(), fixture_data.kxTolerance
        )
        assert end_state.pose.Y() == pytest.approx(
            fixture_data.getRobotPose().Y(), fixture_data.kyTolerance
        )
