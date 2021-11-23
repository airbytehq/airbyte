#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from functools import partial

import pytest
from source_hubspot.api import API, PROPERTIES_PARAM_MAX_LENGTH, split_properties
from source_hubspot.client import Client

NUMBER_OF_PROPERTIES = 2000


@pytest.fixture(name="some_credentials")
def some_credentials_fixture():
    return {"credentials_title": "API Key Credentials", "api_key": "wrong_key"}


@pytest.fixture(name="creds_with_wrong_permissions")
def creds_with_wrong_permissions():
    return {"credentials_title": "API Key Credentials", "api_key": "THIS-IS-THE-API_KEY"}


@pytest.fixture(name="fake_properties_list")
def fake_properties_list():
    return [f"property_number_{i}" for i in range(NUMBER_OF_PROPERTIES)]


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


class TestSplittingPropertiesFunctionality:
    BASE_OBJECT_BODY = {
        "createdAt": "2020-12-10T07:58:09.554Z",
        "updatedAt": "2021-07-31T08:18:58.954Z",
        "archived": False,
    }

    @pytest.fixture
    def client(self, some_credentials):
        return Client(start_date="2021-02-01T00:00:00Z", credentials=some_credentials)

    @pytest.fixture
    def api(self, some_credentials):
        return API(some_credentials)

    @staticmethod
    def set_mock_properties(requests_mock, url, fake_properties_list):
        properties_response = [
            {
                "json": [
                    {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                    for property_name in fake_properties_list
                ],
                "status_code": 200,
            },
        ]
        requests_mock.register_uri("GET", url, properties_response)

    # Mock the getter method that handles requests.
    def get(self, url, api, params=None):
        response = api._session.get(api.BASE_URL + url, params=params)
        return api._parse_and_handle_errors(response)

    def test_splitting_properties(self, fake_properties_list):
        """
        Check that properties are split into multiple arrays
        """
        for slice_property in split_properties(fake_properties_list):
            slice_length = [len(item) for item in slice_property]
            assert sum(slice_length) <= PROPERTIES_PARAM_MAX_LENGTH

    def test_stream_with_splitting_properties(self, requests_mock, client, api, fake_properties_list):
        """
        Check working stream `companies` with large list of properties using new functionality with splitting properties
        """
        # Define stream name
        stream_name = "companies"

        parsed_properties = list(split_properties(fake_properties_list))
        self.set_mock_properties(requests_mock, "/properties/v2/company/properties", fake_properties_list)

        # Create test_stream instance
        test_stream = client._apis.get(stream_name)
        record_ids_paginated = [list(map(str, range(100))), list(map(str, range(100, 150, 1)))]

        after_id = None
        for id_list in record_ids_paginated:
            for property_slice in parsed_properties:
                record_responses = [
                    {
                        "json": {
                            "results": [
                                {**self.BASE_OBJECT_BODY, **{"id": id, "properties": {p: "fake_data" for p in property_slice}}}
                                for id in id_list
                            ],
                            "paging": {"next": {"after": id_list[-1]}} if len(id_list) == 100 else {},
                        },
                        "status_code": 200,
                    }
                ]
                requests_mock.register_uri(
                    "GET",
                    f"{test_stream.url}?limit=100&properties={','.join(property_slice)}{f'&after={after_id}' if after_id else ''}",
                    record_responses,
                )
            after_id = id_list[-1]

        # Read preudo-output from generator object read(), based on real scenario
        stream_records = list(test_stream.read(getter=partial(self.get, test_stream.url, api=api)))

        # check that we have records for all set ids, and that each record has 2000 properties (not more, and not less)
        assert len(stream_records) == sum([len(ids) for ids in record_ids_paginated])
        for record in stream_records:
            assert len(record["properties"]) == NUMBER_OF_PROPERTIES

    def test_stream_with_splitting_properties_with_pagination(self, requests_mock, client, api, fake_properties_list):
        """
        Check working stream `products` with large list of properties using new functionality with splitting properties
        """
        stream_name = "products"

        parsed_properties = list(split_properties(fake_properties_list))
        self.set_mock_properties(requests_mock, "/properties/v2/product/properties", fake_properties_list)
        test_stream = client._apis.get(stream_name)

        for property_slice in parsed_properties:
            record_responses = [
                {
                    "json": {
                        "results": [
                            {**self.BASE_OBJECT_BODY, **{"id": id, "properties": {p: "fake_data" for p in property_slice}}}
                            for id in ["6043593519", "1092593519", "1092593518", "1092593517", "1092593516"]
                        ],
                        "paging": {},
                    },
                    "status_code": 200,
                }
            ]
            requests_mock.register_uri("GET", f"{test_stream.url}?properties={','.join(property_slice)}", record_responses)

        stream_records = list(test_stream.read(getter=partial(self.get, test_stream.url, api=api)))

        assert len(stream_records) == 5
        for record in stream_records:
            assert len(record["properties"]) == NUMBER_OF_PROPERTIES

    def test_stream_with_splitting_properties_with_new_record(self, requests_mock, client, api, fake_properties_list):
        """
        Check working stream `workflows` with large list of properties using new functionality with splitting properties
        """
        stream_name = "deals"

        parsed_properties = list(split_properties(fake_properties_list))
        self.set_mock_properties(requests_mock, "/properties/v2/deal/properties", fake_properties_list)

        # Create test_stream instance
        test_stream = client._apis.get(stream_name)

        ids_list = ["6043593519", "1092593519", "1092593518", "1092593517", "1092593516"]
        for property_slice in parsed_properties:
            record_responses = [
                {
                    "json": {
                        "results": [
                            {**self.BASE_OBJECT_BODY, **{"id": id, "properties": {p: "fake_data" for p in property_slice}}}
                            for id in ids_list
                        ],
                        "paging": {},
                    },
                    "status_code": 200,
                }
            ]
            requests_mock.register_uri("GET", f"{test_stream.url}?properties={','.join(property_slice)}", record_responses)
            ids_list.append("1092593513")

        stream_records = list(test_stream.read(getter=partial(self.get, test_stream.url, api=api)))

        assert len(stream_records) == 6
