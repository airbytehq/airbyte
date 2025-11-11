# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import contextlib
import functools
from collections import defaultdict
from enum import Enum
from types import TracebackType
from typing import Callable, Dict, Iterable, List, Optional, Union

import requests_mock

from airbyte_cdk.test.mock_http.matcher import HttpRequestMatcher
from airbyte_cdk.test.mock_http.request import HttpRequest
from airbyte_cdk.test.mock_http.response import HttpResponse


class SupportedHttpMethods(str, Enum):
    GET = "get"
    PATCH = "patch"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


class HttpMocker(contextlib.ContextDecorator):
    """
    WARNING 1: This implementation only works if the lib used to perform HTTP requests is `requests`.

    WARNING 2: Given multiple requests that are not mutually exclusive, the request will match the first one. This can happen in scenarios
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

    def __init__(self) -> None:
        self._mocker = requests_mock.Mocker()
        self._matchers: Dict[SupportedHttpMethods, List[HttpRequestMatcher]] = defaultdict(list)

    def __enter__(self) -> "HttpMocker":
        self._mocker.__enter__()
        return self

    def __exit__(
        self,
        exc_type: Optional[BaseException],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self._mocker.__exit__(exc_type, exc_val, exc_tb)

    def _validate_all_matchers_called(self) -> None:
        for matcher in self._get_matchers():
            if not matcher.has_expected_match_count():
                raise ValueError(f"Invalid number of matches for `{matcher}`")

    def _mock_request_method(
        self,
        method: SupportedHttpMethods,
        request: HttpRequest,
        responses: Union[HttpResponse, List[HttpResponse]],
    ) -> None:
        if isinstance(responses, HttpResponse):
            responses = [responses]

        matcher = HttpRequestMatcher(request, len(responses))
        if matcher in self._matchers[method]:
            raise ValueError(f"Request {matcher.request} already mocked")
        self._matchers[method].append(matcher)

        getattr(self._mocker, method)(
            requests_mock.ANY,
            additional_matcher=self._matches_wrapper(matcher),
            response_list=[
                {
                    self._get_body_field(response): response.body,
                    "status_code": response.status_code,
                    "headers": response.headers,
                }
                for response in responses
            ],
        )

    @staticmethod
    def _get_body_field(response: HttpResponse) -> str:
        return "text" if isinstance(response.body, str) else "content"

    def get(self, request: HttpRequest, responses: Union[HttpResponse, List[HttpResponse]]) -> None:
        self._mock_request_method(SupportedHttpMethods.GET, request, responses)

    def patch(
        self, request: HttpRequest, responses: Union[HttpResponse, List[HttpResponse]]
    ) -> None:
        self._mock_request_method(SupportedHttpMethods.PATCH, request, responses)

    def post(
        self, request: HttpRequest, responses: Union[HttpResponse, List[HttpResponse]]
    ) -> None:
        self._mock_request_method(SupportedHttpMethods.POST, request, responses)

    def put(self, request: HttpRequest, responses: Union[HttpResponse, List[HttpResponse]]) -> None:
        self._mock_request_method(SupportedHttpMethods.PUT, request, responses)

    def delete(
        self, request: HttpRequest, responses: Union[HttpResponse, List[HttpResponse]]
    ) -> None:
        self._mock_request_method(SupportedHttpMethods.DELETE, request, responses)

    @staticmethod
    def _matches_wrapper(
        matcher: HttpRequestMatcher,
    ) -> Callable[[requests_mock.request._RequestObjectProxy], bool]:
        def matches(requests_mock_request: requests_mock.request._RequestObjectProxy) -> bool:
            # query_params are provided as part of `requests_mock_request.url`
            http_request = HttpRequest(
                requests_mock_request.url,
                query_params={},
                headers=requests_mock_request.headers,
                body=requests_mock_request.body,
            )
            return matcher.matches(http_request)

        return matches

    def assert_number_of_calls(self, request: HttpRequest, number_of_calls: int) -> None:
        corresponding_matchers = list(
            filter(lambda matcher: matcher.request is request, self._get_matchers())
        )
        if len(corresponding_matchers) != 1:
            raise ValueError(
                f"Was expecting only one matcher to match the request but got `{corresponding_matchers}`"
            )

        assert corresponding_matchers[0].actual_number_of_matches == number_of_calls

    # trying to type that using callables provides the error `incompatible with return type "_F" in supertype "ContextDecorator"`
    def __call__(self, f):  # type: ignore
        @functools.wraps(f)
        def wrapper(*args, **kwargs):  # type: ignore  # this is a very generic wrapper that does not need to be typed
            with self:
                assertion_error = None

                kwargs["http_mocker"] = self
                try:
                    result = f(*args, **kwargs)
                except requests_mock.NoMockAddress as no_mock_exception:
                    matchers_as_string = "\n\t".join(
                        map(lambda matcher: str(matcher.request), self._get_matchers())
                    )
                    raise ValueError(
                        f"No matcher matches {no_mock_exception.args[0]} with headers `{no_mock_exception.request.headers}` "
                        f"and body `{no_mock_exception.request.body}`. "
                        f"Matchers currently configured are:\n\t{matchers_as_string}."
                    ) from no_mock_exception
                except AssertionError as test_assertion:
                    assertion_error = test_assertion

                # We validate the matchers before raising the assertion error because we want to show the tester if an HTTP request wasn't
                # mocked correctly
                try:
                    self._validate_all_matchers_called()
                except ValueError as http_mocker_exception:
                    # This seems useless as it catches ValueError and raises ValueError but without this, the prevailing error message in
                    # the output is the function call that failed the assertion, whereas raising `ValueError(http_mocker_exception)`
                    # like we do here provides additional context for the exception.
                    raise ValueError(http_mocker_exception) from None
                if assertion_error:
                    raise assertion_error
                return result

        return wrapper

    def _get_matchers(self) -> Iterable[HttpRequestMatcher]:
        for matchers in self._matchers.values():
            yield from matchers

    def clear_all_matchers(self) -> None:
        """Clears all stored matchers by resetting the _matchers list to an empty state."""
        self._matchers = defaultdict(list)
