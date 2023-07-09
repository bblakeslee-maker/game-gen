import os
import pickle
from functools import wraps
import hashlib

def persistent_cache(cache_file):
    """
    Function to implement a persistent cache. It decorates a function with caching logic,
    storing results of function calls in a file to avoid duplicate computations.

    Parameters:
    cache_file (str): The path to the cache file.

    Returns:
    decorator (function): The wrapper function.
    """

    def decorator(func):
        cache = {}

        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # args = args[1:]

            key = (args, tuple(kwargs.items()))

            byte_data = pickle.dumps(key)
            hasher = hashlib.sha256()
            hasher.update(byte_data)

            key = hasher.digest()

            if key not in cache:
                cache[key] = func(*args, **kwargs)
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache, f)
            return cache[key]
        return wrapper

    return decorator
