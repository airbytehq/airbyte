# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import contextlib
import functools
from types import TracebackType
from typing import Callable, List, Optional, Union

import requests_mock
from airbyte_cdk.test.mock_http import HttpRequest, HttpRequestMatcher, HttpResponse


class HttpMocker(contextlib.ContextDecorator):
    """
    WARNING: This implementation only works if the lib used to perform HTTP requests is `requests`
    """

    def __init__(self) -> None:
        self._mocker = requests_mock.Mocker()
        self._matchers: List[HttpRequestMatcher] = []

    def __enter__(self) -> "HttpMocker":
        self._mocker.__enter__()
        return self

    def __exit__(self, exc_type: Optional[BaseException], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        self._mocker.__exit__(exc_type, exc_val, exc_tb)

    def _validate_all_matchers_called(self) -> None:
        for matcher in self._matchers:
            if not matcher.has_expected_match_count():
                raise ValueError(f"Invalid number of matches for `{matcher}`")

    def get(self, request: HttpRequest, responses: Union[HttpResponse, List[HttpResponse]]) -> None:
        """
        WARNING: Given multiple requests that are not mutually exclusive, the request will match the first one. This can happen in scenarios
        where the same request is added twice (in which case there will always be an exception because we will never match the second
        request) or in a case like this:
        ```
        http_mocker.get(HttpRequest(_A_URL, headers={"less_granular": "1", "more_granular": "2"}), <...>)
        http_mocker.get(HttpRequest(_A_URL, headers={"less_granular": "1"}), <...>)
        requests.get(_A_URL, headers={"less_granular": "1", "more_granular": "2"})
        ```
        In the example above, the matcher would match the second mock as requests_mock iterate over the matcher in reverse order (see
        https://github.com/jamielennox/requests-mock/blob/c06f124a33f56e9f03840518e19669ba41b93202/requests_mock/adapter.py#L246) even
        though the request sent is a better match for the first `http_mocker.get`.
        """
        if isinstance(responses, HttpResponse):
            responses = [responses]

        matcher = HttpRequestMatcher(request, len(responses))
        self._matchers.append(matcher)
        self._mocker.get(
            requests_mock.ANY,
            additional_matcher=self._matches_wrapper(matcher),
            response_list=[{"text": response.body, "status_code": response.status_code} for response in responses],
        )

    def _matches_wrapper(self, matcher: HttpRequestMatcher) -> Callable[[requests_mock.request._RequestObjectProxy], bool]:
        def matches(requests_mock_request: requests_mock.request._RequestObjectProxy) -> bool:
            # query_params are provided as part of `requests_mock_request.url`
            http_request = HttpRequest(requests_mock_request.url, query_params={}, headers=requests_mock_request.headers)
            return matcher.matches(http_request)

        return matches

    def __call__(self, f):  # type: ignore  # trying to type that using callables provides the error `incompatible with return type "_F" in supertype "ContextDecorator"`
        @functools.wraps(f)
        def wrapper(*args, **kwargs):  # type: ignore  # this is a very generic wrapper that does not need to be typed
            with self:
                assertion_error = None

                kwargs["http_mocker"] = self
                try:
                    result = f(*args, **kwargs)
                except requests_mock.NoMockAddress as no_mock_exception:
                    matchers_as_string = "\n\t".join(map(lambda matcher: str(matcher.request), self._matchers))
                    raise ValueError(
                        f"No matcher matches {no_mock_exception.args[0]} with headers `{no_mock_exception.request.headers}`. Matchers currently configured are:\n\t{matchers_as_string}"
                    ) from no_mock_exception
                except AssertionError as test_assertion:
                    assertion_error = test_assertion

                # We validate the matchers before raising the assertion error because we want to show the tester if a HTTP request wasn't
                # mocked correctly
                self._validate_all_matchers_called()
                if assertion_error:
                    raise assertion_error
                return result

        return wrapper
