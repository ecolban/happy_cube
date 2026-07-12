import asyncio
from time import perf_counter, sleep

from time_guard import time_guard


def test_time_guard():
    @time_guard(2)
    def f():
        sleep(t)

    print()
    for fn in (f,):
        for t in (1.2, 5.6):
            start = perf_counter()
            try:
                print(f"Calling {fn.__name__}({t})")
                fn()
                print(f"✅{fn.__name__} completed!")
            except asyncio.TimeoutError:
                print(f"❌{fn.__name__} timed out!")
            print(f"Time = {int((perf_counter() - start) * 1000)} ms")
