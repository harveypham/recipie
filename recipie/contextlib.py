from contextlib import *
from typing import Callable, Any


class _func_wrap(AbstractContextManager):
    def __init__(self, func: Callable, *args, **kwargs):
        from functools import partial
        self._func = partial(func, *args, **kwargs)

class rollback(_func_wrap):
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self._func()

class commit(_func_wrap):
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._func()

class Buffer(AbstractContextManager):
    def __init__(self, size: int, func: Callable):
        assert size > 1, "size must be more than one"
        self._size = size
        self._func = func
        self._buffer = []

    def append(self, item: Any):
        if len(self._buffer) == self._size:
            self._func(self._buffer)
            self._buffer = [item]
        else:
            self._buffer.append(item)

    def clear(self):
        if self._buffer:
            self._func(self._buffer)
            self._buffer = []

    def extend(self, items:list):
        if items:
            temp = self._buffer + items
            *extra, self._buffer = [temp[i:i+self._size] for i in range(0, len(temp), self._size)]
            for s in extra:
                self._func(s)

    def __exit__(self, exec_type, exec_value, traceback):
        self.clear()
