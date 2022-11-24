import commands2
import commands2.button

from util import Counter
import pytest


class MyButton(commands2.button.Button):
    def __init__(self):
        super().__init__(self.isPressed)
        self.pressed = False

    def isPressed(self) -> bool:
        return self.pressed

    def setPressed(self, value: bool):
        self.pressed = value


def test_when_pressed_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()

    class state:
        pass

    state.executed = False

    def cmd1():
        state.executed = True
        return
        yield

    button.setPressed(False)
    button.whenPressed(cmd1())
    scheduler.run()

    assert not state.executed

    button.setPressed(True)
    scheduler.run()
    scheduler.run()

    assert state.executed


def test_when_released_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()

    class state:
        pass

    state.executed = False

    def cmd1():
        state.executed = True
        return
        yield

    button.setPressed(True)
    button.whenReleased(cmd1())
    scheduler.run()

    assert not state.executed

    button.setPressed(False)
    scheduler.run()
    scheduler.run()

    assert state.executed


@pytest.mark.xfail(strict=True)
def test_while_held_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()

    class state:
        pass

    state.executed = 0

    def cmd1():
        state.executed += 1
        return
        yield

    button.setPressed(False)
    button.whileHeld(cmd1())
    scheduler.run()

    assert not state.executed

    button.setPressed(True)
    scheduler.run()
    scheduler.run()
    assert state.executed == 2

    button.setPressed(False)
    scheduler.run()

    assert state.executed == 2


def test_when_held_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()

    class state:
        pass

    state.executed = 0

    def cmd1():
        while True:
            state.executed += 1
            yield

    button.setPressed(False)
    button.whenHeld(cmd1())
    scheduler.run()

    assert not state.executed

    button.setPressed(True)
    scheduler.run()
    scheduler.run()
    assert state.executed == 2

    button.setPressed(False)

    assert state.executed == 2


def test_toggle_when_pressed_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()

    class state:
        pass

    state.executed = 0

    def cmd1():
        while True:
            state.executed += 1
            yield

    button.setPressed(False)

    button.toggleWhenPressed(cmd1())
    scheduler.run()

    assert not state.executed

    button.setPressed(True)
    scheduler.run()

    assert state.executed


@pytest.mark.xfail(strict=True)
def test_function_bindings_coroutine(scheduler: commands2.CommandScheduler):

    buttonWhenPressed = MyButton()
    buttonWhileHeld = MyButton()
    buttonWhenReleased = MyButton()

    buttonWhenPressed.setPressed(False)
    buttonWhileHeld.setPressed(True)
    buttonWhenReleased.setPressed(True)

    counter = Counter()

    def increment():
        counter.increment()
        return
        yield

    buttonWhenPressed.whenPressed(increment())
    buttonWhileHeld.whileHeld(increment())
    buttonWhenReleased.whenReleased(increment())

    scheduler.run()
    buttonWhenPressed.setPressed(True)
    buttonWhenReleased.setPressed(False)
    scheduler.run()

    assert counter.value == 4
