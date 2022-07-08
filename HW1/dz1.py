import functools
import time
import requests
import tracemalloc
from collections import OrderedDict, Counter


def profile(msg='Elapsed time'):
    def internal(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            print(msg, f'({f.__name__}): {time.time() - start}s')
            return result
        return deco
    return internal

#memory
def measure_memory(f):
    @functools.wraps(f)
    def deco(*args, **kwargs):
        tracemalloc.start()
        result = f(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        print(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
        tracemalloc.stop()
        return result
    return deco

#LFU

def cache(max_limit=64):
    def internal(f):
        @functools.wraps(f)
        def deco(*args):
            # Закидуємо url в список ключів
            deco._keys.append(args)
            if args in deco._cache:
                return deco._cache[args]
            result = f(*args)
            # Видалення зі словника значень з більшим ніж max_limit
            if len(deco._cache) >= max_limit:
                # Дізнаємось найменш повторюваний ключ
                least_common_key = Counter(deco._keys).most_common()[-1]
                del deco._cache[least_common_key]
            deco._cache[args] = result
            return result
        deco._cache = OrderedDict()
        # Створюємо список з ключами
        deco._keys = []
        return deco
    return internal

@profile(msg='Elapsed time')
@cache(max_limit=20)
@measure_memory
def fetch_url(url, first_n=100):
    """Fetch a given url"""
    res = requests.get(url)
    return res.content[:first_n] if first_n else res.content

fetch_url('https://reddit.com')
print(fetch_url._cache)