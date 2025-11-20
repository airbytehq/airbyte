#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import freezegun
import pytest

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    ConfiguredAirbyteCatalogSerializer,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.sources.types import Record
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.state_builder import StateBuilder

from .conftest import find_stream, get_source, mock_dynamic_schema_requests_with_skip, read_from_stream
from .utils import run_read


def test_updated_at_field_non_exist_handler(requests_mock, config, fake_properties_list, custom_object_schema):
    requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    stream = find_stream("contact_lists", config)
    created_at = "2022-03-25T16:43:11Z"
    responses = [
        {
            "json": {
                "lists": [
                    {
                        "id": "test_id",
                        "createdAt": created_at,
                    },
                ],
            }
        }
    ]

    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v3/lists/search", responses)

    partitions = list(stream._stream_partition_generator.generate())
    assert len(partitions) == 1

    records = list(partitions[0].read())
    assert len(records) == 1
    assert records[0]["updatedAt"] == created_at


@pytest.mark.parametrize(
    "stream_class, endpoint, cursor_value",
    [
        ("campaigns", "campaigns", {"lastUpdatedTime": 1675121674226}),
        ("companies", "company", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("contact_lists", "contact", {"createdAt": "2021-02-25T16:43:11Z", "updatedAt": "2022-02-25T16:43:11Z"}),
        ("contacts", "contact", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("deals", "deal", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("deals_archived", "deal", {"archivedAt": "2022-02-25T16:43:11Z"}),
        ("deal_pipelines", "deal", {"updatedAt": 1675121674226}),
        ("deal_splits", "deal_split", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("email_events", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("email_subscriptions", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("engagements_calls", "calls", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("engagements_emails", "emails", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("engagements_meetings", "meetings", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("engagements_notes", "notes", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("engagements_tasks", "tasks", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("forms", "form", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("form_submissions", "form", {"updatedAt": 1675121674227}),
        ("goals", "goal_targets", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("leads", "leads", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("line_items", "line_item", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("marketing_emails", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("owners", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("owners_archived", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("products", "product", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("ticket_pipelines", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("tickets", "ticket", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("workflows", "", {"updatedAt": 1675121674226}),
    ],
)
def test_streams_read(stream_class, endpoint, cursor_value, requests_mock, fake_properties_list, config):
    mock_dynamic_schema_requests_with_skip(requests_mock, [])
    stream = find_stream(stream_class, config)
    stream_retriever = stream._stream_partition_generator._partition_factory._retriever
    data_field = (
        stream_retriever.record_selector.extractor.field_path[0] if len(stream_retriever.record_selector.extractor.field_path) > 0 else None
    )
    list_entities = [
        {
            "id": "test_id",
            "created": "2022-02-25T16:43:11Z",
        }
        | cursor_value
    ]
    responses = [{"json": {data_field: list_entities} if data_field else list_entities}]

    is_form_submission = stream_class == "form_submissions"

    if is_form_submission:
        forms_response = [
            {
                "json": {
                    data_field: [{"id": "test_id", "created": "2022-02-25T16:43:11Z", "updatedAt": "2022-02-25T16:43:11Z"}],
                }
            }
        ]

    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]

    contact_response = [
        {
            "json": {
                data_field: [
                    {"id": "test_id", "created": "2022-06-25T16:43:11Z", "properties": {"hs_merged_object_ids": "test_id"}} | cursor_value
                ],
            }
        }
    ]

    read_batch_contact_v1_response = [
        {
            "json": {
                "test_id": {"vid": "test_id", "merge-audits": [{"canonical-vid": 2, "vid-to-merge": 5608, "timestamp": 1653322839932}]}
            },
            "status_code": 200,
        }
    ]

    contact_lists_v1_response = [
        {
            "json": {
                "contacts": [{"vid": "test_id", "merge-audits": [{"canonical-vid": 2, "vid-to-merge": 5608, "timestamp": 1653322839932}]}]
            },
            "status_code": 200,
        }
    ]

    stream._sync_mode = SyncMode.full_refresh
    stream_slice = {}
    if is_form_submission:
        stream_slice = {"form_id": ["test_id"]}
    stream_url = stream_retriever.requester.url_base + "/" + stream_retriever.requester.get_path(stream_slice=stream_slice)
    stream._sync_mode = None

    requests_mock.register_uri(stream_retriever.requester._http_method.value, stream_url, responses)
    # mock associations calls
    if stream_retriever.requester._http_method.value == "POST":
        for association in stream_retriever.requester._parameters.get("associations", []):
            requests_mock.register_uri(
                "POST",
                f"https://api.hubapi.com/crm/v4/associations/{endpoint}/{association}/batch/read",
                [{"json": {"results": []}, "status_code": 200}],
            )
    requests_mock.register_uri("GET", "/crm/v3/objects/contact", contact_response)
    requests_mock.register_uri("GET", "/contacts/v1/lists/all/contacts/all", contact_lists_v1_response)
    requests_mock.register_uri("GET", "/marketing/v3/forms", responses if not is_form_submission else forms_response)
    requests_mock.register_uri("GET", "/email/public/v1/campaigns/test_id", responses)
    requests_mock.register_uri("GET", "/email/public/v1/campaigns?count=500", [{"json": {"campaigns": list_entities}}])
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)
    requests_mock.register_uri("GET", "/contacts/v1/contact/vids/batch/", read_batch_contact_v1_response)
    requests_mock.register_uri("POST", "/crm/v3/lists/search", responses)

    records = run_read(stream)
    assert records


@pytest.mark.parametrize(
    "stream_class, endpoint, cursor_value",
    [
        ("contacts", "contact", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("deals", "deal", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("deals_archived", "deal", {"archivedAt": "2022-02-25T16:43:11Z"}),
    ],
    ids=[
        "Contacts stream with v2 field transformations",
        "Deals stream with v2 field transformations",
        "DealsArchived stream with v2 field transformations",
    ],
)
def test_stream_read_with_legacy_field_transformation(
    stream_class,
    endpoint,
    cursor_value,
    requests_mock,
    fake_properties_list,
    migrated_properties_list,
    config,
):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    stream = find_stream(stream_class, config)
    stream_retriever = stream._stream_partition_generator._partition_factory._retriever
    data_field = stream_retriever.record_selector.extractor.field_path[0]
    responses = [
        {
            "json": {
                data_field: [
                    {
                        "id": "test_id",
                        "created": "2022-02-25T16:43:11Z",
                        "properties": {
                            "hs_v2_latest_time_in_prospect": "1 month",
                            "hs_v2_date_entered_prospect": "2024-01-01T00:00:00Z",
                            "hs_v2_date_exited_prospect": "2024-02-01T00:00:00Z",
                            "hs_v2_cumulative_time_in_prsopect": "1 month",
                            "hs_v2_some_other_property_in_prospect": "Great property",
                        },
                    }
                    | cursor_value
                ],
            }
        }
    ]
    fake_properties_list.extend(migrated_properties_list)
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]
    stream._sync_mode = SyncMode.full_refresh

    stream_url = stream_retriever.requester.url_base + "/" + stream_retriever.requester.get_path()

    requests_mock.register_uri(stream_retriever.requester._http_method.value, stream_url, responses)
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)

    # mock associations calls
    if stream_retriever.requester._http_method.value == "POST":
        for association in stream_retriever.requester._parameters.get("associations", []):
            requests_mock.register_uri(
                "POST",
                f"https://api.hubapi.com/crm/v4/associations/{endpoint}/{association}/batch/read",
                [{"json": {"results": []}, "status_code": 200}],
            )

    records = run_read(stream)
    assert records
    expected_record = {
        "id": "test_id",
        "created": "2022-02-25T16:43:11Z",
        "properties": {
            "hs_v2_date_entered_prospect": "2024-01-01T00:00:00Z",
            "hs_v2_date_exited_prospect": "2024-02-01T00:00:00Z",
            "hs_v2_latest_time_in_prospect": "1 month",
            "hs_v2_cumulative_time_in_prsopect": "1 month",
            "hs_v2_some_other_property_in_prospect": "Great property",
            "hs_time_in_prospect": "1 month",
            "hs_date_exited_prospect": "2024-02-01T00:00:00Z",
        },
        "properties_hs_v2_date_entered_prospect": "2024-01-01T00:00:00Z",
        "properties_hs_v2_date_exited_prospect": "2024-02-01T00:00:00Z",
        "properties_hs_v2_latest_time_in_prospect": "1 month",
        "properties_hs_v2_cumulative_time_in_prsopect": "1 month",
        "properties_hs_v2_some_other_property_in_prospect": "Great property",
        "properties_hs_time_in_prospect": "1 month",
        "properties_hs_date_exited_prospect": "2024-02-01T00:00:00Z",
    } | cursor_value
    if stream_class == "contacts":
        expected_record = expected_record | {"properties_hs_lifecyclestage_prospect_date": "2024-01-01T00:00:00Z"}
        expected_record["properties"] = expected_record["properties"] | {"hs_lifecyclestage_prospect_date": "2024-01-01T00:00:00Z"}
    else:
        expected_record = expected_record | {"properties_hs_date_entered_prospect": "2024-01-01T00:00:00Z"}
        expected_record["properties"] = expected_record["properties"] | {"hs_date_entered_prospect": "2024-01-01T00:00:00Z"}
    record = records[0].data if isinstance(records[0], Record) else records[0]
    assert json.dumps(record, sort_keys=True) == json.dumps(expected_record, sort_keys=True)


@pytest.mark.parametrize("sync_mode", [SyncMode.full_refresh, SyncMode.incremental])
def test_crm_search_streams_with_no_associations(sync_mode, requests_mock, fake_properties_list, config):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    stream_state = AirbyteStateMessage(
        type=AirbyteStateType.STREAM,
        stream=AirbyteStreamState(
            stream_descriptor=StreamDescriptor(name="deal_splits"),
            stream_state=AirbyteStateBlob(updatedAt="2021-01-01T00:00:00.000000Z"),
        ),
    )

    if sync_mode == SyncMode.incremental:
        stream = find_stream("deal_splits", config, [stream_state])
    else:
        stream = find_stream("deal_splits", config)
    data_field = stream._stream_partition_generator._partition_factory._retriever.record_selector.extractor.field_path[0]

    cursor_value = {"updatedAt": "2022-02-25T16:43:11Z"}
    responses = [
        {
            "json": {
                data_field: [
                    {
                        "id": "test_id",
                        "created": "2022-02-25T16:43:11Z",
                    }
                    | cursor_value
                ],
            }
        }
    ]

    endpoint_path = "/crm/v3/objects/deal_split/search"
    requests_mock.register_uri("POST", endpoint_path, responses)

    properties_path = f"/properties/v2/deal_split/properties"
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]
    requests_mock.register_uri("POST", endpoint_path, responses)
    requests_mock.register_uri("GET", properties_path, properties_response)

    records = run_read(stream)
    assert records

    state = stream.cursor.state
    assert state == {"updatedAt": "2022-02-25T16:43:11.000000Z"}


@freezegun.freeze_time("2022-02-25T17:00:00Z")
def test_crm_search_streams_requests_contain_custom_properties(requests_mock, fake_properties_list, config):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    stream_state = AirbyteStateMessage(
        type=AirbyteStateType.STREAM,
        stream=AirbyteStreamState(
            stream_descriptor=StreamDescriptor(name="deal_splits"), stream_state=AirbyteStateBlob(updatedAt="2022-02-01T00:00:00.000000Z")
        ),
    )

    config["lookback_window"] = 10
    stream = find_stream("deal_splits", config, [stream_state])

    data_field = stream._stream_partition_generator._partition_factory._retriever.record_selector.extractor.field_path[0]

    cursor_value = {"updatedAt": "2022-02-25T16:43:11Z"}
    responses = [
        {
            "json": {
                data_field: [
                    {
                        "id": "test_id",
                        "created": "2022-02-25T16:43:11Z",
                    }
                    | cursor_value
                ],
            }
        }
    ]

    # Validates that the json request body contains all the custom properties that are injected via the
    # `fetch_properties_from_endpoint` component definition so that they are included in the API response
    def match_request_body(request):
        return request.json() == {
            "limit": 200,
            "sorts": [{"propertyName": "hs_object_id", "direction": "ASCENDING"}],
            "filters": [
                {"propertyName": "hs_lastmodifieddate", "operator": "GTE", "value": 1643673000000},
                {"propertyName": "hs_lastmodifieddate", "operator": "LTE", "value": 1645808400000},
                {"propertyName": "hs_object_id", "operator": "GTE", "value": 0},
            ],
            "properties": fake_properties_list,
            "after": 0,
        }

    endpoint_path = "/crm/v3/objects/deal_split/search"
    requests_mock.register_uri("POST", endpoint_path, responses, additional_matcher=match_request_body)
    properties_path = f"/properties/v2/deal_split/properties"
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]
    stream._sync_mode = SyncMode.incremental
    requests_mock.register_uri("GET", properties_path, properties_response)
    records = run_read(stream)

    assert records
    state = stream.cursor.state
    assert state == {"updatedAt": "2022-02-25T16:43:11.000000Z"}


@pytest.mark.parametrize(
    "error_response",
    [
        {"json": {}, "status_code": 401},
        {"json": {}, "status_code": 429},
        {"json": {}, "status_code": 502},
        {"json": {}, "status_code": 504},
    ],
)
def test_common_error_retry(error_response, requests_mock, config, fake_properties_list, mock_dynamic_schema_requests):
    """Error once, check that we retry and not fail"""
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    properties_response = [
        {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
        for property_name in fake_properties_list
    ]
    responses = [
        error_response,
        {
            "json": properties_response,
            "status_code": 200,
        },
    ]

    stream = find_stream("companies", config)
    data_field = stream._stream_partition_generator._partition_factory._retriever.record_selector.extractor.field_path[0]

    response = {
        data_field: [
            {
                "id": "test_id",
                "created": "2022-02-25T16:43:11Z",
                "updatedAt": "2022-02-25T16:43:11Z",
                "lastUpdatedTime": "2022-02-25T16:43:11Z",
            }
        ],
    }
    requests_mock.register_uri("GET", "/properties/v2/company/properties", responses)
    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v3/objects/company/search", [{"json": response}])
    associations_responses = [{"json": {"results": []}, "status_code": 200}]

    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v4/associations/company/contacts/batch/read", associations_responses)
    records = run_read(stream)

    expected_record = response[data_field][0]
    record = records[0].data if isinstance(records[0], Record) else records[0]
    assert json.dumps(record, sort_keys=True) == json.dumps(expected_record, sort_keys=True)
    assert len(requests_mock.request_history) > 1


def test_contact_lists_transform(requests_mock, config, custom_object_schema, mock_dynamic_schema_requests):
    requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    responses = [
        {
            "json": {
                "lists": [
                    {
                        "listId": 1,
                        "createdAt": "2022-02-25T16:43:11Z",
                    },
                    {
                        "listId": 2,
                        "createdAt": "2022-02-25T16:43:11Z",
                    },
                    {
                        "listId": 3,
                        "createdAt": "2022-02-25T16:43:11Z",
                    },
                ]
            }
        }
    ]

    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v3/lists/search", responses)
    records = read_from_stream(config, "contact_lists", SyncMode.full_refresh).records

    assert len(records) > 0
    for record in records:
        assert isinstance(record.record.data["updatedAt"], str)


def test_client_side_incremental_stream(mock_dynamic_schema_requests, requests_mock, fake_properties_list, config):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    data_field = "results"
    latest_cursor_value = "2024-01-30T23:46:36.287000Z"
    responses = [
        {
            "json": {
                data_field: [
                    {"id": "test_id_1", "createdAt": "2022-03-25T16:43:11Z", "updatedAt": "2023-01-30T23:46:36.287Z"},
                    {"id": "test_id_2", "createdAt": "2022-03-25T16:43:11Z", "updatedAt": latest_cursor_value},
                    {"id": "test_id_3", "createdAt": "2022-03-25T16:43:11Z", "updatedAt": "2023-02-20T23:46:36.287Z"},
                ],
            }
        }
    ]
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "createdAt": "2023-01-30T23:46:24.355Z", "updatedAt": "2023-01-30T23:46:36.287Z"}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]

    requests_mock.register_uri("GET", "https://api.hubapi.com/marketing/v3/forms", responses)
    requests_mock.register_uri("GET", "/properties/v2/form/properties", properties_response)

    output = read_from_stream(config, "forms", SyncMode.incremental)
    assert output.state_messages[-1].state.stream.stream_state.__dict__["updatedAt"] == latest_cursor_value


def test_custom_object_stream_doesnt_call_hubspot_to_get_json_schema_if_available(
    requests_mock, custom_object_schema, config, expected_custom_object_json_schema, mock_dynamic_schema_requests
):
    adapter = requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    streams = discover(get_source(config), config)
    json_schema = [s.json_schema for s in streams.catalog.catalog.streams if s.name == "animals"][0]

    assert json_schema == expected_custom_object_json_schema
    # called only once when creating dynamic streams
    assert adapter.call_count == 1


def test_get_custom_objects_metadata_success(
    requests_mock, custom_object_schema, expected_custom_object_json_schema, config, mock_dynamic_schema_requests
):
    requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    source_hubspot = get_source(config)
    streams = discover(source_hubspot, config)
    custom_stream = [s for s in source_hubspot.streams(config) if s.name == "animals"][0]
    custom_stream_json_schema = [s.json_schema for s in streams.catalog.catalog.streams if s.name == "animals"][0]

    assert custom_stream_json_schema == expected_custom_object_json_schema
    assert custom_stream._stream_partition_generator._partition_factory._retriever._parameters["entity"] == "p19936848_Animal"


@pytest.mark.parametrize(
    "stream_class, endpoint, cursor_value, fake_properties_list_response, data_to_cast, expected_casted_data",
    [
        (
            "deals",
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "string")],
            {"hs_closed_amount": 123456},
            {"hs_closed_amount": "123456"},
        ),
        (
            "deals",
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "integer")],
            {"hs_closed_amount": "123456"},
            {"hs_closed_amount": 123456},
        ),
        (
            "deals",
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "number")],
            {"hs_closed_amount": "123456.10"},
            {"hs_closed_amount": 123456.10},
        ),
        (
            "deals",
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "boolean")],
            {"hs_closed_amount": "1"},
            {"hs_closed_amount": True},
        ),
    ],
)
def test_cast_record_fields_if_needed(
    stream_class,
    endpoint,
    cursor_value,
    fake_properties_list_response,
    requests_mock,
    data_to_cast,
    expected_casted_data,
    custom_object_schema,
    config,
    mock_dynamic_schema_requests,
):
    """
    Test that the stream cast record fields in properties key with properties endpoint response if needed
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    stream = find_stream(stream_class, config)
    data_field = stream._stream_partition_generator._partition_factory._retriever.record_selector.extractor.field_path[0]

    responses = [
        {
            "json": {
                data_field: [{"id": "test_id", "created": "2022-02-25T16:43:11Z", "properties": data_to_cast} | cursor_value],
            }
        }
    ]

    properties_response = [
        {
            "json": [
                {"name": property_name, "type": property_type, "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name, property_type in fake_properties_list_response
            ],
            "status_code": 200,
        }
    ]

    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v3/objects/deal/search", responses)
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)

    associations_responses = [{"json": {"results": []}, "status_code": 200}]

    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v4/associations/deal/companies/batch/read", associations_responses)
    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v4/associations/deal/contacts/batch/read", associations_responses)
    requests_mock.register_uri("POST", "https://api.hubapi.com/crm/v4/associations/deal/line_items/batch/read", associations_responses)
    records = read_from_stream(config, "deals", SyncMode.full_refresh).records
    assert records
    record = records[0]
    for casted_key, casted_value in expected_casted_data.items():
        assert record.record.data["properties"][casted_key] == casted_value


@pytest.mark.parametrize(
    "stream, scopes, url, method",
    [
        ("campaigns", "crm.lists.read", "https://api.hubapi.com/email/public/v1/campaigns", "GET"),
        (
            "companies",
            "crm.objects.contacts.read, crm.objects.companies.read",
            "https://api.hubapi.com/crm/v3/objects/company/search",
            "POST",
        ),
        ("companies_property_history", "crm.objects.companies.read", "https://api.hubapi.com/properties/v2/companies/properties", "GET"),
        ("contact_lists", "crm.lists.read", "https://api.hubapi.com/crm/v3/lists/search", "POST"),
        ("contacts_property_history", "crm.objects.contacts.read", "https://api.hubapi.com/properties/v2/contacts/properties", "GET"),
        ("deal_pipelines", "crm.objects.contacts.read", "https://api.hubapi.com/crm-pipelines/v1/pipelines/deals", "GET"),
        ("deals", "crm.objects.deals.read", "https://api.hubapi.com/crm/v3/objects/deal/search", "POST"),
        ("deals_property_history", "crm.objects.deals.read", "https://api.hubapi.com/properties/v2/deals/properties", "GET"),
        ("email_events", "content", "https://api.hubapi.com/email/public/v1/events", "GET"),
        ("email_subscriptions", "content", "https://api.hubapi.com/email/public/v1/subscriptions", "GET"),
        (
            "engagements",
            "crm.objects.companies.read, crm.objects.contacts.read, crm.objects.deals.read, tickets, e-commerce",
            "https://api.hubapi.com/engagements/v1/engagements/paged",
            "GET",
        ),
        ("engagements_calls", "crm.objects.contacts.read", "https://api.hubapi.com/crm/v3/objects/calls/search", "POST"),
        (
            "engagements_emails",
            "crm.objects.contacts.read, sales-email-read",
            "https://api.hubapi.com/crm/v3/objects/emails/search",
            "POST",
        ),
        ("engagements_meetings", "crm.objects.contacts.read", "https://api.hubapi.com/crm/v3/objects/meetings/search", "POST"),
        ("engagements_notes", "crm.objects.contacts.read", "https://api.hubapi.com/crm/v3/objects/notes/search", "POST"),
        ("engagements_tasks", "crm.objects.contacts.read", "https://api.hubapi.com/crm/v3/objects/tasks/search", "POST"),
        ("marketing_emails", "content", "https://api.hubapi.com/marketing/v3/emails", "GET"),
        ("deals_archived", "contacts, crm.objects.deals.read", "https://api.hubapi.com/crm/v3/objects/deals", "GET"),
        ("forms", "forms", "https://api.hubapi.com/marketing/v3/forms", "GET"),
        # form_submissions have parent stream forms
        # ("form_submissions", "forms", "https://api.hubapi.com/marketing/v3/forms", "GET"),
        ("goals", "crm.objects.goals.read", "https://api.hubapi.com/crm/v3/objects/goal_targets", "GET"),
        ("line_items", "e-commerce, crm.objects.line_items.read", "https://api.hubapi.com/crm/v3/objects/line_item", "GET"),
        ("owners", "crm.objects.owners.read", "https://api.hubapi.com/crm/v3/owners", "GET"),
        ("owners_archived", "crm.objects.owners.read", "https://api.hubapi.com/crm/v3/owners", "GET"),
        ("products", "e-commerce", "https://api.hubapi.com/crm/v3/objects/product", "GET"),
        ("subscription_changes", "content", "https://api.hubapi.com/email/public/v1/subscriptions/timeline", "GET"),
        (
            "ticket_pipelines",
            "media_bridge.read, tickets, crm.schemas.custom.read, e-commerce, timeline, contacts, crm.schemas.contacts.read, crm.objects.contacts.read, crm.objects.contacts.write, crm.objects.deals.read, crm.schemas.quotes.read, crm.objects.deals.write, crm.objects.companies.read, crm.schemas.companies.read, crm.schemas.deals.read, crm.schemas.line_items.read, crm.objects.companies.write",
            "https://api.hubapi.com/crm/v3/pipelines/tickets",
            "GET",
        ),
        ("workflows", "automation", "https://api.hubapi.com/automation/v3/workflows", "GET"),
        ("contacts", "crm.objects.contacts.read", "https://api.hubapi.com/crm/v3/objects/contact/search", "POST"),
        ("deal_splits", "crm.objects.deals.read", "https://api.hubapi.com/crm/v3/objects/deal_split/search", "POST"),
        (
            "leads",
            "crm.objects.contacts.read, crm.objects.companies.read, crm.objects.leads.read",
            "https://api.hubapi.com/crm/v3/objects/leads/search",
            "POST",
        ),
        ("tickets", "tickets", "https://api.hubapi.com/crm/v3/objects/ticket/search", "POST"),
    ],
)
def test_streams_raise_error_message_if_scopes_missing(stream, scopes, url, method, requests_mock, config, mock_dynamic_schema_requests):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.register_uri(method, url, [{"status_code": 403}])
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": stream, "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = (
        StateBuilder()
        .with_stream_state(
            stream,
            {},
        )
        .build()
    )
    source_hubspot = get_source(config)
    output = read(source_hubspot, config=config, catalog=catalog, state=state)
    assert output.errors[0].trace.error.message == (
        "Access denied (403). The authenticated user does not have permissions to access the resource. "
        f"Verify your scopes: {scopes} to access stream {stream}. "
        f"See details: https://docs.airbyte.com/integrations/sources/hubspot#step-2-configure-the-scopes-for-your-streams-private-app-only"
    )


def test_discover_if_scopes_missing(config, requests_mock, mock_dynamic_schema_requests):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.register_uri("GET", "https://api.hubapi.com/properties/v2/companies/properties", [{"status_code": 403}])
    source_hubspot = get_source(config)
    output = discover(source_hubspot, config=config)
    assert output.catalog


def test_read_catalog_with_missing_scopes(config, requests_mock, mock_dynamic_schema_requests):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.get("https://api.hubapi.com/marketing/v3/emails", json={}, status_code=403)
    requests_mock.get("https://api.hubapi.com/email/public/v1/subscriptions", json={}, status_code=403)
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": "marketing_emails", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                },
                {
                    "stream": {"name": "email_subscriptions", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "append",
                },
            ]
        }
    )
    state = (
        StateBuilder()
        .with_stream_state(
            "marketing_emails",
            {},
        )
        .with_stream_state(
            "email_subscriptions",
            {},
        )
        .build()
    )
    source_hubspot = get_source(config)
    output = read(source_hubspot, config=config, catalog=catalog, state=state)
    assert output.errors
    assert not output.records
    error_messages = [error.trace.error.message for error in output.errors]
    assert error_messages
    assert (
        "Access denied (403). The authenticated user does not have permissions to access the resource. "
        "Verify your scopes: content to access stream email_subscriptions. See details: "
        "https://docs.airbyte.com/integrations/sources/hubspot#step-2-configure-the-scopes-for-your-streams-private-app-only"
    ) in error_messages
    assert (
        "Access denied (403). The authenticated user does not have permissions to access the resource. "
        "Verify your scopes: content to access stream marketing_emails. See details: "
        "https://docs.airbyte.com/integrations/sources/hubspot#step-2-configure-the-scopes-for-your-streams-private-app-only"
    ) in error_messages
