""" Extend functools """

from functools import *
from typing import Any, Callable, Generator, Optional, Union, Type, Tuple


def scoped(outer: callable):

    def wrapper(func):
        setattr(outer, func.__name__, func)

        @wraps(func)
        def _disable(*args, **kwargs):
            raise NameError(f"name {func.__name__} is not defined")
        return _disable

    return wrapper


def no_op(*args, **kwargs):
    pass


def default_on_error(default: any, errors: Union[Type[Exception], Tuple[Type[Exception]]] = Exception):
    def wrapper(func):

        @wraps(func)
        def _default_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors:
                return default;

        return _default_func

    return wrapper

skip_on_error = partial(default_on_error, None)


def retry(
        tries: int,
        errors: Union[None, Type[Exception], Tuple[Type[Exception]]] = None,
        error_filter: Optional[callable] = None,
        delay_gen: Optional[Generator[int, None, None]] = None,
        log_error: Optional[Callable] = None):
    import time

    assert tries >= 2, \
        "Number of tries must be at least 2"
    assert errors is not None or error_filter is not None, \
        "Must specify error classes or error filter function"

    def _all(e):
        return True

    _errors = errors or Exception
    _error_filter = error_filter or _all
    _log_error = log_error or no_op
    _delay_gen = delay_gen or retry.no_delay

    def wrapper(func):

        @wraps(func)
        def _retry(*args, **kwargs):
            delays = _delay_gen()
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

@scoped(retry)
def const_delay(seconds: int):
    from itertools import repeat
    return partial(repeat, seconds)

retry.no_delay = retry.const_delay(0)

@scoped(retry)
def no_jitter(v: int):
    return v

@scoped(retry)
def half_jitter(v: int):
    return v/2 + retry.full_jitter(v/2)

@scoped(retry)
def full_jitter(v: int):
    from random import uniform
    return uniform(0, v)

@scoped(retry)
def expo_backoff(base: int, cap: int, jitter: callable = no_jitter):
    def _expo_backoff():
        expo = 1
        while True:
            yield jitter(min(expo * base, cap))
            expo *= 2
    return _expo_backoff
