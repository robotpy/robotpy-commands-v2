import unittest

from commands2 import Requirement
from commands2.CommandScheduler import CommandScheduler


class ValueHolderRequirement(Requirement):
    value = 0

    def set_value(self, value):
        self.value = value


class CommandTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.scheduler = CommandScheduler()

    def tearDown(self) -> None:
        del self.scheduler





