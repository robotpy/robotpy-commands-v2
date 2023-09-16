// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#include "frc2/command/PIDSubsystem.h"

#include <utility>

using namespace frc2;

PIDSubsystem::PIDSubsystem(frc::PIDController controller,
                           double initialPosition)
    : m_controller{std::move(controller)} {
  SetSetpoint(initialPosition);
  AddChild("PID Controller", &m_controller);
}

void PIDSubsystem::Periodic() {
  if (m_enabled) {
    UseOutput(m_controller.Calculate(GetMeasurement()), GetSetpoint());
  }
}

void PIDSubsystem::SetSetpoint(double setpoint) {
  m_controller.SetSetpoint(setpoint);
}

double PIDSubsystem::GetSetpoint() const {
  return m_controller.GetSetpoint();
}

void PIDSubsystem::Enable() {
  m_controller.Reset();
  m_enabled = true;
}

void PIDSubsystem::Disable() {
  UseOutput(0, 0);
  m_enabled = false;
}

bool PIDSubsystem::IsEnabled() {
  return m_enabled;
}

frc::PIDController& PIDSubsystem::GetController() {
  return m_controller;
}
