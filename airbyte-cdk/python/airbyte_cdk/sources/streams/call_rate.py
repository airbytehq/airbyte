import abc
from typing import Any, Optional

import requests

from pyrate_limiter import Limiter, InMemoryBucket
from pyrate_limiter import Rate as OrgRate, Duration as OrgDuration

Duration = OrgDuration
Rate = OrgRate


class AbstractCallRatePolicy(abc.ABC):
    """
    Should be configurable with different rules, like N per M for endpoint X

    then we ask for endpoint X if we can request
    """

    @abc.abstractmethod
    def try_acquire(self, request: Any, weight: int):
        """ Try to acquire request

        :param request: request object representing single call to API
        :param weight: number of requests to deduct from credit
        :return:
        """


class CallRatePolicy(AbstractCallRatePolicy):
    """
    Policy to control requests rate implemented on top of PyRateLimiter lib.

    TODO: periodical clean up of the bucket
    TODO: support static window strategy, not only moving window
    TODO: support policy without limitations
    """
    def __init__(self, rates: list[Rate]):
        """ Constructor

        :param rates: list of rates, the order is important and must be ascending
        """
        self._bucket = InMemoryBucket(rates)
        self._limiter = Limiter(self._bucket)

    def try_acquire(self, request: Any, weight: int = 1):
        self._limiter.try_acquire(request)


class RequestMatcher:
    """Callable that help to match request object with call rate policies."""
    def __call__(self, request: Any):
        pass


class HttpRequestMatcher(RequestMatcher):
    """Simple implementation of RequestMatcher for http requests case"""
    def __init__(self, method: str = None, url: str = None):
        self._method = method
        self._url = url

    def __call__(self, request: Any) -> bool:
        if isinstance(request, (requests.Request, requests.PreparedRequest)):
            if self._method is not None:
                if request.method != self._method:
                    return False
            if self._url is not None:
                if request.url != self._url:
                    return False
            return True

        return False


class AbstractAPIBudget(abc.ABC):
    """ Interface to some API where client allowed to have N calls per T interval.

    Important: APIBudget is not doing any API calls, the end user code is responsible to call this interface
        to respect call rate limitation of the API.

    It supports multiple policies applied to different group of requests. To distinct these groups we use RequestMatchers.
    Individual policy represented by CallRatePolicy and currently supports only moving window strategy.
    """
    @abc.abstractmethod
    def add_policy(self, request_matcher: RequestMatcher, policy: CallRatePolicy):
        """ Add policy for calls

        :param request_matcher: callable to match request object with corresponding policy
        :param policy: to acquire calls
        :return:
        """

    @abc.abstractmethod
    def acquire_call(self, request: Any, wait: Optional[int] = None) -> bool:
        """ Try to get a call from budget

        :param request:
        :param wait: if set >0 will wait number of seconds; if wait == 0 - will return immediately; if wait is None (default) - will block
        :return: True if call was acquired, False - otherwise
        """


class APIBudget(AbstractAPIBudget):
    def __init__(self):
        self._policies: list[tuple[RequestMatcher, CallRatePolicy]] = []

    def add_policy(self, request_matcher: RequestMatcher, policy: CallRatePolicy):
        self._policies.append((request_matcher, policy))

    def acquire_call(self, request: Any, wait: Optional[int] = None) -> bool:
        for matcher, policy in self._policies:
            if matcher(request):
                if policy.try_acquire(request):
                    return True
        return False
