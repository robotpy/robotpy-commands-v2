// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#include "frc2/command/ProxyCommand.h"

#include <wpi/sendable/SendableBuilder.h>

using namespace frc2;

ProxyCommand::ProxyCommand(wpi::unique_function<Command*()> supplier)
    : m_supplier(std::move(supplier)) {}

ProxyCommand::ProxyCommand(wpi::unique_function<CommandPtr()> supplier)
    : ProxyCommand([supplier = std::move(supplier),
                    holder = std::optional<CommandPtr>{}]() mutable {
        holder = supplier();
        return holder->get();
      }) {}

ProxyCommand::ProxyCommand(Command* command)
    : ProxyCommand([command] { return command; }) {
  SetName(std::string{"Proxy("}.append(command->GetName()).append(")"));
}

ProxyCommand::ProxyCommand(std::unique_ptr<Command> command) {
  SetName(std::string{"Proxy("}.append(command->GetName()).append(")"));
  m_supplier = [command = std::move(command)] { return command.get(); };
}

void ProxyCommand::Initialize() {
  m_command = m_supplier();
  m_command->Schedule();
}

void ProxyCommand::End(bool interrupted) {
  if (interrupted) {
    m_command->Cancel();
  }
  m_command = nullptr;
}

bool ProxyCommand::IsFinished() {
  // because we're between `initialize` and `end`, `m_command` is necessarily
  // not null but if called otherwise and m_command is null, it's UB, so we can
  // do whatever we want -- like return true.
  return m_command == nullptr || !m_command->IsScheduled();
}

void ProxyCommand::InitSendable(wpi::SendableBuilder& builder) {
  Command::InitSendable(builder);
  builder.AddStringProperty(
      "proxied",
      [this] {
        if (m_command) {
          return m_command->GetName();
        } else {
          return std::string{"null"};
        }
      },
      nullptr);
}
