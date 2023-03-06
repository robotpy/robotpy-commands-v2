import unittest

from commands2 import Requirement
from commands2.scheduler import CommandScheduler


class ValueHolderRequirement(Requirement):
    value = 0

    def set_value(self, value):
        self.value = value

    def increment(self):
        self.value += 1


class ConditionHolderRequirement(Requirement):
    cond: bool

    def __init__(self, cond: bool = False) -> None:
        super().__init__()
        self.cond = cond

    def get_condition(self) -> bool:
        return self.cond

    def set_true(self):
        self.cond = True


class CommandTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.scheduler = CommandScheduler()

    def tearDown(self) -> None:
        self.scheduler = None
