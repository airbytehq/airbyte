# Copyright (c) 2025 Airbyte, Inc., all rights reserved.


from functools import wraps
from typing import Dict
from unittest.mock import patch
from urllib.parse import parse_qsl, unquote, urlencode, urlunparse

from httplib2 import Response

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.request import HttpRequest


def parse_and_transform(parse_result_str: str):
    """
    Parse the input string representation of a HttpRequest transform it into the URL.
    """
    parse_result_part = parse_result_str.split("ParseResult(", 1)[1].split(")", 1)[0]

    # Convert the ParseResult string into a dictionary
    components = eval(f"dict({parse_result_part})")

    url = urlunparse(
        (
            components["scheme"],
            components["netloc"],
            components["path"],
            components["params"],
            components["query"],
            components["fragment"],
        )
    )

    return url


class CustomHttpMocker:
    """
    This is a limited mocker for usage with httplib2.Http.request
    It has a similar interface to airbyte HttpMocker such than when we move this connector to low-code only with
    a http retriever we will be able to substitute CustomHttpMocker => HttpMocker in out integration testing with minimal changes.

    Note: there is only support for get and post method and url matching ignoring the body but this is enough for the current test set.
    """

    requests_mapper: Dict = {}

    def post(self, request: HttpRequest, response: HttpResponse):
        custom_response = (Response({"status": response.status_code}), response.body.encode("utf-8"))
        uri = parse_and_transform(str(request))
        decoded_url = unquote(uri)
        self.requests_mapper[("POST", decoded_url)] = custom_response

    def get(self, request: HttpRequest, response: HttpResponse):
        custom_response = (Response({"status": response.status_code}), response.body.encode("utf-8"))
        uri = parse_and_transform(str(request))
        decoded_url = unquote(uri)
        self.requests_mapper[("GET", decoded_url)] = custom_response

    def mock_request(self, uri, method="GET", body=None, headers=None, **kwargs):
        decoded_url = unquote(uri)
        mocked_response = self.requests_mapper.get((method, decoded_url))
        if not mocked_response:
            raise Exception(f"Mock response not found {uri} {method}")
        return mocked_response

    # trying to type that using callables provides the error `incompatible with return type "_F" in supertype "ContextDecorator"`
    def __call__(self, test_func):  # type: ignore
        @wraps(test_func)
        def wrapper(*args, **kwargs):  # type: ignore  # this is a very generic wrapper that does not need to be typed
            kwargs["http_mocker"] = self

            with patch("httplib2.Http.request", side_effect=self.mock_request):
                return test_func(*args, **kwargs)

        return wrapper
