# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import requests


def create_requests_response(requests_mock, status_code, json) -> requests.Response:
    """
    Since the error handlers expect requests.Response object, the easiest way to mock them is to use the requests_mock library
    """
    dummy_url = "https://dummy_url.com/"
    requests_mock.get(
        dummy_url,
        status_code=status_code,
        json=json,
    )
    return requests.get(dummy_url)
