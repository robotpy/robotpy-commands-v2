from typing import Callable, Optional, overload, List, Union

from ._impl import Command, Subsystem
from ._impl import Trigger as _Trigger

from .coroutinecommand import CoroutineCommand, Coroutineable, Coroutine

class Trigger:
	"""
	A button that can be pressed or released.
	"""

	def __init__(self, is_active: Callable[[], bool] = lambda: False) -> None:
		self._trigger = _Trigger(is_active)

	def __bool__(self) -> bool:
		return bool(self._trigger)

	def get(self) -> bool:
		return bool(self)

	def __call__(self) -> bool:
		return bool(self)

	def __and__(self, other: 'Trigger') -> 'Trigger':
		return Trigger(lambda: self() and other())
	
	def __or__(self, other: 'Trigger') -> 'Trigger':
		return Trigger(lambda: self() or other())

	def __not__(self) -> 'Trigger':
		return Trigger(lambda: not self())

	@overload
	def whenActive(self, command: Command, /, interruptible: bool = True) -> None: ...

	@overload
	def whenActive(self, coroutine: Union[Coroutine, Coroutineable], /, *, interruptible: bool = True, requirements: Optional[List[Subsystem]] = None) -> None: ...

	@overload
	def whenActive(self, coroutine: None, /, *, interruptible: bool = True, requirements: Optional[List[Subsystem]] = None) -> Callable[[Coroutineable], None]: ...

	def whenActive(self, command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]], /, interruptible: bool = True, requirements: Optional[List[Subsystem]] = None) -> Union[None, Callable[[Coroutineable], None]]:
		if command_or_coroutine is None:
			def wrapper(coroutine: Coroutineable) -> None:
				self.whenActive(coroutine, interruptible = interruptible, requirements = requirements)
			return wrapper

		if isinstance(command_or_coroutine, Command):
			self._trigger.whenActive(command_or_coroutine, interruptible)
			return

		self._trigger.whenActive(CoroutineCommand(command_or_coroutine, requirements), interruptible)
		return

	@overload
	def whenInactive(self, command: Command, /, interruptible: bool = True) -> None: ...

	@overload
	def whenInactive(self, coroutine: Union[Coroutine, Coroutineable], /, *, interruptible: bool = True, requirements: Optional[List[Subsystem]] = None) -> None: ...

	@overload
	def whenInactive(self, coroutine: None, /, *, interruptible: bool = True, requirements: Optional[List[Subsystem]] = None) -> Callable[[Coroutineable], None]: ...

	def whenInactive(self, command_or_coroutine: Optional[Union[Command, Coroutine, Coroutineable]], /, interruptible: bool = True, requirements: Optional[List[Subsystem]] = None) -> Union[None, Callable[[Coroutineable], None]]:
		if command_or_coroutine is None:
			def wrapper(coroutine: Coroutineable) -> None:
				self.whenInactive(coroutine, interruptible = interruptible, requirements = requirements)
			return wrapper

		if isinstance(command_or_coroutine, Command):
			self._trigger.whenInactive(command_or_coroutine, interruptible)
			return

		self._trigger.whenInactive(CoroutineCommand(command_or_coroutine, requirements), interruptible)
		return