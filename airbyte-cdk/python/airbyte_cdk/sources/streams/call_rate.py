#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import abc
import dataclasses
import datetime
import logging
import time
from datetime import timedelta
from threading import RLock
from typing import TYPE_CHECKING, Any, Mapping, Optional
from urllib import parse

import requests
import requests_cache
from pyrate_limiter import InMemoryBucket, Limiter
from pyrate_limiter import Rate as PyRateRate
from pyrate_limiter import RateItem, TimeClock
from pyrate_limiter.exceptions import BucketFullException

# prevents mypy from complaining about missing session attributes in LimiterMixin
if TYPE_CHECKING:
    MIXIN_BASE = requests.Session
else:
    MIXIN_BASE = object

logger = logging.getLogger("airbyte")


@dataclasses.dataclass
class Rate:
    """Call rate limit"""

    limit: int
    interval: timedelta


class CallRateLimitHit(Exception):
    def __init__(self, error: str, item: Any, weight: int, rate: str, time_to_wait: timedelta):
        """Constructor

        :param error: error message
        :param item: object passed into acquire_call
        :param weight: how many credits were requested
        :param rate: string representation of the rate violated
        :param time_to_wait: how long should wait util more call will be available
        """
        self.item = item
        self.weight = weight
        self.rate = rate
        self.time_to_wait = time_to_wait
        super().__init__(error)


class AbstractCallRatePolicy(abc.ABC):
    """Call rate policy interface.
    Should be configurable with different rules, like N per M for endpoint X. Endpoint X is matched with APIBudget.
    """

    @abc.abstractmethod
    def matches(self, request: Any) -> bool:
        """Tells if this policy matches specific request and should apply to it

        :param request:
        :return: True if policy should apply to this request, False - otherwise
        """

    @abc.abstractmethod
    def try_acquire(self, request: Any, weight: int) -> None:
        """Try to acquire request

        :param request: a request object representing a single call to API
        :param weight: number of requests to deduct from credit
        :return:
        """

    @abc.abstractmethod
    def update(self, available_calls: Optional[int], call_reset_ts: Optional[datetime.datetime]) -> None:
        """Update call rate counting with current values

        :param available_calls:
        :param call_reset_ts:
        """


class RequestMatcher(abc.ABC):
    """Callable that help to match a request object with call rate policies."""

    @abc.abstractmethod
    def __call__(self, request: Any) -> bool:
        """

        :param request:
        :return: True if matches the provided request object, False - otherwise
        """


class HttpRequestMatcher(RequestMatcher):
    """Simple implementation of RequestMatcher for http requests case"""

    def __init__(
        self,
        method: Optional[str] = None,
        url: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, Any]] = None,
    ):
        """Constructor

        :param method:
        :param url:
        :param params:
        :param headers:
        """
        self._method = method
        self._url = url
        self._params = {str(k): str(v) for k, v in (params or {}).items()}
        self._headers = {str(k): str(v) for k, v in (headers or {}).items()}

    @staticmethod
    def _match_dict(obj: Mapping[str, Any], pattern: Mapping[str, Any]) -> bool:
        """Check that all elements from pattern dict present and have the same values in obj dict

        :param obj:
        :param pattern:
        :return:
        """
        return pattern.items() <= obj.items()

    def __call__(self, request: Any) -> bool:
        """

        :param request:
        :return: True if matches the provided request object, False - otherwise
        """
        if isinstance(request, requests.Request):
            prepared_request = request.prepare()
        elif isinstance(request, requests.PreparedRequest):
            prepared_request = request
        else:
            return False

        if self._method is not None:
            if prepared_request.method != self._method:
                return False
        if self._url is not None and prepared_request.url is not None:
            url_without_params = prepared_request.url.split("?")[0]
            if url_without_params != self._url:
                return False
        if self._params is not None:
            parsed_url = parse.urlsplit(prepared_request.url)
            params = dict(parse.parse_qsl(str(parsed_url.query)))
            if not self._match_dict(params, self._params):
                return False
        if self._headers is not None:
            if not self._match_dict(prepared_request.headers, self._headers):
                return False
        return True


class BaseCallRatePolicy(AbstractCallRatePolicy, abc.ABC):
    def __init__(self, matchers: list[RequestMatcher]):
        self._matchers = matchers

    def matches(self, request: Any) -> bool:
        """Tell if this policy matches specific request and should apply to it

        :param request:
        :return: True if policy should apply to this request, False - otherwise
        """

        if not self._matchers:
            return True
        return any(matcher(request) for matcher in self._matchers)


class UnlimitedCallRatePolicy(BaseCallRatePolicy):
    """
    This policy is for explicit unlimited call rates.
    It can be used when we want to match a specific group of requests and don't apply any limits.

    Example:

    APICallBudget(
        [
            UnlimitedCallRatePolicy(
                matchers=[HttpRequestMatcher(url="/some/method", headers={"sandbox": true})],
            ),
            FixedWindowCallRatePolicy(
                matchers=[HttpRequestMatcher(url="/some/method")],
                next_reset_ts=datetime.now(),
                period=timedelta(hours=1)
                call_limit=1000,
            ),
        ]
    )

    The code above will limit all calls to /some/method except calls that have header sandbox=True
    """

    def try_acquire(self, request: Any, weight: int) -> None:
        """Do nothing"""

    def update(self, available_calls: Optional[int], call_reset_ts: Optional[datetime.datetime]) -> None:
        """Do nothing"""


class FixedWindowCallRatePolicy(BaseCallRatePolicy):
    def __init__(self, next_reset_ts: datetime.datetime, period: timedelta, call_limit: int, matchers: list[RequestMatcher]):
        """A policy that allows {call_limit} calls within a {period} time interval

        :param next_reset_ts: next call rate reset time point
        :param period: call rate reset period
        :param call_limit:
        :param matchers:
        """

        self._next_reset_ts = next_reset_ts
        self._offset = period
        self._call_limit = call_limit
        self._calls_num = 0
        self._lock = RLock()
        super().__init__(matchers=matchers)

    def try_acquire(self, request: Any, weight: int) -> None:
        if weight > self._call_limit:
            raise ValueError("Weight can not exceed the call limit")
        if not self.matches(request):
            raise ValueError("Request does not match the policy")

        with self._lock:
            self._update_current_window()

            if self._calls_num + weight > self._call_limit:
                reset_in = self._next_reset_ts - datetime.datetime.now()
                error_message = (
                    f"reached maximum number of allowed calls {self._call_limit} " f"per {self._offset} interval, next reset in {reset_in}."
                )
                raise CallRateLimitHit(
                    error=error_message,
                    item=request,
                    weight=weight,
                    rate=f"{self._call_limit} per {self._offset}",
                    time_to_wait=reset_in,
                )

            self._calls_num += weight

    def update(self, available_calls: Optional[int], call_reset_ts: Optional[datetime.datetime]) -> None:
        """Update call rate counters, by default, only reacts to decreasing updates of available_calls and changes to call_reset_ts.
        We ignore updates with available_calls > current_available_calls to support call rate limits that are lower than API limits.

        :param available_calls:
        :param call_reset_ts:
        """
        with self._lock:
            self._update_current_window()
            current_available_calls = self._call_limit - self._calls_num

            if available_calls is not None and current_available_calls > available_calls:
                logger.debug(
                    "got rate limit update from api, adjusting available calls from %s to %s", current_available_calls, available_calls
                )
                self._calls_num = self._call_limit - available_calls

            if call_reset_ts is not None and call_reset_ts != self._next_reset_ts:
                logger.debug("got rate limit update from api, adjusting reset time from %s to %s", self._next_reset_ts, call_reset_ts)
                self._next_reset_ts = call_reset_ts

    def _update_current_window(self) -> None:
        now = datetime.datetime.now()
        if now > self._next_reset_ts:
            logger.debug("started new window, %s calls available now", self._call_limit)
            self._next_reset_ts = self._next_reset_ts + self._offset
            self._calls_num = 0


class MovingWindowCallRatePolicy(BaseCallRatePolicy):
    """
    Policy to control requests rate implemented on top of PyRateLimiter lib.
    The main difference between this policy and FixedWindowCallRatePolicy is that the rate-limiting window
    is moving along requests that we made, and there is no moment when we reset an available number of calls.
    This strategy requires saving of timestamps of all requests within a window.
    """

    def __init__(self, rates: list[Rate], matchers: list[RequestMatcher]):
        """Constructor

        :param rates: list of rates, the order is important and must be ascending
        :param matchers:
        """
        if not rates:
            raise ValueError("The list of rates can not be empty")
        pyrate_rates = [PyRateRate(limit=rate.limit, interval=int(rate.interval.total_seconds() * 1000)) for rate in rates]
        self._bucket = InMemoryBucket(pyrate_rates)
        # Limiter will create the background task that clears old requests in the bucket
        self._limiter = Limiter(self._bucket)
        super().__init__(matchers=matchers)

    def try_acquire(self, request: Any, weight: int) -> None:
        if not self.matches(request):
            raise ValueError("Request does not match the policy")

        try:
            self._limiter.try_acquire(request, weight=weight)
        except BucketFullException as exc:
            item = self._limiter.bucket_factory.wrap_item(request, weight)
            assert isinstance(item, RateItem)

            with self._limiter.lock:
                time_to_wait = self._bucket.waiting(item)
                assert isinstance(time_to_wait, int)

                raise CallRateLimitHit(
                    error=str(exc.meta_info["error"]),
                    item=request,
                    weight=int(exc.meta_info["weight"]),
                    rate=str(exc.meta_info["rate"]),
                    time_to_wait=timedelta(milliseconds=time_to_wait),
                )

    def update(self, available_calls: Optional[int], call_reset_ts: Optional[datetime.datetime]) -> None:
        """Adjust call bucket to reflect the state of the API server

        :param available_calls:
        :param call_reset_ts:
        :return:
        """
        if available_calls is not None and call_reset_ts is None:  # we do our best to sync buckets with API
            if available_calls == 0:
                with self._limiter.lock:
                    items_to_add = self._bucket.count() < self._bucket.rates[0].limit
                    if items_to_add > 0:
                        now: int = TimeClock().now()  # type: ignore[no-untyped-call]
                        self._bucket.put(RateItem(name="dummy", timestamp=now, weight=items_to_add))
        # TODO: add support if needed, it might be that it is not possible to make a good solution for this case
        # if available_calls is not None and call_reset_ts is not None:
        #     ts = call_reset_ts.timestamp()


class AbstractAPIBudget(abc.ABC):
    """Interface to some API where a client allowed to have N calls per T interval.

    Important: APIBudget is not doing any API calls, the end user code is responsible to call this interface
        to respect call rate limitation of the API.

    It supports multiple policies applied to different group of requests. To distinct these groups we use RequestMatchers.
    Individual policy represented by MovingWindowCallRatePolicy and currently supports only moving window strategy.
    """

    @abc.abstractmethod
    def acquire_call(self, request: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        """Try to get a call from budget, will block by default

        :param request:
        :param block: when true (default) will block the current thread until call credit is available
        :param timeout: if set will limit maximum time in block, otherwise will wait until credit is available
        :raises: CallRateLimitHit - when no credits left and if timeout was set the waiting time exceed the timeout
        """

    @abc.abstractmethod
    def get_matching_policy(self, request: Any) -> Optional[AbstractCallRatePolicy]:
        """Find matching call rate policy for specific request"""

    @abc.abstractmethod
    def update_from_response(self, request: Any, response: Any) -> None:
        """Update budget information based on response from API

        :param request: the initial request that triggered this response
        :param response: response from the API
        """


class APIBudget(AbstractAPIBudget):
    """Default APIBudget implementation"""

    def __init__(self, policies: list[AbstractCallRatePolicy], maximum_attempts_to_acquire: int = 100000) -> None:
        """Constructor

        :param policies: list of policies in this budget
        :param maximum_attempts_to_acquire: number of attempts before throwing hit ratelimit exception, we put some big number here
         to avoid situations when many threads compete with each other for a few lots over a significant amount of time
        """

        self._policies = policies
        self._maximum_attempts_to_acquire = maximum_attempts_to_acquire

    def get_matching_policy(self, request: Any) -> Optional[AbstractCallRatePolicy]:
        for policy in self._policies:
            if policy.matches(request):
                return policy
        return None

    def acquire_call(self, request: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        """Try to get a call from budget, will block by default.
        Matchers will be called sequentially in the same order they were added.
        The first matcher that returns True will

        :param request:
        :param block: when true (default) will block the current thread until call credit is available
        :param timeout: if provided will limit maximum time in block, otherwise will wait until credit is available
        :raises: CallRateLimitHit - when no calls left and if timeout was set the waiting time exceed the timeout
        """

        policy = self.get_matching_policy(request)
        if policy:
            self._do_acquire(request=request, policy=policy, block=block, timeout=timeout)
        elif self._policies:
            logger.info("no policies matched with requests, allow call by default")

    def update_from_response(self, request: Any, response: Any) -> None:
        """Update budget information based on response from API

        :param request: the initial request that triggered this response
        :param response: response from the API
        """
        pass

    def _do_acquire(self, request: Any, policy: AbstractCallRatePolicy, block: bool, timeout: Optional[float]) -> None:
        """Internal method to try to acquire a call credit

        :param request:
        :param policy:
        :param block:
        :param timeout:
        """
        last_exception = None
        # sometimes we spend all budget before a second attempt, so we have few more here
        for attempt in range(1, self._maximum_attempts_to_acquire):
            try:
                policy.try_acquire(request, weight=1)
                return
            except CallRateLimitHit as exc:
                last_exception = exc
                if block:
                    if timeout is not None:
                        time_to_wait = min(timedelta(seconds=timeout), exc.time_to_wait)
                    else:
                        time_to_wait = exc.time_to_wait

                    time_to_wait = max(timedelta(0), time_to_wait)  # sometimes we get negative duration
                    logger.info("reached call limit %s. going to sleep for %s", exc.rate, time_to_wait)
                    time.sleep(time_to_wait.total_seconds())
                else:
                    raise

        if last_exception:
            logger.info("we used all %s attempts to acquire and failed", self._maximum_attempts_to_acquire)
            raise last_exception


class HttpAPIBudget(APIBudget):
    """Implementation of AbstractAPIBudget for HTTP"""

    def __init__(
        self,
        ratelimit_reset_header: str = "ratelimit-reset",
        ratelimit_remaining_header: str = "ratelimit-remaining",
        status_codes_for_ratelimit_hit: tuple[int] = (429,),
        **kwargs: Any,
    ):
        """Constructor

        :param ratelimit_reset_header: name of the header that has a timestamp of the next reset of call budget
        :param ratelimit_remaining_header: name of the header that has the number of calls left
        :param status_codes_for_ratelimit_hit: list of HTTP status codes that signal about rate limit being hit
        """
        self._ratelimit_reset_header = ratelimit_reset_header
        self._ratelimit_remaining_header = ratelimit_remaining_header
        self._status_codes_for_ratelimit_hit = status_codes_for_ratelimit_hit
        super().__init__(**kwargs)

    def update_from_response(self, request: Any, response: Any) -> None:
        policy = self.get_matching_policy(request)
        if not policy:
            return

        if isinstance(response, requests.Response):
            available_calls = self.get_calls_left_from_response(response)
            reset_ts = self.get_reset_ts_from_response(response)
            policy.update(available_calls=available_calls, call_reset_ts=reset_ts)

    def get_reset_ts_from_response(self, response: requests.Response) -> Optional[datetime.datetime]:
        if response.headers.get(self._ratelimit_reset_header):
            return datetime.datetime.fromtimestamp(int(response.headers[self._ratelimit_reset_header]))
        return None

    def get_calls_left_from_response(self, response: requests.Response) -> Optional[int]:
        if response.headers.get(self._ratelimit_remaining_header):
            return int(response.headers[self._ratelimit_remaining_header])

        if response.status_code in self._status_codes_for_ratelimit_hit:
            return 0

        return None


class LimiterMixin(MIXIN_BASE):
    """Mixin class that adds rate-limiting behavior to requests."""

    def __init__(
        self,
        api_budget: AbstractAPIBudget,
        **kwargs: Any,
    ):
        self._api_budget = api_budget
        super().__init__(**kwargs)  # type: ignore # Base Session doesn't take any kwargs

    def send(self, request: requests.PreparedRequest, **kwargs: Any) -> requests.Response:
        """Send a request with rate-limiting."""
        self._api_budget.acquire_call(request)
        response = super().send(request, **kwargs)
        self._api_budget.update_from_response(request, response)
        return response


class LimiterSession(LimiterMixin, requests.Session):
    """Session that adds rate-limiting behavior to requests."""


class CachedLimiterSession(requests_cache.CacheMixin, LimiterMixin, requests.Session):
    """Session class with caching and rate-limiting behavior."""
