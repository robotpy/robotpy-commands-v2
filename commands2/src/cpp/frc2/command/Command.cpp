// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#include "frc2/command/Command.h"

#include <wpi/sendable/SendableBuilder.h>
#include <wpi/sendable/SendableRegistry.h>

#include "frc2/command/CommandHelper.h"
#include "frc2/command/CommandScheduler.h"
#include "frc2/command/ConditionalCommand.h"
#include "frc2/command/InstantCommand.h"
#include "frc2/command/ParallelCommandGroup.h"
#include "frc2/command/ParallelDeadlineGroup.h"
#include "frc2/command/ParallelRaceGroup.h"
#include "frc2/command/RepeatCommand.h"
#include "frc2/command/SequentialCommandGroup.h"
#include "frc2/command/WaitCommand.h"
#include "frc2/command/WaitUntilCommand.h"
#include "frc2/command/WrapperCommand.h"

using namespace frc2;

Command::Command() {
  wpi::SendableRegistry::Add(this, GetTypeName(*this));
}

Command::~Command() {
  CommandScheduler::GetInstance().Cancel(this);
}

Command& Command::operator=(const Command& rhs) {
  m_isComposed = false;
  return *this;
}

void Command::Initialize() {}
void Command::Execute() {}
void Command::End(bool interrupted) {}

wpi::SmallSet<Subsystem*, 4> Command::GetRequirements() const {
  return m_requirements;
}

void Command::AddRequirements(Requirements requirements) {
  m_requirements.insert(requirements.begin(), requirements.end());
}

void Command::AddRequirements(wpi::SmallSet<Subsystem*, 4> requirements) {
  m_requirements.insert(requirements.begin(), requirements.end());
}

void Command::AddRequirements(Subsystem* requirement) {
  m_requirements.insert(requirement);
}

void Command::SetName(std::string_view name) {
  wpi::SendableRegistry::SetName(this, name);
}

std::string Command::GetName() const {
  return wpi::SendableRegistry::GetName(this);
}

std::string Command::GetSubsystem() const {
  return wpi::SendableRegistry::GetSubsystem(this);
}

void Command::SetSubsystem(std::string_view subsystem) {
  wpi::SendableRegistry::SetSubsystem(this, subsystem);
}

CommandPtr Command::WithTimeout(units::second_t duration) && {
  return std::move(*this).ToPtr().WithTimeout(duration);
}

CommandPtr Command::Until(std::function<bool()> condition) && {
  return std::move(*this).ToPtr().Until(std::move(condition));
}

CommandPtr Command::OnlyWhile(std::function<bool()> condition) && {
  return std::move(*this).ToPtr().OnlyWhile(std::move(condition));
}

CommandPtr Command::IgnoringDisable(bool doesRunWhenDisabled) && {
  return std::move(*this).ToPtr().IgnoringDisable(doesRunWhenDisabled);
}

CommandPtr Command::WithInterruptBehavior(
    InterruptionBehavior interruptBehavior) && {
  return std::move(*this).ToPtr().WithInterruptBehavior(interruptBehavior);
}

CommandPtr Command::BeforeStarting(std::function<void()> toRun,
                                   Requirements requirements) && {
  return std::move(*this).ToPtr().BeforeStarting(std::move(toRun),
                                                 requirements);
}

CommandPtr Command::AndThen(std::function<void()> toRun,
                            Requirements requirements) && {
  return std::move(*this).ToPtr().AndThen(std::move(toRun), requirements);
}

CommandPtr Command::Repeatedly() && {
  return std::move(*this).ToPtr().Repeatedly();
}

CommandPtr Command::AsProxy() && {
  return std::move(*this).ToPtr().AsProxy();
}

CommandPtr Command::Unless(std::function<bool()> condition) && {
  return std::move(*this).ToPtr().Unless(std::move(condition));
}

CommandPtr Command::OnlyIf(std::function<bool()> condition) && {
  return std::move(*this).ToPtr().OnlyIf(std::move(condition));
}

CommandPtr Command::FinallyDo(std::function<void(bool)> end) && {
  return std::move(*this).ToPtr().FinallyDo(std::move(end));
}

CommandPtr Command::HandleInterrupt(std::function<void(void)> handler) && {
  return std::move(*this).ToPtr().HandleInterrupt(std::move(handler));
}

CommandPtr Command::WithName(std::string_view name) && {
  return std::move(*this).ToPtr().WithName(name);
}

void Command::Schedule() {
  CommandScheduler::GetInstance().Schedule(this);
}

void Command::Cancel() {
  CommandScheduler::GetInstance().Cancel(this);
}

bool Command::IsScheduled() const {
  return CommandScheduler::GetInstance().IsScheduled(this);
}

bool Command::HasRequirement(Subsystem* requirement) const {
  bool hasRequirement = false;
  for (auto&& subsystem : GetRequirements()) {
    hasRequirement |= requirement == subsystem;
  }
  return hasRequirement;
}

bool Command::IsComposed() const {
  return m_isComposed;
}

void Command::SetComposed(bool isComposed) {
  m_isComposed = isComposed;
}

void Command::InitSendable(wpi::SendableBuilder& builder) {
  builder.SetSmartDashboardType("Command");
  builder.AddStringProperty(
      ".name", [this] { return GetName(); }, nullptr);
  builder.AddBooleanProperty(
      "running", [this] { return IsScheduled(); },
      [this](bool value) {
        bool isScheduled = IsScheduled();
        if (value && !isScheduled) {
          Schedule();
        } else if (!value && isScheduled) {
          Cancel();
        }
      });
  builder.AddBooleanProperty(
      ".isParented", [this] { return IsComposed(); }, nullptr);
  builder.AddStringProperty(
      "interruptBehavior",
      [this] {
        switch (GetInterruptionBehavior()) {
          case Command::InterruptionBehavior::kCancelIncoming:
            return "kCancelIncoming";
          case Command::InterruptionBehavior::kCancelSelf:
            return "kCancelSelf";
          default:
            return "Invalid";
        }
      },
      nullptr);
  builder.AddBooleanProperty(
      "runsWhenDisabled", [this] { return RunsWhenDisabled(); }, nullptr);
}

namespace frc2 {
bool RequirementsDisjoint(Command* first, Command* second) {
  bool disjoint = true;
  auto&& requirements = second->GetRequirements();
  for (auto&& requirement : first->GetRequirements()) {
    disjoint &= requirements.find(requirement) == requirements.end();
  }
  return disjoint;
}
}  // namespace frc2
