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
    button.setPressed(False)

    class state: pass
    state.executed = False

    @button.whenPressed
    def cmd1():
        state.executed = True
        return
        yield

    scheduler.run()

    assert not state.executed

    button.setPressed(True)
    scheduler.run()
    scheduler.run()

    assert state.executed


def test_when_released_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()
    button.setPressed(True)

    class state: pass
    state.executed = False

    @button.whenReleased()
    def cmd1():
        state.executed = True
        return
        yield

    scheduler.run()

    assert not state.executed

    button.setPressed(False)
    scheduler.run()
    scheduler.run()

    assert state.executed

def test_while_held_coroutine(scheduler: commands2.CommandScheduler):
    button = MyButton()
    button.setPressed(False)

    class state: pass
    state.executed = 0

    @button.whileHeld(interruptible=True)
    def cmd1():
        state.executed += 1
        return
        yield

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
    button.setPressed(False)

    class state: pass
    state.executed = 0

    @button.whenHeld(runs_when_disabled=True)
    def cmd1():
        while True:
            state.executed += 1
            yield

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
    button.setPressed(False)

    class state: pass
    state.executed = 0

    @button.toggleWhenPressed
    def cmd1():
        while True:
            state.executed += 1
            yield
    
    
    scheduler.run()

    assert not state.executed

    button.setPressed(True)
    scheduler.run()

    assert state.executed
