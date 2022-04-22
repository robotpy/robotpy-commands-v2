
#include "helpers.h"

std::vector<std::shared_ptr<frc2::Command>> pyargs2cmdList(py::args cmds) {
  std::vector<std::shared_ptr<frc2::Command>> commands;
  for (auto cmd : cmds) {
    commands.emplace_back(py::cast<std::shared_ptr<frc2::Command>>(cmd));
  }
  return commands;
}

std::vector<std::shared_ptr<frc2::Subsystem>> pyargs2SharedSubsystemList(py::args subs) {
  std::vector<std::shared_ptr<frc2::Subsystem>> subsystems;
  for (auto sub : subs) {
    subsystems.emplace_back(py::cast<std::shared_ptr<frc2::Subsystem>>(sub));
  }
  return subsystems;
}

std::vector<frc2::Subsystem*> pyargs2SubsystemList(py::args subs) {
  std::vector<frc2::Subsystem*> subsystems;
  for (auto sub : subs) {
    subsystems.emplace_back(py::cast<frc2::Subsystem*>(sub));
  }
  return subsystems;
}

CommandIterator::CommandIterator(std::shared_ptr<frc2::Command> cmd) : cmd(cmd) {}
std::shared_ptr<frc2::Command> CommandIterator::operator*() const { return cmd; }
CommandIterator& CommandIterator::operator++() {
  if (!called_initialize) {
    cmd->Initialize();
    called_initialize = true;
    return *this;
  }
  cmd->Execute();
  return *this;
}

bool operator==(const CommandIterator& it, const CommandIteratorSentinel&) {
  return it.called_initialize && it.cmd->IsFinished();
}
