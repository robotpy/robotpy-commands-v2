from typing import Callable, Set

from commands2.command import commandify, Command
from commands2.requirement import Requirement


@commandify(runs_when_disabled=True, requirements=set({}))
def nothing() -> Command:
    pass


@commandify(runs_when_disabled=True, requirements=set({}))
def print_cmd(msg: str, printer: Callable[[str], None] = print) -> Command:
    printer(msg)


def run_once(action: Callable[[], None], requirements: Set[Requirement] = None) -> Command:
    @commandify(requirements=requirements if requirements is not None else {})
    def run_once_impl():
        action()

    return run_once_impl()


def run(action: Callable[[], None], requirements: Set[Requirement] = None) -> Command:
    @commandify(requirements=requirements if requirements is not None else {})
    def run_impl():
        while True:
            yield
            action()

    return run_impl()
