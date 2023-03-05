import unittest

from commands2.Commands import *
from tests.CommandTestBase import CommandTestBase, ValueHolderRequirement


class CommandsTest(CommandTestBase):
    def test_none(self):
        cmd = none()
        self.assertIsInstance(cmd, Command)
        self.scheduler.schedule(cmd)
        # Should end immediately
        self.assertFalse(self.scheduler.is_scheduled(cmd))

    def test_run_once(self):
        req = ValueHolderRequirement()

        cmd = run_once(lambda: req.set_value(req.value + 1), {req})

        self.assertIsInstance(cmd, Command)
        self.scheduler.schedule(cmd)
        # Should end immediately
        self.assertEqual(1, req.value)
        self.assertFalse(self.scheduler.is_scheduled(cmd))
        self.scheduler.run()
        self.assertFalse(self.scheduler.is_scheduled(cmd))
        self.assertEqual(1, req.value)


if __name__ == '__main__':
    unittest.main()
