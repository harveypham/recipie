""" Extend functools """

from functools import *
from typing import Any, Callable, Iterator, Optional, Union, Type, Tuple


def no_op(*args, **kwargs):
    pass

def no_filter(_):
    return True


def scoped(outer: Callable):

    def wrapper(func):
        setattr(outer, func.__name__, func)

        @wraps(func)
        def _disable(*args, **kwargs):
            raise NameError(f"name {func.__name__} is not defined")
        return _disable

    return wrapper


def default_on_error(
        default: Any,
        errors: Union[Type[Exception], Tuple[Type[Exception]]] = Exception,
        error_filter: Callable[[Exception], bool] = no_filter):
    def wrapper(func):

        @wraps(func)
        def _default_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                if error_filter(e):
                    return default
                else:
                    raise

        return _default_func

    return wrapper

skip_on_error = partial(default_on_error, None)


def retry(
        tries: int,
        errors: Union[None, Type[Exception], Tuple[Type[Exception]]] = None,
        error_filter: Callable[[Exception], bool] = None,
        delay_gen: Optional[Callable[[], Iterator[int]]] = None,
        log_error: Optional[Callable] = None):
    import time

    assert tries >= 2, \
        "Number of tries must be at least 2"
    assert errors is not None or error_filter is not None, \
        "Must specify error classes or error filter function"

    _errors = errors or Exception
    _error_filter = error_filter or no_filter
    _log_error = log_error or no_op

    def wrapper(func):

        @wraps(func)
        def _retry(*args, **kwargs):
            delays = (delay_gen or retry.no_delay)()
            for i in range(tries-1):
                try:
                    return func(*args, **kwargs)
                except _errors as e:
                    if not _error_filter(e):
                        raise

                    delay = next(delays)
                    _log_error(f"Retrying error {str(e)} at {i} attempt in {delay} seconds...")
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
    from random import uniform
    return v//2 + uniform(0, v//2 + v%2)

@scoped(retry)
def full_jitter(v: int):
    from random import uniform
    return uniform(0, v)

@scoped(retry)
def expo_backoff(base: int, cap: int, jitter: Callable = None):
    _jitter = jitter if jitter is not None else retry.no_jitter
    def _expo_backoff():
        expo = 1
        while True:
            yield _jitter(min(expo * base, cap))
            expo *= 2
    return _expo_backoff
