import signal
from collections.abc import Callable
from functools import wraps


def timeout_handler(_signum, _frame):
    raise TimeoutError()


def time_guard(timeout: int = 1) -> Callable[[Callable], Callable]:
    """A decorator that raises a TimeoutError after `timeout` seconds unless the
    decorated function hasn't already returned."""

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator
