import unittest

from commands2.Command import Command, commandify
from tests.CommandTestBase import CommandTestBase, ValueHolderRequirement


@commandify()
def test_decorator_command(requirement: ValueHolderRequirement, increment):
    count = 0
    while count < 3:
        requirement.value += increment
        count += 1
        yield


class SchedulerTest(CommandTestBase):
    def test_schedule(self):
        req = ValueHolderRequirement()

        # print(test_decorator_command)
        cmd: Command = test_decorator_command(req, 12)
        self.assertIsInstance(cmd, Command)
        self.assertListEqual(list(cmd.requirements), [req])
        self.assertEqual(0, req.value)
        self.scheduler.schedule(cmd)
        self.assertEqual(12, req.value)
        self.scheduler.run()
        self.assertEqual(24, req.value)
        # Reschedule, see if count restarts
        self.scheduler.schedule(cmd)

        self.scheduler.run()
        self.assertEqual(36, req.value)
        # Command shouldn't be running anymore after 3 iterations
        self.scheduler.run()
        self.assertEqual(36, req.value)
        self.scheduler.run()

        # Reschedule, this time it should run again for 3 iterations
        self.scheduler.schedule(cmd)
        self.assertEqual(48, req.value)
        self.scheduler.run()
        self.assertEqual(60, req.value)
        self.scheduler.run()
        self.assertEqual(72, req.value)
        # Should end now
        self.scheduler.run()
        self.assertEqual(72, req.value)

    def test_cancel(self):
        req = ValueHolderRequirement()

        # print(test_decorator_command)
        cmd: Command = test_decorator_command(req, 12)
        self.assertIsInstance(cmd, Command)
        self.assertListEqual(list(cmd.requirements), [req])
        self.assertEqual(0, req.value)
        self.scheduler.schedule(cmd)
        self.assertTrue(self.scheduler.is_scheduled(cmd))
        self.assertEqual(12, req.value)
        self.scheduler.run()
        self.assertEqual(24, req.value)
        # Reschedule, see if count restarts
        self.scheduler.cancel(cmd)
        self.assertFalse(self.scheduler.is_scheduled(cmd))
        self.scheduler.run()
        # Command shouldn't be running anymore after 3 iterations
        self.assertEqual(24, req.value)

        # Reschedule, this time it should run again for 3 iterations
        self.scheduler.schedule(cmd)
        self.assertEqual(36, req.value)
        self.scheduler.run()
        self.assertEqual(48, req.value)
        self.scheduler.run()
        self.assertEqual(60, req.value)
        # Should end now
        self.scheduler.run()
        self.assertEqual(60, req.value)

    def test_requirement_detection(self):
        req1, req2 = ValueHolderRequirement(), ValueHolderRequirement()

        @commandify()
        def command(req1, req2, x):
            pass

        cmd = command(req1, req2, 10)
        self.assertIsInstance(cmd, Command)
        self.assertSetEqual({req1, req2}, cmd.requirements)


if __name__ == '__main__':
    unittest.main()
