import commands2
import commands2.button
from util import Counter


class MyButton(commands2.button.Trigger):
    def __init__(self):
        super().__init__(self.isPressed)
        self.pressed = False

    def isPressed(self) -> bool:
        return self.pressed

    def setPressed(self, value: bool):
        self.pressed = value


class MyCommand(commands2.Command):
    executed = 0

    ended = 0
    canceled = 0

    def execute(self) -> None:
        self.executed += 1

    def end(self, interrupted: bool) -> None:
        self.ended += 1
        if interrupted:
            self.canceled += 1


def test_ob_true(scheduler: commands2.CommandScheduler):
    cmd1 = MyCommand()
    button = MyButton()
    button.setPressed(False)

    button.onTrue(cmd1)
    scheduler.run()

    assert not cmd1.executed
    assert not scheduler.isScheduled(cmd1)

    button.setPressed(True)
    scheduler.run()
    scheduler.run()

    assert cmd1.executed
    assert scheduler.isScheduled(cmd1)


def test_on_false(scheduler: commands2.CommandScheduler):
    cmd1 = MyCommand()
    button = MyButton()
    button.setPressed(True)

    button.onFalse(cmd1)
    scheduler.run()

    assert not cmd1.executed
    assert not scheduler.isScheduled(cmd1)

    button.setPressed(False)
    scheduler.run()
    scheduler.run()

    assert cmd1.executed
    assert scheduler.isScheduled(cmd1)


def test_while_true(scheduler: commands2.CommandScheduler):
    cmd1 = MyCommand()
    button = MyButton()
    button.setPressed(False)

    button.whileTrue(cmd1)
    scheduler.run()

    assert not cmd1.executed
    assert not scheduler.isScheduled(cmd1)

    button.setPressed(True)
    scheduler.run()
    scheduler.run()

    assert cmd1.executed == 2
    assert scheduler.isScheduled(cmd1)

    button.setPressed(False)
    scheduler.run()

    assert cmd1.executed == 2
    assert not scheduler.isScheduled(cmd1)


def test_toggle_when_pressed(scheduler: commands2.CommandScheduler):
    cmd1 = MyCommand()
    button = MyButton()
    button.setPressed(False)

    button.toggleOnTrue(cmd1)
    scheduler.run()

    assert not cmd1.executed
    assert not scheduler.isScheduled(cmd1)

    button.setPressed(True)
    scheduler.run()

    assert cmd1.executed
    assert scheduler.isScheduled(cmd1)


def test_function_bindings(scheduler: commands2.CommandScheduler):
    buttonOnTrue = MyButton()
    buttonWhileTrue = MyButton()
    buttonOnFalse = MyButton()

    buttonOnTrue.setPressed(False)
    buttonWhileTrue.setPressed(True)
    buttonOnFalse.setPressed(True)

    counter = Counter()

    buttonOnTrue.onTrue(commands2.InstantCommand(counter.increment))
    buttonWhileTrue.whileTrue(commands2.InstantCommand(counter.increment))
    buttonOnFalse.onFalse(commands2.InstantCommand(counter.increment))

    scheduler.run()
    buttonOnTrue.setPressed(True)
    buttonOnFalse.setPressed(False)
    scheduler.run()

    assert counter.value == 2


def test_button_composition(scheduler: commands2.CommandScheduler):
    button1 = MyButton()
    button2 = MyButton()

    button1.setPressed(True)
    button2.setPressed(False)

    # TODO: not sure if this is a great idea?
    assert button1
    assert not button2

    assert not button1.and_(button2)
    assert button1.or_(button2)
    assert not button1.not_()
    assert button1.and_(button2.not_())
