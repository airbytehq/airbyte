import pickle
from pathlib import Path
import logging
from typing import Sequence
from urllib3.util import Retry

import requests
from requests.adapters import HTTPAdapter

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


def http_adapter(
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_on: Sequence[int] = (413, 429, 500, 502, 503, 504, 599),
        methods: Sequence[str] = ('HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'),
        backoff_factor: int = 1,
        allow_http_insecure: bool = False,
) -> requests.Session:
    """ See:
    https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    """
    retries = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=retry_on,
        allowed_methods=methods,
    )

    adapter = TimeoutHTTPAdapter(timeout=timeout, max_retries=retries)
    http = requests.Session()
    http.mount("https://", adapter)
    if allow_http_insecure:
        # noinspection HttpUrlsUsage
        http.mount("http://", adapter)

    return http


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.pop('timeout', 5.0)
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        kwargs.setdefault('timeout', self.timeout)
        return super().send(request, **kwargs)
