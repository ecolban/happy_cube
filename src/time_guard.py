import multiprocessing
import multiprocessing.queues
from collections.abc import Callable
from functools import wraps
from typing import Any


def _worker(
    q: multiprocessing.queues.Queue[tuple[str, Any]],
    f: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> None:
    try:
        q.put(('ok', f(*args, **kwargs)))
    except Exception as e:
        q.put(('err', e))


def time_guard(timeout: int = 1) -> Callable[[Callable], Callable]:
    """A decorator that raises a TimeoutError after `timeout` seconds unless the
    decorated function hasn't already returned."""

    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ctx = multiprocessing.get_context('fork')
            q = ctx.Queue()
            p = ctx.Process(target=_worker, args=(q, f, args, kwargs))
            p.start()
            p.join(timeout)
            if p.is_alive():
                p.terminate()
                p.join()
                raise TimeoutError()
            status, val = q.get_nowait()
            if status == 'err':
                raise val
            return val

        return wrapper

    return decorator
