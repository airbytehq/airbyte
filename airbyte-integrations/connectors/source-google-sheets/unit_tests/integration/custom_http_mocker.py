# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Dict
from urllib.parse import parse_qsl, unquote, urlencode, urlunparse

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.request import HttpRequest
from httplib2 import Response


def parse_and_transform(parse_result_str: str):
    """
    Parse the input string representation of a HttpRequest transform it into the URL.
    """
    # Extract the ParseResult portion only
    parse_result_part = parse_result_str.split("ParseResult(", 1)[1].split(")", 1)[0]

    # Convert the ParseResult string into a dictionary
    components = eval(f"dict({parse_result_part})")

    # Reconstruct the URL
    url = urlunparse((
        components["scheme"],
        components["netloc"],
        components["path"],
        components["params"],
        components["query"],
        components["fragment"],
    ))

    return url


class CustomHttpMocker:
    """
    This is a limited mocker for usage with httplib2.Http.request
    It has a similar interface to airbyte HttpMocker.get() method such than when we move this connector to manifest only with
    a http retriever we will be able to substitute CustomHttpMocker => HttpMocker in out integration testing with minimal changes.

    e.g.
        def test_any_test(self) -> None:
            http_mocker = CustomHttpMocker()
            http_mocker.get(
                RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
                HttpResponse(json.dumps({}), 200)
            )

            with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
               ... the rest of your implementation

        now when the streams use a http retriever we can test like:

        @HttpMocker()
        def test_any_test(self, http_mocker: HttpMocker) -> None:
            http_mocker.get(
                RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
                HttpResponse(json.dumps({}), 200)
            )

            ... the rest of your implementation

    Note: there is only support for get method and url matching ignoring the body but this is enough for the current test set.
    """
    requests_mapper: Dict = {}

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
