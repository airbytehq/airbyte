#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture():
    return {
        "api_key": "test_api_key"
    }


@fixture(name="mock_responses")
def mock_responses():
    return {
        "Users": {
            "users": [
                {
                    "id": 1,
                    "first_name": "Chris",
                    "last_name": "James",
                    "display_name": "Chris James",
                    "email": "chris@example.com",
                    "user_type_id": 1
                }
            ]
        }
    }


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None):
        if response is None:
            response = {}

        url = f"https://api.rm.smartsheet.com/api/v1/{path}"
        requests_mock.get(url, json=response)

    return _mock_stream
