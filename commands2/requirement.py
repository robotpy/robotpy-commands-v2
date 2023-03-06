from typing import *
from enum import *


class InterruptBehavior(IntEnum):
    CANCEL_SELF = 1
    CANCEL_INCOMING = 2


class Requirement:
    def __init__(self):
        # make atomic
        self._value = 0

    def requirement_level(self) -> int:
        return self._value

    def is_required(self) -> bool:
        return self._value > 0

    def require(self) -> Optional[Generator[None, int, None]]:
        if self._value == InterruptBehavior.CANCEL_INCOMING.value:
            return None

        def gen() -> Generator[None, int, None]:
            self._value = yield
            # For some reason generators need at least two yields
            yield

        callback = gen()
        # Generators need to be started before they can get values
        callback.__next__()
        return callback

