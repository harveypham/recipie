""" Extend functools """

import time
from functools import *
from typing import Any, Callable, Generator, Optional, Union, Type, Tuple
import random
from itertools import repeat


def no_op(*args, **kwargs):
    pass

def default_on_error(default: Any, error=Exception):
    def wrapper(func):

        @wraps(func)
        def _deault_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error:
                return default;

        return _deault_func

    return wrapper

skip_on_error = partial(default_on_error, None)

def no_jitter(v: int):
    return v

def half_jitter(v: int):
    return v/2 + random.uniform(0, v/2)

def full_jitter(v: int):
    return random.uniform(0, v)

def expo_backoff(base: int, cap: int, jitter: Callable = no_jitter):
    def _expo_backoff():
        expo = 1
        while True:
            yield jitter(min(expo * base, cap))
            expo *= 2
    return _expo_backoff

def const_delay(seconds: int):
    return partial(repeat, seconds)

no_delay = const_delay(0)

def retry(
        tries: int,
        errors: Union[None, Type[Exception], Tuple[Type[Exception]]] = None,
        error_filter: Optional[Callable] = None,
        delay_gen: Generator[int, None, None] = no_delay,
        log_error: Optional[Callable] = None):

    assert tries >= 2, "Number of tries must be at least 2"
    assert errors is not None or error_filter is not None

    def _all(e):
        return True

    _errors = errors or Exception
    _error_filter = error_filter or _all
    _log_error = log_error or no_op

    def wrapper(func):
        assert tries >= 2, "Number of tries must be greater than 1"

        @wraps(func)
        def _retry(*args, **kwargs):
            delays = delay_gen()
            for i in range(tries-1):
                try:
                    return func(*args, **kwargs)
                except _errors as e:
                    if not _error_filter(e):
                        raise

                    delay = next(delays)
                    _log_error(f"Retrying error {str(e)} in {delay} seconds...")
                    time.sleep(delay)
            return func(*args, **kwargs)
        return _retry

    return wrapper
