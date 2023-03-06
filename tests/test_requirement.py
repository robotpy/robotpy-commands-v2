import unittest

import pytest

from commands2 import Requirement, InterruptBehavior, CommandScheduler


def test_requirements(scheduler: CommandScheduler):
    requirement = Requirement()
    assert not requirement.is_required()
    assert 0 == requirement.requirement_level()

    gen = requirement.require()
    assert gen is not None
    gen.send(InterruptBehavior.CANCEL_SELF)

    with pytest.raises(StopIteration):
        gen.send(0)

    # Ensure it's required
    assert requirement.is_required()
    assert 1 == requirement.requirement_level()

    gen = requirement.require()
    assert gen is not None

    gen.send(InterruptBehavior.CANCEL_INCOMING)

    # Ensure it's required
    assert requirement.is_required()
    assert 2 == requirement.requirement_level()

    gen = requirement.require()
    assert gen is None
