from functools import wraps
from typing import Any, Callable, Generator, List, Union, Optional
from ._impl import CommandBase, Subsystem
import inspect
from typing_extensions import TypeGuard

Coroutine = Generator[None, None, None]
CoroutineFunction = Callable[[], Generator[None, None, None]]
Coroutineable = Union[Callable[[], None],  CoroutineFunction]

def is_coroutine(func: Any) -> TypeGuard[Coroutine]:
	return inspect.isgenerator(func)

def is_coroutine_function(func: Any) -> TypeGuard[CoroutineFunction]:
	return inspect.isgeneratorfunction(func)

def is_coroutineable(func: Any) -> TypeGuard[Coroutineable]:
	return is_coroutine_function(func) or callable(func)

def ensure_generator_function(func: Coroutineable) -> Callable[..., Coroutine]:
	if is_coroutine_function(func):
		return func

	@wraps(func)
	def wrapper(*args, **kwargs):
		func(*args, **kwargs)
		yield

	return wrapper

class CoroutineCommand(CommandBase):
	coroutine: Optional[Coroutine]
	coroutine_function: Optional[Coroutineable]
	is_finished: bool

	def __init__(self, coroutine: Union[Coroutine, Coroutineable], requirements: Optional[List[Subsystem]] = None) -> None:
		self.coroutine = None
		self.coroutine_function = None

		if is_coroutine(coroutine):
			self.coroutine = coroutine
		elif is_coroutine_function(coroutine):
			self.coroutine_function = coroutine
		else:
			raise TypeError("The coroutine must be a coroutine or a coroutine function")

		if requirements is not None:
			self.addRequirements(requirements)

		self.is_finished = False

	def initialize(self) -> None:
		if self.coroutine_function:
			self.coroutine = ensure_generator_function(self.coroutine_function)()
		elif self.coroutine and self.is_finished:
			RuntimeError("Generator objects cannot be reused.")

		self.is_finished = False


	def execute(self):
		try:
			if not self.is_finished:
				if not self.coroutine:
					raise TypeError("This command was not properly initialized")
				next(self.coroutine)
		except StopIteration:
			self.is_finished = True

	def isFinished(self):
		return self.is_finished

class commandify:
	def __init__(self, requirements: Optional[List[Subsystem]] = None) -> None:
		self.requirements = requirements

	def __call__(self, func: Coroutineable):
		@wraps(func)
		def arg_accepter(*args, **kwargs) -> CoroutineCommand:
			return CoroutineCommand(lambda: ensure_generator_function(func)(*args, **kwargs), self.requirements)
		return arg_accepter
