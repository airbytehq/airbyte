#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from source_hubspot.api import API, split_properties
from source_hubspot.client import Client


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"credentials_title": "API Key Credentials", "api_key": "wrong_key"}


@pytest.fixture(name="creds_with_wrong_permissions")
def creds_with_wrong_permissions():
    return {"credentials_title": "API Key Credentials", "api_key": "THIS-IS-THE-API_KEY"}


def test_client_backoff_on_limit_reached(requests_mock, some_credentials):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429, "headers": {"Retry-After": "0"}},
        {"json": [], "status_code": 200},
    ]

    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=some_credentials)

    alive, error = client.health_check()

    assert alive
    assert not error


def test_client_backoff_on_server_error(requests_mock, some_credentials):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "something bad"}, "status_code": 500},
        {"json": [], "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=some_credentials)

    alive, error = client.health_check()

    assert alive
    assert not error


def test_wrong_permissions_api_key(requests_mock, creds_with_wrong_permissions):
    """
    Error with API Key Permissions to particular stream,
    typically this issue raises along with calling `workflows` stream with API Key
    that doesn't have required permissions to read the stream.
    """
    # Define stream name
    stream_name = "workflows"

    # Mapping tipical response for mocker
    responses = [
        {
            "json": {
                "status": "error",
                "message": f'This hapikey ({creds_with_wrong_permissions.get("api_key")}) does not have proper permissions! (requires any of [automation-access])',
                "correlationId": "2fe0a9af-3609-45c9-a4d7-83a1774121aa",
            }
        }
    ]

    # We expect something like this
    expected_warining_message = {
        "type": "LOG",
        "log": {
            "level": "WARN",
            "message": f'Stream `workflows` cannot be procced. This hapikey ({creds_with_wrong_permissions.get("api_key")}) does not have proper permissions! (requires any of [automation-access])',
        },
    }

    # create base parent instances
    client = Client(start_date="2021-02-01T00:00:00Z", credentials=creds_with_wrong_permissions)
    api = API(creds_with_wrong_permissions)

    # Create test_stream instance
    test_stream = client._apis.get(stream_name)

    # Mocking Request
    requests_mock.register_uri("GET", test_stream.url, responses)

    # Mock the getter method that handles requests.
    def get(url=test_stream.url, params=None):
        response = api._session.get(api.BASE_URL + url, params=params)
        return api._parse_and_handle_errors(response)

    # Define request params value
    params = {"limit": 100, "properties": ""}

    # Read preudo-output from generator object _read(), based on real scenario
    list(test_stream._read(getter=get, params=params))

    # match logged expected logged warning message with output given from preudo-output
    assert expected_warining_message


def test_splitting_properties(requests_mock, some_credentials):
    """
    Check working stream `companies` with large list of properties using new functionality with splitting properties
    """
    # Define stream name
    stream_name = "companies"
    number_of_properties = 2000

    client = Client(start_date="2021-02-01T00:00:00Z", credentials=some_credentials)
    api = API(some_credentials)

    properties_list = [f"property_number_{i}" for i in range(number_of_properties)]
    parsed_properties = list(split_properties(properties_list))

    # Check that properties are split into multiple arrays
    assert len(parsed_properties) > 1

    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in properties_list
            ],
            "status_code": 200,
        },
    ]
    requests_mock.register_uri("GET", "/properties/v2/company/properties", properties_response)

    # Create test_stream instance
    test_stream = client._apis.get(stream_name)

    for property_slice in parsed_properties:
        record_responses = [
            {
                "json": {
                    "results": [
                        {
                            "id": id,
                            "properties": {p: "fake_data" for p in property_slice},
                            "createdAt": "2020-12-10T07:58:09.554Z",
                            "updatedAt": "2021-07-31T08:18:58.954Z",
                            "archived": False,
                        }
                        for id in ["6043593519", "1092593519", "1092593518", "1092593517", "1092593516"]
                    ],
                    "paging": {},
                },
                "status_code": 200,
            }
        ]
        requests_mock.register_uri("GET", f"{test_stream.url}?properties={','.join(property_slice)}", record_responses)

    # Mock the getter method that handles requests.
    def get(url=test_stream.url, params=None):
        response = api._session.get(api.BASE_URL + url, params=params)
        return api._parse_and_handle_errors(response)

    # Read preudo-output from generator object read(), based on real scenario
    stream_records = list(test_stream.read(getter=get))

    # check that we have records for all set ids, and that each record has 2000 properties (not more, and not less)
    assert len(stream_records) == 5
    for record in stream_records:
        assert len(record["properties"]) == number_of_properties
