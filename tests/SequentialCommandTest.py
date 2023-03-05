import unittest

from commands2.Commands import *
from tests.CommandTestBase import CommandTestBase, ValueHolderRequirement


class SequentialCommandTest(CommandTestBase):
    def test_sequence(self):
        req1 = ValueHolderRequirement()
        req2 = ValueHolderRequirement()

        def increment_command(requirement: ValueHolderRequirement, increment: int):
            count = 0
            while count < 3:
                requirement.value += increment
                count += 1
                yield

        cmd1: Command = commandify(lambda interrupted, *args, **kwargs: req1.set_value(-3), {req1}) \
            (increment_command)(req1, 10)
        cmd2 = run_once(lambda: req1.set_value(0), {req1})
        cmd3: Command = commandify(lambda interrupted, *args, **kwargs: req2.set_value(3), {req2}) \
            (increment_command)(req2, -5)

        cmd = sequence(cmd1, cmd2, cmd3)
        self.assertSetEqual({req1, req2}, cmd.requirements)

        self.scheduler.schedule(cmd)
        self.assertEqual(10, req1.value)
        self.assertEqual(0, req2.value)

        self.scheduler.run()
        self.assertEqual(20, req1.value)
        self.assertEqual(0, req2.value)

        self.scheduler.cancel(cmd)
        self.assertEqual(-3, req1.value)
        self.assertEqual(0, req2.value)

        # Schedule again

        self.scheduler.schedule(cmd)
        self.assertEqual(7, req1.value)
        self.assertEqual(0, req2.value)

        self.scheduler.run()
        self.assertEqual(17, req1.value)
        self.assertEqual(0, req2.value)

        self.scheduler.run()
        self.assertEqual(27, req1.value)
        self.assertEqual(0, req2.value)

        self.scheduler.run()
        self.assertEqual(0, req1.value)
        self.assertEqual(-5, req2.value)

        self.scheduler.run()
        self.assertEqual(0, req1.value)
        self.assertEqual(-10, req2.value)

        self.scheduler.cancel(cmd)
        self.assertEqual(0, req1.value)
        self.assertEqual(3, req2.value)


if __name__ == '__main__':
    unittest.main()
