#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from http import HTTPStatus
from unittest.mock import MagicMock

import pendulum
import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode, Type
from source_hubspot.errors import HubspotRateLimited
from source_hubspot.helpers import APIv3Property
from source_hubspot.source import SourceHubspot
from source_hubspot.streams import API, Companies, Deals, Engagements, Products, Stream, Workflows

from .utils import read_full_refresh, read_incremental

NUMBER_OF_PROPERTIES = 2000

logger = logging.getLogger("test_client")


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_check_connection_ok(requests_mock, config):
    responses = [
        {"json": [], "status_code": 200},
    ]

    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    ok, error_msg = SourceHubspot().check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_empty_config(config):
    config = {}

    with pytest.raises(KeyError):
        SourceHubspot().check_connection(logger, config=config)


def test_check_connection_invalid_config(config):
    config.pop("start_date")

    with pytest.raises(KeyError):
        SourceHubspot().check_connection(logger, config=config)


def test_check_connection_exception(config):
    ok, error_msg = SourceHubspot().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_streams(config):
    streams = SourceHubspot().streams(config)

    assert len(streams) == 25


def test_check_credential_title_exception(config):
    config["credentials"].pop("credentials_title")

    with pytest.raises(Exception):
        SourceHubspot().check_connection(logger, config=config)


def test_parse_and_handle_errors(some_credentials):
    response = MagicMock()
    response.status_code = HTTPStatus.TOO_MANY_REQUESTS

    with pytest.raises(HubspotRateLimited):
        API(some_credentials)._parse_and_handle_errors(response)


def test_convert_datetime_to_string():
    pendulum_time = pendulum.now()

    assert Stream._convert_datetime_to_string(pendulum_time, declared_format="date")
    assert Stream._convert_datetime_to_string(pendulum_time, declared_format="date-time")


def test_cast_datetime(common_params, caplog):
    field_value = pendulum.now()
    field_name = "curent_time"

    Companies(**common_params)._cast_datetime(field_name, field_value)

    expected_warining_message = {
        "type": "LOG",
        "log": {
            "level": "WARN",
            "message": f"Couldn't parse date/datetime string in {field_name}, trying to parse timestamp... Field value: {field_value}. Ex: argument of type 'DateTime' is not iterable",
        },
    }
    assert expected_warining_message["log"]["message"] in caplog.text


def test_check_connection_backoff_on_limit_reached(requests_mock, config):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429, "headers": {"Retry-After": "0"}},
        {"json": [], "status_code": 200},
    ]

    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    source = SourceHubspot()
    alive, error = source.check_connection(logger=logger, config=config)

    assert alive
    assert not error


def test_check_connection_backoff_on_server_error(requests_mock, config):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "something bad"}, "status_code": 500},
        {"json": [], "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    source = SourceHubspot()
    alive, error = source.check_connection(logger=logger, config=config)

    assert alive
    assert not error


def test_wrong_permissions_api_key(requests_mock, creds_with_wrong_permissions, common_params, caplog):
    """
    Error with API Key Permissions to particular stream,
    typically this issue raises along with calling `workflows` stream with API Key
    that doesn't have required permissions to read the stream.
    """

    # Mapping tipical response for mocker
    json = {
        "status": "error",
        "message": f'This hapikey ({creds_with_wrong_permissions.get("api_key")}) does not have proper permissions! (requires any of [automation-access])',
        "correlationId": "2fe0a9af-3609-45c9-a4d7-83a1774121aa",
    }

    # We expect something like this
    expected_warining_message = {
        "type": "LOG",
        "log": {
            "level": "WARN",
            "message": f'Stream `workflows` cannot be procced. This hapikey ({creds_with_wrong_permissions.get("api_key")}) does not have proper permissions! (requires any of [automation-access])',
        },
    }

    # Create test_stream instance
    test_stream = Workflows(**common_params)

    # Mocking Request
    requests_mock.register_uri("GET", test_stream.url, json=json, status_code=403)
    records = list(test_stream.read_records(sync_mode=SyncMode.full_refresh))

    # match logged expected logged warning message with output given from preudo-output
    assert expected_warining_message["log"]["message"] in caplog.text
    assert not records


class TestSplittingPropertiesFunctionality:
    BASE_OBJECT_BODY = {
        "createdAt": "2020-12-10T07:58:09.554Z",
        "updatedAt": "2021-07-31T08:18:58.954Z",
        "archived": False,
    }

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

    def test_stream_with_splitting_properties(self, requests_mock, api, fake_properties_list, common_params):
        """
        Check working stream `companies` with large list of properties using new functionality with splitting properties
        """
        test_stream = Companies(**common_params)

        parsed_properties = list(APIv3Property(fake_properties_list).split())
        self.set_mock_properties(requests_mock, "/properties/v2/company/properties", fake_properties_list)

        record_ids_paginated = [list(map(str, range(100))), list(map(str, range(100, 150, 1)))]

        test_stream._sync_mode = SyncMode.full_refresh
        test_stream_url = test_stream.url
        test_stream._sync_mode = None

        after_id = None
        for id_list in record_ids_paginated:
            for property_slice in parsed_properties:
                record_responses = [
                    {
                        "json": {
                            "results": [
                                {**self.BASE_OBJECT_BODY, **{"id": id, "properties": {p: "fake_data" for p in property_slice.properties}}}
                                for id in id_list
                            ],
                            "paging": {"next": {"after": id_list[-1]}} if len(id_list) == 100 else {},
                        },
                        "status_code": 200,
                    }
                ]
                prop_key, prop_val = next(iter(property_slice.as_url_param().items()))
                requests_mock.register_uri(
                    "GET",
                    f"{test_stream_url}?limit=100&{prop_key}={prop_val}{f'&after={after_id}' if after_id else ''}",
                    record_responses,
                )
            after_id = id_list[-1]

        # Read preudo-output from generator object
        stream_records = read_full_refresh(test_stream)

        # check that we have records for all set ids, and that each record has 2000 properties (not more, and not less)
        assert len(stream_records) == sum([len(ids) for ids in record_ids_paginated])
        for record in stream_records:
            assert len(record["properties"]) == NUMBER_OF_PROPERTIES

    def test_stream_with_splitting_properties_with_pagination(self, requests_mock, common_params, api, fake_properties_list):
        """
        Check working stream `products` with large list of properties using new functionality with splitting properties
        """

        parsed_properties = list(APIv3Property(fake_properties_list).split())
        self.set_mock_properties(requests_mock, "/properties/v2/product/properties", fake_properties_list)

        test_stream = Products(**common_params)

        for property_slice in parsed_properties:
            record_responses = [
                {
                    "json": {
                        "results": [
                            {**self.BASE_OBJECT_BODY, **{"id": id, "properties": {p: "fake_data" for p in property_slice.properties}}}
                            for id in ["6043593519", "1092593519", "1092593518", "1092593517", "1092593516"]
                        ],
                        "paging": {},
                    },
                    "status_code": 200,
                }
            ]
            prop_key, prop_val = next(iter(property_slice.as_url_param().items()))
            requests_mock.register_uri("GET", f"{test_stream.url}?{prop_key}={prop_val}", record_responses)

        stream_records = list(test_stream.read_records(sync_mode=SyncMode.incremental))

        assert len(stream_records) == 5
        for record in stream_records:
            assert len(record["properties"]) == NUMBER_OF_PROPERTIES

    def test_stream_with_splitting_properties_with_new_record(self, requests_mock, common_params, api, fake_properties_list):
        """
        Check working stream `workflows` with large list of properties using new functionality with splitting properties
        """

        parsed_properties = list(APIv3Property(fake_properties_list).split())
        self.set_mock_properties(requests_mock, "/properties/v2/deal/properties", fake_properties_list)

        test_stream = Deals(**common_params)

        ids_list = ["6043593519", "1092593519", "1092593518", "1092593517", "1092593516"]
        for property_slice in parsed_properties:
            record_responses = [
                {
                    "json": {
                        "results": [
                            {**self.BASE_OBJECT_BODY, **{"id": id, "properties": {p: "fake_data" for p in property_slice.properties}}}
                            for id in ids_list
                        ],
                        "paging": {},
                    },
                    "status_code": 200,
                }
            ]
            test_stream._sync_mode = SyncMode.full_refresh
            prop_key, prop_val = next(iter(property_slice.as_url_param().items()))
            requests_mock.register_uri("GET", f"{test_stream.url}?{prop_key}={prop_val}", record_responses)
            test_stream._sync_mode = None
            ids_list.append("1092593513")

        stream_records = read_full_refresh(test_stream)

        assert len(stream_records) == 6


@pytest.fixture(name="configured_catalog")
def configured_catalog_fixture():
    configured_catalog = {
        "streams": [
            {
                "stream": {
                    "name": "quotes",
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh", "incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["updatedAt"],
                },
                "sync_mode": "incremental",
                "cursor_field": ["updatedAt"],
                "destination_sync_mode": "append",
            }
        ]
    }
    return ConfiguredAirbyteCatalog.parse_obj(configured_catalog)


def test_it_should_not_read_quotes_stream_if_it_does_not_exist_in_client(oauth_config, configured_catalog):
    """
    If 'quotes' stream is not in the client, it should skip it.
    """
    source = SourceHubspot()

    all_records = list(source.read(logger, config=oauth_config, catalog=configured_catalog, state=None))
    records = [record for record in all_records if record.type == Type.RECORD]
    assert not records


def test_search_based_stream_should_not_attempt_to_get_more_than_10k_records(requests_mock, common_params, fake_properties_list):
    """
    If there are more than 10,000 records that would be returned by the Hubspot search endpoint,
    the CRMSearchStream instance should stop at the 10Kth record
    """

    responses = [
        {
            "json": {
                "results": [{"id": f"{y}", "updatedAt": "2022-02-25T16:43:11Z"} for y in range(100)],
                "paging": {
                    "next": {
                        "after": f"{x * 100}",
                    }
                },
            },
            "status_code": 200,
        }
        for x in range(1, 101)
    ]
    # After reaching 10K records, it performs a new search query.
    responses.extend(
        [
            {
                "json": {
                    "results": [{"id": f"{y}", "updatedAt": "2022-03-01T00:00:00Z"} for y in range(100)],
                    "paging": {
                        "next": {
                            "after": f"{x * 100}",
                        }
                    },
                },
                "status_code": 200,
            }
            for x in range(1, 10)
        ]
    )
    # Last page... it does not have paging->next->after
    responses.append(
        {
            "json": {"results": [{"id": f"{y}", "updatedAt": "2022-03-01T00:00:00Z"} for y in range(100)], "paging": {}},
            "status_code": 200,
        }
    )

    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]

    # Create test_stream instance with some state
    test_stream = Companies(**common_params)
    test_stream._init_sync = pendulum.parse("2022-02-24T16:43:11Z")
    test_stream.state = {"updatedAt": "2022-02-24T16:43:11Z"}

    # Mocking Request
    test_stream._sync_mode = SyncMode.incremental
    requests_mock.register_uri("POST", test_stream.url, responses)
    test_stream._sync_mode = None
    requests_mock.register_uri("GET", "/properties/v2/company/properties", properties_response)
    requests_mock.register_uri("POST", "/crm/v4/associations/company/contacts/batch/read", [{"status_code": 200, "json": {"results": []}}])

    records, _ = read_incremental(test_stream, {})
    # The stream should not attempt to get more than 10K records.
    # Instead, it should use the new state to start a new search query.
    assert len(records) == 11000
    assert test_stream.state["updatedAt"] == test_stream._init_sync.to_iso8601_string()


def test_engagements_stream_pagination_works(requests_mock, common_params):
    """
    Tests the engagements stream handles pagination correctly, for both
    full_refresh and incremental sync modes.
    """

    # Mocking Request
    requests_mock.register_uri(
        "GET",
        "/engagements/v1/engagements/paged?count=250",
        [
            {
                "json": {
                    "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234593251}} for y in range(250)],
                    "hasMore": True,
                    "offset": 250,
                },
                "status_code": 200,
            },
            {
                "json": {
                    "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234593251}} for y in range(250, 500)],
                    "hasMore": True,
                    "offset": 500,
                },
                "status_code": 200,
            },
            {
                "json": {
                    "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234595251}} for y in range(500, 600)],
                    "hasMore": False,
                },
                "status_code": 200,
            },
        ],
    )

    requests_mock.register_uri(
        "GET",
        "/engagements/v1/engagements/recent/modified?count=100",
        [
            {
                "json": {
                    "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234595252}} for y in range(100)],
                    "hasMore": True,
                    "offset": 100,
                },
                "status_code": 200,
            },
            {
                "json": {
                    "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234595252}} for y in range(100, 200)],
                    "hasMore": True,
                    "offset": 200,
                },
                "status_code": 200,
            },
            {
                "json": {
                    "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234595252}} for y in range(200, 250)],
                    "hasMore": False,
                },
                "status_code": 200,
            },
        ],
    )

    # Create test_stream instance for full refresh.
    test_stream = Engagements(**common_params)

    records = read_full_refresh(test_stream)
    # The stream should handle pagination correctly and output 600 records.
    assert len(records) == 600
    assert test_stream.state["lastUpdated"] == int(test_stream._init_sync.timestamp() * 1000)

    test_stream = Engagements(**common_params)
    records, _ = read_incremental(test_stream, {})
    # The stream should handle pagination correctly and output 250 records.
    assert len(records) == 250
    assert test_stream.state["lastUpdated"] == int(test_stream._init_sync.timestamp() * 1000)


def test_incremental_engagements_stream_stops_at_10K_records(requests_mock, common_params, fake_properties_list):
    """
    If there are more than 10,000 engagements that would be returned by the Hubspot recent engagements endpoint,
    the Engagements instance should stop at the 10Kth record.
    """

    responses = [
        {
            "json": {
                "results": [{"engagement": {"id": f"{y}", "lastUpdated": 1641234595252}} for y in range(100)],
                "hasMore": True,
                "offset": x * 100,
            },
            "status_code": 200,
        }
        for x in range(1, 102)
    ]

    # Create test_stream instance with some state
    test_stream = Engagements(**common_params)
    test_stream.state = {"lastUpdated": 1641234595251}
    # Mocking Request
    requests_mock.register_uri("GET", "/engagements/v1/engagements/recent/modified?count=100", responses)
    records, _ = read_incremental(test_stream, {})
    # The stream should not attempt to get more than 10K records.
    assert len(records) == 10000
    assert test_stream.state["lastUpdated"] == int(test_stream._init_sync.timestamp() * 1000)
