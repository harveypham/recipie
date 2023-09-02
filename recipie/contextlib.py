from contextlib import *
from functools import partial as _partial


class cleanup(AbstractContextManager):
    def __init__(self, func: callable, *args, **kwargs):
        self._func = _partial(func, *args, **kwargs) if args or kwargs else func
    
    def __exit__(self, *_):
        self._func()

    def cancel(self):
        self._func = lambda: None

class rollback(AbstractContextManager, _partial):
    def __exit__(self, exc_type, *_):
        if exc_type is not None:
            self.__call__()

class commit(AbstractContextManager, _partial):
    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self.__call__()


class Buffer(AbstractContextManager):
    def __init__(self, size: int, func: callable):
        assert size > 1, "size must be more than one"
        self._size = size
        self._func = func
        self._buffer = []

    def append(self, item: any):
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
            all_items = self._buffer + items
            *pages, self._buffer = [all_items[i:i+self._size] for i in range(0, len(all_items), self._size)]
            for page in pages:
                self._func(page)

    def __exit__(self, *_):
        self.clear()
