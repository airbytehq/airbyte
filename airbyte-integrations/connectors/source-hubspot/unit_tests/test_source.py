#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from datetime import timedelta
from urllib.parse import urlencode

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import discover
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .conftest import find_stream, get_source, mock_dynamic_schema_requests_with_skip, read_from_stream
from .utils import read_full_refresh, read_incremental


NUMBER_OF_PROPERTIES = 2000

logger = logging.getLogger("test_client")


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_check_connection_ok(requests_mock, config):
    responses = [
        {
            "json": [
                {
                    "name": "hs__migration_soft_delete",
                    "type": "enumeration",
                }
            ],
            "status_code": 200,
        },
    ]

    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", responses)
    requests_mock.register_uri("GET", "/crm/v3/objects/contact", {})
    ok, error_msg = get_source(config).check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_empty_config(caplog):
    config = {}
    get_source(config).check_connection(logger, config=config)
    assert "KeyError: ['credentials', 'credentials_title']" in caplog.records[0].message
    assert caplog.records[0].levelname == "ERROR"


def test_check_connection_exception(config):
    ok, error_msg = get_source(config).check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_bad_request_exception(requests_mock, config_invalid_client_id):
    responses = [
        {"json": {"message": "invalid client_id"}, "status_code": 400},
    ]
    requests_mock.register_uri("POST", "/oauth/v1/token", responses)
    ok, error_msg = get_source(config_invalid_client_id).check_connection(logger, config=config_invalid_client_id)
    assert not ok
    assert error_msg


def test_streams(requests_mock, config):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    streams = get_source(config).streams(config)

    assert len(streams) == 32


def test_streams_forbidden_returns_default_streams(requests_mock, config):
    # 403 forbidden → no custom streams, should fall back to the 32 built-in ones
    requests_mock.get(
        "https://api.hubapi.com/crm/v3/schemas",
        json={"status": "error", "message": "This access_token does not have proper permissions!"},
        status_code=403,
    )
    streams = get_source(config).streams(config)
    assert len(streams) == 32


def test_check_credential_title_exception(config):
    config["credentials"].pop("credentials_title")
    ok, message = get_source(config).check_connection(logger, config=config)
    assert ok == False
    assert "`authenticator_selection_path` is not found in the config" in message


def test_streams_ok_with_one_custom_stream(requests_mock, config, mock_dynamic_schema_requests):
    # 200 OK → one custom “cars” stream added to the 32 built-ins, total = 33
    adapter = requests_mock.get(
        "https://api.hubapi.com/crm/v3/schemas",
        json={"results": [{"name": "cars", "fullyQualifiedName": "cars", "properties": {}}]},
        status_code=200,
    )
    streams = discover(get_source(config), config).catalog.catalog.streams
    assert adapter.called
    assert len(streams) == 33


def test_check_connection_backoff_on_limit_reached(requests_mock, config):
    """Error once, check that we retry and not fail"""
    prop_response = [
        {
            "json": [
                {
                    "name": "hs__migration_soft_delete",
                    "type": "enumeration",
                }
            ],
            "status_code": 200,
        }
    ]
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429, "headers": {"Retry-After": "0"}},
        {"json": [], "status_code": 200},
    ]
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", prop_response)
    requests_mock.register_uri("GET", "/crm/v3/objects/contact", responses)
    source = get_source(config)
    alive, error = source.check_connection(logger=logger, config=config)

    assert alive
    assert not error


def test_check_connection_backoff_on_server_error(requests_mock, config):
    """Error once, check that we retry and not fail"""
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    prop_response = [
        {
            "json": [
                {
                    "name": "hs__migration_soft_delete",
                    "type": "enumeration",
                }
            ],
            "status_code": 200,
        }
    ]
    responses = [
        {"json": {"error": "something bad"}, "status_code": 500},
        {"json": [], "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", prop_response)
    requests_mock.register_uri("GET", "/crm/v3/objects/contact", responses)
    source = get_source(config)
    alive, error = source.check_connection(logger=logger, config=config)

    assert alive
    assert not error


def test_stream_forbidden(requests_mock, config, mock_dynamic_schema_requests):
    json = {
        "status": "error",
        "message": "This access_token does not have proper permissions!",
    }
    requests_mock.get("https://api.hubapi.com/automation/v3/workflows", json=json, status_code=403)
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json=json, status_code=403)

    output = read_from_stream(config, "workflows", SyncMode.full_refresh)
    assert not output.records
    assert "The authenticated user does not have permissions to access the resource" in output.errors[0].trace.error.message


def test_parent_stream_forbidden(requests_mock, config, fake_properties_list, mock_dynamic_schema_requests):
    json = {
        "status": "error",
        "message": "This access_token does not have proper permissions!",
    }
    requests_mock.get("https://api.hubapi.com/marketing/v3/forms", json=json, status_code=403)
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]
    requests_mock.get("https://api.hubapi.com/properties/v2/form/properties", properties_response)
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json=json, status_code=403)

    output = read_from_stream(config, "form_submissions", SyncMode.full_refresh)
    assert not output.records
    assert "The authenticated user does not have permissions to access the resource" in output.errors[0].trace.error.message


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

    def test_stream_with_splitting_properties(self, requests_mock, fake_properties_list, config, mock_dynamic_schema_requests):
        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
        """
        Check working stream `companies` with large list of properties using new functionality with splitting properties
        """
        test_stream = find_stream("companies", config)

        self.set_mock_properties(requests_mock, "/properties/v2/company/properties", fake_properties_list)

        record_ids_paginated = [list(map(str, range(100))), list(map(str, range(100, 150, 1)))]

        test_stream._sync_mode = SyncMode.full_refresh
        test_stream_url = test_stream.retriever.requester.url_base + "/" + test_stream.retriever.requester.get_path()
        properties_slices = (fake_properties_list[:686], fake_properties_list[686:1351], fake_properties_list[1351:])
        after_id = None
        for id_list in record_ids_paginated:
            for property_slice in properties_slices:
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
                params = {
                    "associations": "contacts",
                    "properties": ",".join(property_slice),
                    "limit": 100,
                }
                if after_id:
                    params.update({"after": after_id})
                requests_mock.register_uri(
                    "GET",
                    f"{test_stream_url}?{urlencode(params)}",
                    record_responses,
                )
            after_id = id_list[-1]

        stream_records = read_from_stream(config, "companies", SyncMode.full_refresh).records
        # check that we have records for all set ids, and that each record has 2000 properties (not more, and not less)
        assert len(stream_records) == sum([len(ids) for ids in record_ids_paginated])
        for record_ab_message in stream_records:
            record = record_ab_message.record.data
            assert len(record["properties"]) == NUMBER_OF_PROPERTIES
            properties = [field for field in record if field.startswith("properties_")]
            assert len(properties) == NUMBER_OF_PROPERTIES

    def test_stream_with_splitting_properties_with_pagination(self, requests_mock, config, fake_properties_list):
        """
        Check working stream `products` with large list of properties using new functionality with splitting properties
        """
        mock_dynamic_schema_requests_with_skip(requests_mock, ["product"])
        requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

        self.set_mock_properties(requests_mock, "/properties/v2/product/properties", fake_properties_list)

        test_stream = find_stream("products", config)

        property_slices = (fake_properties_list[:686], fake_properties_list[686:1351], fake_properties_list[1351:])

        for property_slice in property_slices:
            data = {p: "fake_data" for p in property_slice}
            record_responses = [
                {
                    "json": {
                        "results": [
                            {**self.BASE_OBJECT_BODY, **{"id": id, "properties": data}}
                            for id in ["6043593519", "1092593519", "1092593518", "1092593517", "1092593516"]
                        ],
                        "paging": {},
                    },
                    "status_code": 200,
                }
            ]
            params = {
                "archived": "false",
                "properties": ",".join(property_slice),
                "limit": 100,
            }
            requests_mock.register_uri(
                "GET",
                f"{test_stream.retriever.requester.url_base}/{test_stream.retriever.requester.get_path()}?{urlencode(params)}",
                record_responses,
            )
        state = (
            StateBuilder()
            .with_stream_state(
                "products",
                {"updatedAt": "2006-01-01T00:03:18.336Z"},
            )
            .build()
        )

        stream_records = read_from_stream(config, "products", SyncMode.incremental, state).records

        assert len(stream_records) == 5
        for record_ab_message in stream_records:
            record = record_ab_message.record.data
            assert len(record["properties"]) == NUMBER_OF_PROPERTIES
            properties = [field for field in record if field.startswith("properties_")]
            assert len(properties) == NUMBER_OF_PROPERTIES


def test_search_based_stream_should_not_attempt_to_get_more_than_10k_records(
    requests_mock, config, fake_properties_list, mock_dynamic_schema_requests
):
    """
    If there are more than 10,000 records that would be returned by the Hubspot search endpoint,
    the CRMSearchStream instance should stop at the 10Kth record
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    responses = [
        {
            "json": {
                "results": [{"id": f"{y}", "updatedAt": "2022-02-25T16:43:11Z"} for y in range(200)],
                "paging": {
                    "next": {
                        "after": f"{x * 200}",
                    }
                },
            },
            "status_code": 200,
        }
        for x in range(1, 51)
    ]
    # After reaching 10K records, it performs a new search query.
    responses.extend(
        [
            {
                "json": {
                    "results": [{"id": f"{y}", "updatedAt": "2022-03-01T00:00:00Z"} for y in range(200)],
                    "paging": {
                        "next": {
                            "after": f"{x * 200}",
                        }
                    },
                },
                "status_code": 200,
            }
            for x in range(1, 5)
        ]
    )
    # Last page... it does not have paging->next->after
    responses.append(
        {
            "json": {"results": [{"id": f"{y}", "updatedAt": "2022-03-01T00:00:00Z"} for y in range(200)], "paging": {}},
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
    test_stream = find_stream("companies", config)
    state = (
        StateBuilder()
        .with_stream_state(
            "companies",
            {"updatedAt": "2022-02-24T16:43:11Z"},
        )
        .build()
    )

    test_stream_url = test_stream.retriever.requester.url_base + "/" + test_stream.retriever.requester.get_path() + "/search"
    requests_mock.register_uri("POST", test_stream_url, responses)
    requests_mock.register_uri("GET", "/properties/v2/company/properties", properties_response)
    requests_mock.register_uri(
        "POST",
        "/crm/v4/associations/company/contacts/batch/read",
        [{"status_code": 200, "json": {"results": [{"from": {"id": "1"}, "to": [{"toObjectId": "2"}]}]}}],
    )
    requests_mock.register_uri(
        "POST",
        "/crm/v4/associations/company/contacts/batch/read",
        [{"status_code": 200, "json": {"results": [{"from": {"id": "1"}, "to": [{"toObjectId": "2"}]}]}}],
    )

    output = read_from_stream(config, "companies", SyncMode.incremental, state)
    # The stream should not attempt to get more than 10K records.
    # Instead, it should use the new state to start a new search query.
    assert len(output.records) == 11000
    assert output.state_messages[1].state.stream.stream_state.updatedAt == "2022-03-01T00:00:00.000000Z"


def test_search_based_incremental_stream_should_sort_by_id(requests_mock, config, fake_properties_list, mock_dynamic_schema_requests):
    """
    If there are more than 10,000 records that would be returned by the Hubspot search endpoint,
    the CRMSearchStream instance should stop at the 10Kth record
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    # Create test_stream instance with some state
    test_stream = find_stream("companies", config)
    test_stream.associations = []

    # Custom callback to mock search endpoint filter and sort behavior, returns 100 records per request.
    # See _process_search in stream.py for details on the structure of the filter amd sort parameters.
    # The generated records will have an id that is the sum of the current id and the current "after" value
    # and the updatedAt field will be a random date between min_time and max_time.
    # Store "after" value in the record to check if it resets after 10k records.
    responses = [
        {
            "json": {
                "results": [{"id": f"{y}", "updatedAt": "2022-02-25T16:43:11Z"} for y in range(x * 200 - 200 + 1, x * 200 + 1)],
                "paging": {
                    "next": {
                        "after": f"{x * 200}",
                    }
                },
            },
            "status_code": 200,
        }
        for x in range(1, 51)
    ]
    responses_more_than_10k = [
        {
            "json": {
                "results": [{"id": f"{y + 10000}", "updatedAt": "2022-02-25T16:43:11Z"} for y in range(x * 200 - 200 + 1, x * 200 + 1)],
                "paging": {
                    "next": {
                        "after": f"{x * 200}",
                    }
                }
                if x < 5
                else None,
            },
            "status_code": 200,
        }
        for x in range(1, 6)
    ]
    responses.extend(responses_more_than_10k)
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]
    test_stream_url = test_stream.retriever.requester.url_base + "/" + test_stream.retriever.requester.get_path() + "/search"
    # Mocking Request
    requests_mock.register_uri("POST", test_stream_url, responses)
    requests_mock.register_uri("GET", "/properties/v2/company/properties", properties_response)
    requests_mock.register_uri(
        "POST",
        "/crm/v4/associations/company/contacts/batch/read",
        [{"status_code": 200, "json": {"results": [{"from": {"id": f"{x}"}, "to": [{"toObjectId": "2"}]}]}} for x in range(1, 11001, 200)],
    )
    state = (
        StateBuilder()
        .with_stream_state(
            "companies",
            {"updatedAt": "2022-01-24T16:43:11Z"},
        )
        .build()
    )
    output = read_from_stream(config, "companies", SyncMode.incremental, state)
    records = output.records
    # The stream should not attempt to get more than 10K records.
    # Instead, it should use the new state to start a new search query.
    assert len(records) == 11000
    # Check that the records are sorted by id and that "after" resets after 10k records
    assert dict(records[0].record.data)["id"] == "1"
    assert dict(records[10000 - 1].record.data)["id"] == "10000"
    assert dict(records[10000].record.data)["id"] == "10001"
    assert dict(records[-1].record.data)["id"] == "11000"
    assert output.state_messages[1].state.stream.stream_state.updatedAt == "2022-02-25T16:43:11.000000Z"


def test_engagements_stream_pagination_works(requests_mock, config):
    """
    Tests the engagements stream handles pagination correctly, for both
    full_refresh and incremental sync modes.
    """

    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

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
        "/engagements/v1/engagements/recent/modified?count=250",
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
    test_stream = find_stream("engagements", config)

    records = read_full_refresh(test_stream)
    # The stream should handle pagination correctly and output 600 records.
    assert len(records) == 600

    test_stream = find_stream("engagements", config)
    records, _ = read_incremental(test_stream, {})
    # The stream should handle pagination correctly and output 250 records.
    assert len(records) == 100


def test_engagements_stream_since_old_date(mock_dynamic_schema_requests, requests_mock, fake_properties_list, config):
    """
    Connector should use 'All Engagements' API for old dates (more than 30 days)
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    old_date = 1614038400000  # Tuesday, 23 February 2021, 0:00:00
    recent_date = 1645315200000
    responses = [
        {
            "json": {
                "results": [{"engagement": {"id": f"{y}", "lastUpdated": recent_date}} for y in range(100)],
                "hasMore": False,
                "offset": 0,
                "total": 100,
            },
            "status_code": 200,
        }
    ]

    # Mocking Request
    requests_mock.register_uri("GET", "/engagements/v1/engagements/paged?count=250", responses)
    state = (
        StateBuilder()
        .with_stream_state(
            "engagements",
            {"lastUpdated": old_date},
        )
        .build()
    )
    output = read_from_stream(config, "engagements", SyncMode.incremental, state)

    assert len(output.records) == 100
    assert int(output.state_messages[0].state.stream.stream_state.lastUpdated) == recent_date


def test_engagements_stream_since_recent_date(mock_dynamic_schema_requests, requests_mock, fake_properties_list, config):
    """
    Connector should use 'Recent Engagements' API for recent dates (less than 30 days)
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    recent_date = ab_datetime_now() - timedelta(days=10)  # 10 days ago
    recent_date = int(recent_date.timestamp() * 1000)
    responses = [
        {
            "json": {
                "results": [{"engagement": {"id": f"{y}", "lastUpdated": recent_date}} for y in range(100)],
                "hasMore": False,
                "offset": 0,
                "total": 100,
            },
            "status_code": 200,
        }
    ]
    state = StateBuilder().with_stream_state("engagements", {"lastUpdated": recent_date}).build()
    # Mocking Request
    requests_mock.register_uri("GET", f"/engagements/v1/engagements/recent/modified?count=250&since={recent_date}", responses)
    output = read_from_stream(config, "engagements", SyncMode.incremental, state)
    # The stream should not attempt to get more than 10K records.
    assert len(output.records) == 100
    assert int(output.state_messages[0].state.stream.stream_state.lastUpdated) == recent_date


def test_engagements_stream_since_recent_date_more_than_10k(mock_dynamic_schema_requests, requests_mock, fake_properties_list, config):
    """
    Connector should use 'Recent Engagements' API for recent dates (less than 30 days).
    If response from 'Recent Engagements' API returns 10k records, it means that there more records,
    so 'All Engagements' API should be used.
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    recent_date = ab_datetime_now() - timedelta(days=10)  # 10 days ago
    recent_date = int(recent_date.timestamp() * 1000)
    responses = [
        {
            "json": {
                "results": [{"engagement": {"id": f"{y}", "lastUpdated": recent_date}} for y in range(100)],
                "hasMore": False,
                "offset": 0,
                "total": 10001,
            },
            "status_code": 200,
        }
    ]
    state = StateBuilder().with_stream_state("engagements", {"lastUpdated": recent_date}).build()
    # Mocking Request
    requests_mock.register_uri("GET", f"/engagements/v1/engagements/recent/modified?count=250&since={recent_date}", responses)
    requests_mock.register_uri("GET", "/engagements/v1/engagements/paged?count=250", responses)

    output = read_from_stream(config, "engagements", SyncMode.incremental, state)
    assert len(output.records) == 100
    assert int(output.state_messages[0].state.stream.stream_state.lastUpdated) == recent_date


def test_pagination_marketing_emails_stream(requests_mock, config):
    """
    Test pagination for Marketing Emails stream
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    requests_mock.register_uri(
        "GET",
        "/marketing-emails/v1/emails/with-statistics?limit=250",
        [
            {
                "json": {
                    "objects": [{"id": f"{y}", "updated": 1641234593251} for y in range(250)],
                    "limit": 250,
                    "offset": 0,
                    "total": 600,
                },
                "status_code": 200,
            },
            {
                "json": {
                    "objects": [{"id": f"{y}", "updated": 1641234593251} for y in range(250, 500)],
                    "limit": 250,
                    "offset": 250,
                    "total": 600,
                },
                "status_code": 200,
            },
            {
                "json": {
                    "objects": [{"id": f"{y}", "updated": 1641234595251} for y in range(500, 600)],
                    "limit": 250,
                    "offset": 500,
                    "total": 600,
                },
                "status_code": 200,
            },
        ],
    )
    test_stream = find_stream("marketing_emails", config)

    records = read_full_refresh(test_stream)
    # The stream should handle pagination correctly and output 600 records.
    assert len(records) == 600
