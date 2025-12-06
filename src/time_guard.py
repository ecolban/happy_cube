import asyncio
import signal
from collections.abc import Callable
from functools import wraps
from time import perf_counter, sleep


def timeout_handler(_signum, _frame):
    raise TimeoutError()


def time_guard(timeout: int = 1) -> Callable[[Callable], Callable]:
    """A decorator that raises an asyncio.TimeoutError after `timeout` seconds unless the
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


@time_guard(2)
def f(t: float = 0.1):
    sleep(t)


async def main():
    for fn in (f,):
        for t in (1.2, 5.6):
            start = perf_counter()
            try:
                print(f"Calling {fn.__name__}({t})")
                await fn(t)
                print(f"✅{fn.__name__} completed!")
            except asyncio.TimeoutError:
                print(f"❌{fn.__name__} timed out!")
            print(f"Time = {int((perf_counter() - start) * 1000)} ms")


if __name__ == '__main__':
    asyncio.run(main())
