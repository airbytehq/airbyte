#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import patch

import mock
import pendulum
import pytest
from source_hubspot.streams import (
    ContactsWebAnalytics,
    CustomObject,
    Deals,
    RecordUnnester,
)

from airbyte_cdk.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode
from airbyte_cdk.sources.types import Record

from .conftest import find_stream, mock_dynamic_schema_requests_with_skip, read_from_stream
from .utils import read_full_refresh, read_incremental


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_updated_at_field_non_exist_handler(requests_mock, config, common_params, fake_properties_list, custom_object_schema):
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

    stream_slices = list(stream.retriever.stream_slicer.stream_slices())
    assert len(stream_slices) == 1

    records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices[0]))
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
        ("marketing_emails", "", {"updated": "1634050455543"}),
        ("owners", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("owners_archived", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("products", "product", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("ticket_pipelines", "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("tickets", "ticket", {"updatedAt": "2022-02-25T16:43:11Z"}),
        ("workflows", "", {"updatedAt": 1675121674226}),
    ],
)
@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_streams_read(
    mock_get_custom_object_streams, stream_class, endpoint, cursor_value, requests_mock, common_params, fake_properties_list, config
):
    mock_dynamic_schema_requests_with_skip(requests_mock, [])
    stream = find_stream(stream_class, config)
    data_field = (
        stream.retriever.record_selector.extractor.field_path[0] if len(stream.retriever.record_selector.extractor.field_path) > 0 else None
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
    if isinstance(stream_class, str):
        stream_slice = {}
        if is_form_submission:
            stream_slice = {"form_id": ["test_id"]}
        stream_url = stream.retriever.requester.url_base + "/" + stream.retriever.requester.get_path(stream_slice=stream_slice)
    else:
        stream_url = stream.url + "/test_id" if is_form_submission else stream.url
    stream._sync_mode = None

    requests_mock.register_uri("GET", stream_url, responses)
    requests_mock.register_uri("GET", "/crm/v3/objects/contact", contact_response)
    requests_mock.register_uri("GET", "/contacts/v1/lists/all/contacts/all", contact_lists_v1_response)
    requests_mock.register_uri("GET", "/marketing/v3/forms", responses if not is_form_submission else forms_response)
    requests_mock.register_uri("GET", "/email/public/v1/campaigns/test_id", responses)
    requests_mock.register_uri("GET", "/email/public/v1/campaigns?count=500", [{"json": {"campaigns": list_entities}}])
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)
    requests_mock.register_uri("GET", "/contacts/v1/contact/vids/batch/", read_batch_contact_v1_response)
    requests_mock.register_uri("POST", "/crm/v3/lists/search", responses)

    records = read_full_refresh(stream)
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
@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_stream_read_with_legacy_field_transformation(
    mock_get_custom_object_streams,
    stream_class,
    endpoint,
    cursor_value,
    requests_mock,
    common_params,
    fake_properties_list,
    migrated_properties_list,
    config,
):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    if isinstance(stream_class, str):
        stream = find_stream(stream_class, config)
        data_field = stream.retriever.record_selector.extractor.field_path[0]
    else:
        stream = stream_class(**common_params)
        data_field = stream.data_field
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

    if isinstance(stream_class, str):
        stream_url = stream.retriever.requester.url_base + "/" + stream.retriever.requester.get_path()
    else:
        stream_url = stream.url
    requests_mock.register_uri("GET", stream_url, responses)
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)

    records = read_full_refresh(stream)
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
@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_crm_search_streams_with_no_associations(
    mock_get_custom_object_streams, sync_mode, common_params, requests_mock, fake_properties_list, config
):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    stream_state = AirbyteStateMessage(
        type=AirbyteStateType.STREAM,
        stream=AirbyteStreamState(
            stream_descriptor=StreamDescriptor(name="deal_splits"), stream_state=AirbyteStateBlob(updatedAt="2021-01-01T00:00:00.000000Z")
        ),
    )

    if sync_mode == SyncMode.incremental:
        stream = find_stream("deal_splits", config, [stream_state])
    else:
        stream = find_stream("deal_splits", config)
    data_field = stream.retriever.record_selector.extractor.field_path[0]

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
    if sync_mode == SyncMode.full_refresh:
        endpoint_path = "/crm/v3/objects/deal_split"
        requests_mock.register_uri("GET", endpoint_path, responses)
    else:
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
    stream._sync_mode = sync_mode
    requests_mock.register_uri("POST", endpoint_path, responses)
    requests_mock.register_uri("GET", properties_path, properties_response)
    if sync_mode == SyncMode.incremental:
        records, state = read_incremental(stream, stream_state=stream_state.stream.stream_state.__dict__)
        assert state
    else:
        records = read_full_refresh(stream)
    assert records


@pytest.mark.parametrize(
    "error_response",
    [
        {"json": {}, "status_code": 429},
        {"json": {}, "status_code": 502},
        {"json": {}, "status_code": 504},
    ],
)
@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_common_error_retry(mock_get_custom_object_streams, error_response, requests_mock, common_params, fake_properties_list, config):
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
    data_field = stream.retriever.record_selector.extractor.field_path[0]

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
    stream._sync_mode = SyncMode.full_refresh
    stream_url = stream.retriever.requester.url_base + "/" + stream.retriever.requester.get_path()
    stream._sync_mode = None
    requests_mock.register_uri("GET", stream_url, [{"json": response}])
    records = read_full_refresh(stream)

    expected_record = response[data_field][0]
    record = records[0].data if isinstance(records[0], Record) else records[0]
    assert json.dumps(record, sort_keys=True) == json.dumps(expected_record, sort_keys=True)
    assert len(requests_mock.request_history) > 1


def test_contact_lists_transform(requests_mock, common_params, config, custom_object_schema):
    requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    stream = find_stream("contact_lists", config)

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
    records = read_full_refresh(stream)

    assert len(records) > 0
    for record in records:
        assert isinstance(record["updatedAt"], str)


@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_client_side_incremental_stream(
    mock_get_custom_object_streams, mock_dynamic_schema_requests, requests_mock, common_params, fake_properties_list, config
):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    stream = find_stream("forms", config)
    data_field = stream.retriever.record_selector.extractor.field_path[0]
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

    stream_url = stream.retriever.requester.url_base + stream.retriever.requester.path

    requests_mock.register_uri("GET", stream_url, responses)
    requests_mock.register_uri("GET", "/properties/v2/form/properties", properties_response)

    output = read_from_stream(config, "forms", SyncMode.incremental)
    assert output.state_messages[-1].state.stream.stream_state.__dict__[stream.cursor_field] == latest_cursor_value


@pytest.fixture(name="custom_object_schema")
def custom_object_schema_fixture():
    return {
        "labels": {"this": "that"},
        "requiredProperties": ["name"],
        "searchableProperties": ["name"],
        "primaryDisplayProperty": "name",
        "secondaryDisplayProperties": [],
        "archived": False,
        "restorable": True,
        "metaType": "PORTAL_SPECIFIC",
        "id": "7232155",
        "fullyQualifiedName": "p19936848_Animal",
        "createdAt": "2022-06-17T18:40:27.019Z",
        "updatedAt": "2022-06-17T18:40:27.019Z",
        "objectTypeId": "2-7232155",
        "properties": [
            {
                "name": "name",
                "label": "Animal name",
                "type": "string",
                "fieldType": "text",
                "description": "The animal name.",
                "groupName": "animal_information",
                "options": [],
                "displayOrder": -1,
                "calculated": False,
                "externalOptions": False,
                "hasUniqueValue": False,
                "hidden": False,
                "hubspotDefined": False,
                "modificationMetadata": {"archivable": True, "readOnlyDefinition": True, "readOnlyValue": False},
                "formField": True,
            }
        ],
        "associations": [],
        "name": "animals",
    }


@pytest.fixture(name="expected_custom_object_json_schema")
def expected_custom_object_json_schema():
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": ["null", "object"],
        "additionalProperties": True,
        "properties": {
            "id": {"type": ["null", "string"]},
            "createdAt": {"type": ["null", "string"], "format": "date-time"},
            "updatedAt": {"type": ["null", "string"], "format": "date-time"},
            "archived": {"type": ["null", "boolean"]},
            "properties": {"type": ["null", "object"], "properties": {"name": {"type": ["null", "string"]}}},
            "properties_name": {"type": ["null", "string"]},
        },
    }


def test_custom_object_stream_doesnt_call_hubspot_to_get_json_schema_if_available(
    requests_mock, custom_object_schema, expected_custom_object_json_schema, common_params
):
    stream = CustomObject(
        entity="animals",
        schema=expected_custom_object_json_schema,
        fully_qualified_name="p123_animals",
        custom_properties={"name": {"type": ["null", "string"]}},
        **common_params,
    )

    adapter = requests_mock.register_uri("GET", "/crm/v3/schemas", [{"json": {"results": [custom_object_schema]}}])
    json_schema = stream.get_json_schema()

    assert json_schema == expected_custom_object_json_schema
    assert not adapter.called


def test_get_custom_objects_metadata_success(requests_mock, custom_object_schema, expected_custom_object_json_schema, api):
    requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    for entity, fully_qualified_name, schema, custom_properties in api.get_custom_objects_metadata():
        assert entity == "animals"
        assert fully_qualified_name == "p19936848_Animal"
        assert schema == expected_custom_object_json_schema


@pytest.mark.parametrize(
    "input_data, unnest_fields, expected_output",
    (
        (
            [{"id": 1, "createdAt": "2020-01-01", "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"}}],
            [],
            [{"id": 1, "createdAt": "2020-01-01", "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"}}],
        ),
        (
            [
                {
                    "id": 1,
                    "createdAt": "2020-01-01",
                    "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"},
                    "properties": {"phone": "+38044-111-111", "address": "31, Cleveland str, Washington DC"},
                }
            ],
            [],
            [
                {
                    "id": 1,
                    "createdAt": "2020-01-01",
                    "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"},
                    "properties": {"phone": "+38044-111-111", "address": "31, Cleveland str, Washington DC"},
                    "properties_phone": "+38044-111-111",
                    "properties_address": "31, Cleveland str, Washington DC",
                }
            ],
        ),
        (
            [
                {
                    "id": 1,
                    "createdAt": "2020-01-01",
                    "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"},
                }
            ],
            ["email"],
            [
                {
                    "id": 1,
                    "createdAt": "2020-01-01",
                    "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"},
                    "email_from": "integration-test@airbyte.io",
                    "email_to": "michael_scott@gmail.com",
                }
            ],
        ),
        (
            [
                {
                    "id": 1,
                    "createdAt": "2020-01-01",
                    "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"},
                    "properties": {"phone": "+38044-111-111", "address": "31, Cleveland str, Washington DC"},
                }
            ],
            ["email"],
            [
                {
                    "id": 1,
                    "createdAt": "2020-01-01",
                    "email": {"from": "integration-test@airbyte.io", "to": "michael_scott@gmail.com"},
                    "email_from": "integration-test@airbyte.io",
                    "email_to": "michael_scott@gmail.com",
                    "properties": {"phone": "+38044-111-111", "address": "31, Cleveland str, Washington DC"},
                    "properties_phone": "+38044-111-111",
                    "properties_address": "31, Cleveland str, Washington DC",
                }
            ],
        ),
    ),
)
def test_records_unnester(input_data, unnest_fields, expected_output):
    unnester = RecordUnnester(fields=unnest_fields)
    assert list(unnester.unnest(input_data)) == expected_output


def test_web_analytics_stream_slices(common_params, mocker):
    parent_slicer_mock = mocker.patch("airbyte_cdk.sources.streams.http.HttpSubStream.stream_slices")
    parent_slicer_mock.return_value = (_ for _ in [{"parent": {"id": 1}}])

    pendulum_now_mock = mocker.patch("pendulum.now")
    pendulum_now_mock.return_value = pendulum.parse(common_params["start_date"]).add(days=50)

    stream = ContactsWebAnalytics(**common_params)
    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field="occurredAt"))

    assert len(slices) == 2
    assert all(map(lambda slice: slice["objectId"] == 1, slices))

    assert [("2021-01-10T00:00:00Z", "2021-02-09T00:00:00Z"), ("2021-02-09T00:00:00Z", "2021-03-01T00:00:00Z")] == [
        (s["occurredAfter"], s["occurredBefore"]) for s in slices
    ]


def test_web_analytics_latest_state(common_params, mocker):
    parent_slicer_mock = mocker.patch("airbyte_cdk.sources.streams.http.HttpSubStream.stream_slices")
    parent_slicer_mock.return_value = (_ for _ in [{"parent": {"id": "1"}}])

    pendulum_now_mock = mocker.patch("pendulum.now")
    pendulum_now_mock.return_value = pendulum.parse(common_params["start_date"]).add(days=10)

    parent_slicer_mock = mocker.patch("source_hubspot.streams.BaseStream.read_records")
    parent_slicer_mock.return_value = (_ for _ in [{"objectId": "1", "occurredAt": "2021-01-02T00:00:00Z"}])

    stream = ContactsWebAnalytics(**common_params)
    stream.state = {"1": {"occurredAt": "2021-01-01T00:00:00Z"}}
    slices = list(stream.stream_slices(SyncMode.incremental, cursor_field="occurredAt"))
    records = [
        list(stream.read_records(SyncMode.incremental, cursor_field="occurredAt", stream_slice=stream_slice)) for stream_slice in slices
    ]

    assert len(slices) == 1
    assert len(records) == 1
    assert len(records[0]) == 1
    assert records[0][0]["objectId"] == "1"
    assert stream.state["1"]["occurredAt"] == "2021-01-02T00:00:00Z"


@pytest.mark.parametrize(
    "stream_class, cursor_value, data_to_cast, expected_casted_data",
    [
        ("marketing_emails", {"updated": 1634050455543}, {"rootMicId": 123456}, {"rootMicId": "123456"}),
        ("marketing_emails", {"updated": 1634050455543}, {"rootMicId": None}, {"rootMicId": None}),
        ("marketing_emails", {"updated": 1634050455543}, {"rootMicId": "123456"}, {"rootMicId": "123456"}),
        ("marketing_emails", {"updated": 1634050455543}, {"rootMicId": 1234.56}, {"rootMicId": "1234.56"}),
    ],
)
@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_cast_record_fields_with_schema_if_needed(
    mock_get_custom_object_stream, stream_class, cursor_value, requests_mock, common_params, data_to_cast, expected_casted_data, config
):
    """
    Test that the stream cast record fields with stream json schema if needed
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    if isinstance(stream_class, str):
        stream = find_stream(stream_class, config)
        data_field = stream.retriever.record_selector.extractor.field_path[0]
    else:
        stream = stream_class(**common_params)
        data_field = stream.data_field

    responses = [
        {
            "json": {
                data_field: [
                    {
                        "id": "test_id",
                        "created": "2022-02-25T16:43:11Z",
                    }
                    | data_to_cast
                    | cursor_value
                ],
            }
        }
    ]

    stream._sync_mode = SyncMode.full_refresh

    if isinstance(stream_class, str):
        stream_url = stream.retriever.requester.url_base + stream.retriever.requester.path
    else:
        stream_url = stream.url

    stream._sync_mode = None

    requests_mock.register_uri("GET", stream_url, responses)
    records = read_full_refresh(stream)
    record = records[0]
    for casted_key, casted_value in expected_casted_data.items():
        assert record[casted_key] == casted_value


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
            Deals,
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "integer")],
            {"hs_closed_amount": "123456"},
            {"hs_closed_amount": 123456},
        ),
        (
            Deals,
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "number")],
            {"hs_closed_amount": "123456.10"},
            {"hs_closed_amount": 123456.10},
        ),
        (
            Deals,
            "deal",
            {"updatedAt": "2022-02-25T16:43:11Z"},
            [("hs_closed_amount", "boolean")],
            {"hs_closed_amount": "1"},
            {"hs_closed_amount": True},
        ),
    ],
)
@mock.patch("source_hubspot.source.SourceHubspot.get_custom_object_streams")
def test_cast_record_fields_if_needed(
    mock_get_custom_object_streams,
    stream_class,
    endpoint,
    cursor_value,
    fake_properties_list_response,
    requests_mock,
    common_params,
    data_to_cast,
    expected_casted_data,
    custom_object_schema,
    config,
):
    """
    Test that the stream cast record fields in properties key with properties endpoint response if needed
    """
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)

    if isinstance(stream_class, str):
        stream = find_stream(stream_class, config)
        data_field = stream.retriever.record_selector.extractor.field_path[0]
    else:
        stream = stream_class(**common_params)
        data_field = stream.data_field

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

    stream._sync_mode = SyncMode.full_refresh
    if isinstance(stream_class, str):
        stream_url = stream.retriever.requester.url_base + "/" + stream.retriever.requester.get_path()
    else:
        stream_url = stream.url
    stream._sync_mode = None

    requests_mock.register_uri("GET", stream_url, responses)
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)
    records = read_full_refresh(stream)
    assert records
    record = records[0]
    for casted_key, casted_value in expected_casted_data.items():
        assert record["properties"][casted_key] == casted_value
