#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture():
    return {"credentials": {"personal_access_token": "TOKEN"}}


@fixture(name="mock_response")
def mock_response():
    return {
        "data": [{"gid": "gid", "resource_type": "resource_type", "name": "name"}],
        "next_page": {"offset": "offset", "path": "path", "uri": "uri"},
    }


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None):
        if response is None:
            response = {}

        url = f"https://app.asana.com/api/1.0/{path}"
        requests_mock.get(url, json=response)

    return _mock_stream
