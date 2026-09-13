"""Retry for transient SAP failures.

The CDK's backoff machinery lives under `sources.streams.http` and is useless
here. SAP raises `RESOURCE_FAILURE` / `RFC_COMMUNICATION_FAILURE` whenever the
system is briefly out of free work processes -- routine on a busy system, and not
something that should fail a sync.

Only failures classified as transient are retried. A wrong password must *not* be
retried: repeating it locks the SAP user out.
"""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import TypeVar

from airbyte_cdk.models import FailureType

from source_sap.errors import classify

logger = logging.getLogger("airbyte")

T = TypeVar("T")

DEFAULT_ATTEMPTS = 3
DEFAULT_BASE_DELAY = 5.0


def retry_transient(
    attempts: int = DEFAULT_ATTEMPTS, base_delay: float = DEFAULT_BASE_DELAY
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry a callable while SAP reports a transient condition."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> T:
            delay = base_delay
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    if classify(str(exc)) is not FailureType.transient_error or attempt == attempts:
                        raise
                    logger.warning(
                        "SAP reported a transient failure (attempt %d of %d), retrying in %.0fs: %s",
                        attempt,
                        attempts,
                        delay,
                        str(exc).splitlines()[0] if str(exc) else exc,
                    )
                    time.sleep(delay)
                    delay *= 2
            raise AssertionError("unreachable")  # pragma: no cover

        return wrapper

    return decorator
