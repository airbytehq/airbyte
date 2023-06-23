import pickle
from pathlib import Path
import logging

logger = logging.getLogger("airbyte")


def cache(path: str):
    def outer(f):
        def inner(*args, **kwargs):
            cache = Path(f"cache-{path}")
            if cache.exists():
                logger.info(f"Using cache for {path}")
                pickled = cache.read_bytes()
                return pickle.loads(cache.read_bytes())
            else:
                result = f(*args, **kwargs)
                pickled = pickle.dumps(result)
                cache.write_bytes(pickled)
                return result

        if 1:
            return inner
        else:
            return lambda *args, **kwargs: f(*args, **kwargs)

    return outer
