"""Limiter class implementation
"""
import asyncio
import logging
from functools import wraps
from inspect import isawaitable
from threading import RLock
from time import sleep
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from .abstracts import AbstractBucket
from .abstracts import AbstractClock
from .abstracts import BucketFactory
from .abstracts import Duration
from .abstracts import Rate
from .abstracts import RateItem
from .buckets import InMemoryBucket
from .clocks import TimeClock
from .exceptions import BucketFullException
from .exceptions import LimiterDelayException

logger = logging.getLogger("pyrate_limiter")

ItemMapping = Callable[[Any], Tuple[str, int]]
DecoratorWrapper = Callable[[Callable[[Any], Any]], Callable[[Any], Any]]


class SingleBucketFactory(BucketFactory):
    """Single-bucket factory for quick use with Limiter"""

    bucket: AbstractBucket
    clock: AbstractClock

    def __init__(self, bucket: AbstractBucket, clock: AbstractClock):
        self.clock = clock
        self.bucket = bucket
        self.schedule_leak(bucket, clock)

    def wrap_item(self, name: str, weight: int = 1):
        now = self.clock.now()

        async def wrap_async():
            return RateItem(name, await now, weight=weight)

        def wrap_sycn():
            return RateItem(name, now, weight=weight)

        return wrap_async() if isawaitable(now) else wrap_sycn()

    def get(self, _: RateItem) -> AbstractBucket:
        return self.bucket


class Limiter:
    """This class responsibility is to sum up all underlying logic
    and make working with async/sync functions easily
    """

    bucket_factory: BucketFactory
    raise_when_fail: bool
    max_delay: Optional[int] = None
    lock: RLock

    def __init__(
        self,
        argument: Union[BucketFactory, AbstractBucket, Rate, List[Rate]],
        clock: AbstractClock = TimeClock(),
        raise_when_fail: bool = True,
        max_delay: Optional[Union[int, Duration]] = None,
    ):
        """Init Limiter using either a single bucket / multiple-bucket factory
        / single rate / rate list
        """
        self.bucket_factory = self._init_bucket_factory(argument, clock=clock)
        self.raise_when_fail = raise_when_fail

        if max_delay is not None:
            if isinstance(max_delay, Duration):
                max_delay = int(max_delay)

            assert max_delay >= 0, "Max-delay must not be negative"

        self.max_delay = max_delay
        self.lock = RLock()

    def _init_bucket_factory(
        self,
        argument: Union[BucketFactory, AbstractBucket, Rate, List[Rate]],
        clock: AbstractClock,
    ) -> BucketFactory:
        if isinstance(argument, Rate):
            argument = [argument]

        if isinstance(argument, list):
            assert len(argument) > 0, "Rates must not be empty"
            assert isinstance(argument[0], Rate), "Not valid rates list"
            rates = argument
            logger.info("Initializing default bucket(InMemoryBucket) with rates: %s", rates)
            argument = InMemoryBucket(rates)

        if isinstance(argument, AbstractBucket):
            argument = SingleBucketFactory(argument, clock)

        assert isinstance(argument, BucketFactory), "Not a valid bucket/bucket-factory"
        return argument

    def _raise_bucket_full_if_necessary(
        self,
        bucket: AbstractBucket,
        item: RateItem,
    ):
        if self.raise_when_fail:
            assert bucket.failing_rate is not None  # NOTE: silence mypy
            raise BucketFullException(item, bucket.failing_rate)

    def _raise_delay_exception_if_necessary(
        self,
        bucket: AbstractBucket,
        item: RateItem,
        delay: int,
    ):
        if self.raise_when_fail:
            assert bucket.failing_rate is not None  # NOTE: silence mypy
            assert isinstance(self.max_delay, int)
            raise LimiterDelayException(
                item,
                bucket.failing_rate,
                delay,
                self.max_delay,
            )

    def delay_or_raise(
        self,
        bucket: AbstractBucket,
        item: RateItem,
    ) -> Union[bool, Awaitable[bool]]:
        """On `try_acquire` failed, handle delay or raise error immediately"""
        assert bucket.failing_rate is not None

        if self.max_delay is None:
            self._raise_bucket_full_if_necessary(bucket, item)
            return False

        delay = bucket.waiting(item)

        def _handle_reacquire(re_acquire: bool) -> bool:
            if not re_acquire:
                logger.error(
                    """
                Re-acquiring with delay expected to be successful,
                if it failed then either clock or bucket is probably unstable
                """
                )
                self._raise_bucket_full_if_necessary(bucket, item)

            return re_acquire

        if isawaitable(delay):

            async def _handle_async():
                nonlocal delay
                delay = await delay
                assert isinstance(delay, int), "Delay not integer"
                delay += 50

                if delay > self.max_delay:
                    logger.error(
                        "Required delay too large: actual=%s, expected=%s",
                        delay,
                        self.max_delay,
                    )
                    self._raise_delay_exception_if_necessary(bucket, item, delay)
                    return False

                await asyncio.sleep(delay / 1000)
                item.timestamp += delay
                re_acquire = bucket.put(item)

                if isawaitable(re_acquire):
                    re_acquire = await re_acquire

                return _handle_reacquire(re_acquire)

            return _handle_async()

        assert isinstance(delay, int)

        if delay < 0:
            logger.error(
                "Cannot fit item into bucket: item=%s, rate=%s, bucket=%s",
                item,
                bucket.failing_rate,
                bucket,
            )
            self._raise_bucket_full_if_necessary(bucket, item)
            return False

        delay += 50

        if delay > self.max_delay:
            logger.error(
                "Required delay too large: actual=%s, expected=%s",
                delay,
                self.max_delay,
            )
            self._raise_delay_exception_if_necessary(bucket, item, delay)
            return False

        sleep(delay / 1000)
        item.timestamp += delay
        re_acquire = bucket.put(item)
        # NOTE: if delay is not Awaitable, then `bucket.put` is not Awaitable
        assert isinstance(re_acquire, bool)
        return _handle_reacquire(re_acquire)

    def handle_bucket_put(
        self,
        bucket: AbstractBucket,
        item: RateItem,
    ) -> Union[bool, Awaitable[bool]]:
        """Putting item into bucket"""

        def _handle_result(is_success: bool):
            if not is_success:
                return self.delay_or_raise(bucket, item)

            return True

        acquire = bucket.put(item)

        if isawaitable(acquire):

            async def _put_async():
                nonlocal acquire
                acquire = await acquire
                result = _handle_result(acquire)

                while isawaitable(result):
                    result = await result

                return result

            return _put_async()

        return _handle_result(acquire)  # type: ignore

    def try_acquire(self, name: str, weight: int = 1) -> Union[bool, Awaitable[bool]]:
        """Try accquiring an item with name & weight
        Return true on success, false on failure
        """
        with self.lock:
            assert weight >= 0, "item's weight must be >= 0"

            if weight == 0:
                # NOTE: if item is weightless, just let it go through
                # NOTE: this might change in the futre
                return True

            item = self.bucket_factory.wrap_item(name, weight)

            if isawaitable(item):

                async def _handle_async():
                    nonlocal item
                    item = await item
                    bucket = self.bucket_factory.get(item)
                    assert isinstance(bucket, AbstractBucket), f"Invalid bucket: item: {name}"
                    result = self.handle_bucket_put(bucket, item)

                    while isawaitable(result):
                        result = await result

                    return result

                return _handle_async()

            assert isinstance(item, RateItem)  # NOTE: this is to silence mypy warning
            bucket = self.bucket_factory.get(item)
            assert isinstance(bucket, AbstractBucket), f"Invalid bucket: item: {name}"
            result = self.handle_bucket_put(bucket, item)

            if isawaitable(result):

                async def _handle_async_result():
                    nonlocal result
                    while isawaitable(result):
                        result = await result

                    return result

                return _handle_async_result()

            return result

    def as_decorator(self) -> Callable[[ItemMapping], DecoratorWrapper]:
        """Use limiter decorator
        Use with both sync & async function
        """

        def with_mapping_func(mapping: ItemMapping) -> DecoratorWrapper:
            def decorator_wrapper(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
                """Actual function warpper"""

                @wraps(func)
                def wrapper(*args, **kwargs):
                    (name, weight) = mapping(*args, **kwargs)
                    assert isinstance(name, str), "Mapping name is expected but not found"
                    assert isinstance(weight, int), "Mapping weight is expected but not found"
                    accquire_ok = self.try_acquire(name, weight)

                    if not isawaitable(accquire_ok):
                        return func(*args, **kwargs)

                    async def _handle_accquire_async():
                        nonlocal accquire_ok
                        accquire_ok = await accquire_ok
                        result = func(*args, **kwargs)

                        if isawaitable(result):
                            return await result

                        return result

                    return _handle_accquire_async()

                return wrapper

            return decorator_wrapper

        return with_mapping_func
