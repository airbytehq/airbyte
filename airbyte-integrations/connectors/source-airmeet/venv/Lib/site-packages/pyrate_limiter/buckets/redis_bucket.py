"""Bucket implementation using Redis
"""
from __future__ import annotations

from inspect import isawaitable
from typing import Awaitable
from typing import List
from typing import Optional
from typing import Tuple
from typing import TYPE_CHECKING
from typing import Union

from ..abstracts import AbstractBucket
from ..abstracts import Rate
from ..abstracts import RateItem
from ..utils import id_generator


if TYPE_CHECKING:
    from redis import Redis
    from redis.asyncio import Redis as AsyncRedis


class LuaScript:
    """Scripts that deal with bucket operations"""

    PUT_ITEM = """
    local now = ARGV[1]
    local space_required = tonumber(ARGV[2])
    local bucket = ARGV[3]
    local item_name = ARGV[4]

    for idx, key in ipairs(KEYS) do
        if idx > 4 then
            local interval = tonumber(key)
            local limit = tonumber(ARGV[idx])
            local count = redis.call('ZCOUNT', bucket, now - interval, now)
            local space_available = limit - tonumber(count)
            if space_available < space_required then
                return idx - 5
            end
        end
    end

    for i=1,space_required do
        redis.call('ZADD', bucket, now, item_name..i)
    end
    return -1
    """


class RedisBucket(AbstractBucket):
    """A bucket using redis for storing data
    - We are not using redis' built-in TIME since it is non-deterministic
    - In distributed context, use local server time or a remote time server
    - Each bucket instance use a dedicated connection to avoid race-condition
    - can be either sync or async
    """

    rates: List[Rate]
    failing_rate: Optional[Rate]
    bucket_key: str
    script_hash: str
    redis: Union[Redis, AsyncRedis]

    def __init__(
        self,
        rates: List[Rate],
        redis: Union[Redis, AsyncRedis],
        bucket_key: str,
        script_hash: str,
    ):
        self.rates = rates
        self.redis = redis
        self.bucket_key = bucket_key
        self.script_hash = script_hash
        self.failing_rate = None

    @classmethod
    def init(
        cls,
        rates: List[Rate],
        redis: Union[Redis, AsyncRedis],
        bucket_key: str,
    ):
        script_hash = redis.script_load(LuaScript.PUT_ITEM)

        if isawaitable(script_hash):

            async def _async_init():
                nonlocal script_hash
                script_hash = await script_hash
                return cls(rates, redis, bucket_key, script_hash)

            return _async_init()

        return cls(rates, redis, bucket_key, script_hash)

    def _check_and_insert(self, item: RateItem) -> Union[Rate, None, Awaitable[Optional[Rate]]]:
        keys = [
            "timestamp",
            "weight",
            "bucket",
            "name",
            *[rate.interval for rate in self.rates],
        ]

        args = [
            item.timestamp,
            item.weight,
            self.bucket_key,
            # NOTE: this is to avoid key collision since we are using ZSET
            f"{item.name}:{id_generator()}:",
            *[rate.limit for rate in self.rates],
        ]

        idx = self.redis.evalsha(self.script_hash, len(keys), *keys, *args)

        def _handle_sync(returned_idx: int):
            assert isinstance(returned_idx, int), "Not int"
            if returned_idx < 0:
                return None

            return self.rates[returned_idx]

        async def _handle_async(returned_idx: Awaitable[int]):
            assert isawaitable(returned_idx), "Not corotine"
            awaited_idx = await returned_idx
            return _handle_sync(awaited_idx)

        return _handle_async(idx) if isawaitable(idx) else _handle_sync(idx)

    def put(self, item: RateItem) -> Union[bool, Awaitable[bool]]:
        """Add item to key"""
        failing_rate = self._check_and_insert(item)
        if isawaitable(failing_rate):

            async def _handle_async():
                nonlocal failing_rate
                self.failing_rate = await failing_rate
                return not bool(self.failing_rate)

            return _handle_async()

        assert isinstance(failing_rate, Rate) or failing_rate is None
        self.failing_rate = failing_rate
        return not bool(self.failing_rate)

    def leak(self, current_timestamp: Optional[int] = None) -> Union[int, Awaitable[int]]:
        assert current_timestamp is not None
        return self.redis.zremrangebyscore(
            self.bucket_key,
            0,
            current_timestamp - self.rates[-1].interval,
        )

    def flush(self):
        self.failing_rate = None
        return self.redis.delete(self.bucket_key)

    def count(self):
        return self.redis.zcard(self.bucket_key)

    def peek(self, index: int) -> Union[RateItem, None, Awaitable[Optional[RateItem]]]:
        items = self.redis.zrange(
            self.bucket_key,
            -1 - index,
            -1 - index,
            withscores=True,
            score_cast_func=int,
        )

        if not items:
            return None

        def _handle_items(received_items: List[Tuple[str, int]]):
            if not received_items:
                return None

            item = received_items[0]
            rate_item = RateItem(name=str(item[0]), timestamp=item[1])
            return rate_item

        if isawaitable(items):

            async def _awaiting():
                nonlocal items
                items = await items
                return _handle_items(items)

            return _awaiting()

        assert isinstance(items, list)
        return _handle_items(items)
