from contextlib import *
from functools import partial
from typing import Callable


class _func_wrap(AbstractContextManager):
    def __init__(self, func: Callable, *args, **kwargs):
        self._func = partial(func, *args, **kwargs)

class rollback(_func_wrap):
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self._func()

class commit(_func_wrap):
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._func()

