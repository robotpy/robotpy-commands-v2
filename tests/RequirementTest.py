import unittest

from commands2 import Requirement, InterruptBehavior


class RequirementsTest(unittest.TestCase):
    def test_requirements(self):
        requirement = Requirement()
        self.assertFalse(requirement.is_required())
        self.assertEqual(0, requirement.requirement_level())

        gen = requirement.require()
        self.assertIsNotNone(gen, msg="Requiring an empty requirement should be possible!")
        gen.send(InterruptBehavior.CANCEL_SELF)

        self.assertRaises(StopIteration, lambda: gen.send(0),
                          # msg="Using the same require callable should fail!"
                          )

        # Ensure it's required
        self.assertTrue(requirement.is_required())
        self.assertEqual(1, requirement.requirement_level())

        gen = requirement.require()
        self.assertIsNotNone(gen, msg="Requiring an interruptible requirement should be possible!")

        gen.send(InterruptBehavior.CANCEL_INCOMING)

        # Ensure it's required
        self.assertTrue(requirement.is_required())
        self.assertEqual(2, requirement.requirement_level())

        gen = requirement.require()
        self.assertIsNone(gen, msg="Uninterruptible requirements should return None!")


if __name__ == '__main__':
    unittest.main()
