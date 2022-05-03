import commands2
import commands2.button
from commands2 import commandify

from util import Counter
import pytest

def test_coroutine_command(scheduler: commands2.CommandScheduler):
    class state: pass
    state.co1_count = 0
    def co1():
        for i in range(3):
            state.co1_count += 1
            yield 

    cmd1 = commands2.CoroutineCommand(co1)

    cmd1.schedule()

    for _ in range(10):
        scheduler.run()
    
    assert state.co1_count == 3


def test_coroutine_composition(scheduler: commands2.CommandScheduler):
    class state: pass
    state.co1_count = 0
    state.co2_count = 0
    def co1():
        for i in range(3):
            state.co1_count += 1
            yield

    def co2():
        state.co2_count += 1
        yield from co1()
        state.co2_count += 1

    commands2.CoroutineCommand(co2).schedule()

    for _ in range(10):
        scheduler.run()
    
    assert state.co1_count == 3
    assert state.co2_count == 2

def test_yield_from_command(scheduler: commands2.CommandScheduler):
    class state: pass
    state.co1_count = 0
    state.co2_count = 0

    class Command1(commands2.CommandBase):
        def execute(self) -> None:
            state.co1_count += 1
        
        def isFinished(self) -> bool:
            return state.co1_count == 3

    def co2():
        state.co2_count += 1
        yield from Command1()
        state.co2_count += 1
    
    commands2.CoroutineCommand(co2).schedule()

    for _ in range(10):
        scheduler.run()
    
    assert state.co1_count == 3
    assert state.co2_count == 2

# def test_commandify(scheduler: commands2.CommandScheduler):
#     class state: pass
#     state.co1_count = 0

#     def co1(n):
#         for i in range(n):
#             print(1)
#             state.co1_count += 1
#             yield 

#     Cmd1 = commandify(co1)
#     Cmd1(5).schedule()
#     # Cmd1(5).schedule()

#     for _ in range(10):
#         scheduler.run()
    
#     assert state.co1_count == 5

def test_commandify_decorator(scheduler: commands2.CommandScheduler):
    class state: pass
    state.co1_count = 0

    @commandify
    def Cmd1(n):
        for i in range(n):
            print(1)
            state.co1_count += 1
            yield 

    cmd = Cmd1(5)
    cmd.schedule()
    # Cmd1(5).schedule()
    for _ in range(10):
        scheduler.run()
    
    assert state.co1_count == 5

def test_coroutine_command_lambda_pass_args(): ...