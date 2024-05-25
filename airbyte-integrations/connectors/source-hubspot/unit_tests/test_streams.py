#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from source_hubspot.streams import (
    Campaigns,
    Companies,
    ContactLists,
    Contacts,
    ContactsListMemberships,
    ContactsMergedAudit,
    ContactsPropertyHistory,
    ContactsWebAnalytics,
    CustomObject,
    DealPipelines,
    Deals,
    DealsArchived,
    EmailEvents,
    EmailSubscriptions,
    EngagementsCalls,
    EngagementsEmails,
    EngagementsMeetings,
    EngagementsNotes,
    EngagementsTasks,
    Forms,
    FormSubmissions,
    Goals,
    LineItems,
    MarketingEmails,
    Owners,
    OwnersArchived,
    Products,
    RecordUnnester,
    TicketPipelines,
    Tickets,
    Workflows,
)

from .utils import read_full_refresh, read_incremental


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_updated_at_field_non_exist_handler(requests_mock, common_params, fake_properties_list):
    stream = ContactLists(**common_params)

    responses = [
        {
            "json": {
                stream.data_field: [
                    {
                        "id": "test_id",
                        "createdAt": "2022-03-25T16:43:11Z",
                    },
                ],
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

    requests_mock.register_uri("GET", stream.url, responses)
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", properties_response)

    _, stream_state = read_incremental(stream, {})

    expected = int(pendulum.parse(common_params["start_date"]).timestamp() * 1000)

    assert stream_state[stream.updated_at_field] == expected


@pytest.mark.parametrize(
    "stream, endpoint, cursor_value",
    [
        (Campaigns, "campaigns", {"lastUpdatedTime": 1675121674226}),
        (Companies, "company", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (ContactLists, "contact", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Contacts, "contact", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (ContactsMergedAudit, "contact", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Deals, "deal", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (DealsArchived, "deal", {"archivedAt": "2022-02-25T16:43:11Z"}),
        (DealPipelines, "deal", {"updatedAt": 1675121674226}),
        (EmailEvents, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (EmailSubscriptions, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (EngagementsCalls, "calls", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (EngagementsEmails, "emails", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (EngagementsMeetings, "meetings", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (EngagementsNotes, "notes", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (EngagementsTasks, "tasks", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Forms, "form", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (FormSubmissions, "form", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Goals, "goal_targets", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (LineItems, "line_item", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (MarketingEmails, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Owners, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (OwnersArchived, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Products, "product", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (TicketPipelines, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Tickets, "ticket", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Workflows, "", {"updatedAt": 1675121674226}),
    ],
)
def test_streams_read(stream, endpoint, cursor_value, requests_mock, common_params, fake_properties_list):
    stream = stream(**common_params)
    responses = [
        {
            "json": {
                stream.data_field: [
                    {
                        "id": "test_id",
                        "created": "2022-02-25T16:43:11Z",
                    }
                    | cursor_value
                ],
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
                stream.data_field: [
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
                "contacts": [
                    {"vid": "test_id", "merge-audits": [{"canonical-vid": 2, "vid-to-merge": 5608, "timestamp": 1653322839932}]}
                ]
            },
            "status_code": 200,
        }
    ]

    is_form_submission = isinstance(stream, FormSubmissions)
    stream._sync_mode = SyncMode.full_refresh
    stream_url = stream.url + "/test_id" if is_form_submission else stream.url
    stream._sync_mode = None

    requests_mock.register_uri("GET", stream_url, responses)
    requests_mock.register_uri("GET", "/crm/v3/objects/contact", contact_response)
    requests_mock.register_uri("GET", "/contacts/v1/lists/all/contacts/all", contact_lists_v1_response)
    requests_mock.register_uri("GET", "/marketing/v3/forms", responses)
    requests_mock.register_uri("GET", "/email/public/v1/campaigns/test_id", responses)
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)
    requests_mock.register_uri("GET", "/contacts/v1/contact/vids/batch/", read_batch_contact_v1_response)

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
def test_common_error_retry(error_response, requests_mock, common_params, fake_properties_list):
    """Error once, check that we retry and not fail"""
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

    stream = Companies(**common_params)

    response = {
        stream.data_field: [
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
    stream_url = stream.url
    stream._sync_mode = None
    requests_mock.register_uri("GET", stream_url, [{"json": response}])
    records = read_full_refresh(stream)

    assert [response[stream.data_field][0]] == records


def test_contact_lists_transform(requests_mock, common_params):
    stream = ContactLists(**common_params)

    responses = [
        {
            "json": {
                stream.data_field: [
                    {
                        "listId": 1,
                        "createdAt": 1654117200000,
                        "filters": [[{"value": "@hubspot"}]],
                    },
                    {
                        "listId": 2,
                        "createdAt": 1654117200001,
                        "filters": [[{"value": True}, {"value": "FORM_ABUSE"}]],
                    },
                    {
                        "listId": 3,
                        "createdAt": 1654117200002,
                        "filters": [[{"value": 1000}]],
                    },
                ]
            }
        }
    ]

    requests_mock.register_uri("GET", stream.url, responses)
    records = read_full_refresh(stream)

    assert records[0]["filters"][0][0]["value"] == "@hubspot"
    assert records[1]["filters"][0][0]["value"] == "True"
    assert records[1]["filters"][0][1]["value"] == "FORM_ABUSE"
    assert records[2]["filters"][0][0]["value"] == "1000"


def test_client_side_incremental_stream(requests_mock, common_params, fake_properties_list):
    stream = Forms(**common_params)
    latest_cursor_value = "2030-01-30T23:46:36.287Z"
    responses = [
        {
            "json": {
                stream.data_field: [
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

    requests_mock.register_uri("GET", stream.url, responses)
    requests_mock.register_uri("GET", "/properties/v2/form/properties", properties_response)

    list(stream.read_records(SyncMode.incremental))
    assert stream.state == {stream.cursor_field: pendulum.parse(latest_cursor_value).to_rfc3339_string()}


@pytest.mark.parametrize(
    "state, record, expected",
    [
        (
            {"updatedAt": ""},
            {"id": "test_id_1", "updatedAt": "2023-01-30T23:46:36.287Z"},
            (True, {"updatedAt": "2023-01-30T23:46:36.287000+00:00"}),
        ),
        (
            {"updatedAt": "2023-01-30T23:46:36.287000+00:00"},
            {"id": "test_id_1", "updatedAt": "2023-01-29T01:02:03.123Z"},
            (False, {"updatedAt": "2023-01-30T23:46:36.287000+00:00"}),
        ),
    ],
    ids=[
        "Empty Sting in state + new record",
        "State + old record",
    ],
)
def test_empty_string_in_state(state, record, expected, requests_mock, common_params, fake_properties_list):
    stream = Forms(**common_params)
    stream.state = state
    # overcome the availability strartegy issues by mocking the responses
    # A.K.A: not related to the test at all, but definetely required.
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "CreatedAt": "2023-01-30T23:46:24.355Z", "updatedAt": "2023-01-30T23:46:36.287Z"}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]
    requests_mock.register_uri("GET", stream.url, json=record)
    requests_mock.register_uri("GET", "/properties/v2/form/properties", properties_response)
    # end of mocking `availability strategy`

    result = stream.filter_by_state(stream.state, record)
    assert result == expected[0]
    assert stream.state == expected[1]


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


def test_contacts_merged_audit_stream_doesnt_call_hubspot_to_get_json_schema(requests_mock, common_params):
    stream = ContactsMergedAudit(**common_params)

    adapter = requests_mock.register_uri(
        "GET",
        f"/properties/v2/{stream.entity}/properties",
        [
            {
                "json": [
                    {
                        "name": "hs_object_id",
                        "label": "Record ID",
                        "type": "number",
                    }
                ]
            }
        ],
    )
    _ = stream.get_json_schema()

    assert not adapter.called


def test_get_custom_objects_metadata_success(requests_mock, custom_object_schema, expected_custom_object_json_schema, api):
    requests_mock.register_uri("GET", "/crm/v3/schemas", json={"results": [custom_object_schema]})
    for (entity, fully_qualified_name, schema, custom_properties) in api.get_custom_objects_metadata():
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

    parent_slicer_mock = mocker.patch("source_hubspot.streams.Stream.read_records")
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


def test_property_history_transform(common_params):
    stream = ContactsPropertyHistory(**common_params)
    versions = [{"value": "Georgia", "timestamp": 1645135236625}]
    records = [
        {
            "vid": 1,
            "canonical-vid": 1,
            "portal-id": 1,
            "is-contact": True,
            "properties": {"hs_country": {"versions": versions}, "lastmodifieddate": {"value": 1645135236625}},
        }
    ]
    assert [
        {"vid": 1, "canonical-vid": 1, "portal-id": 1, "is-contact": True, "property": "hs_country", **version} for version in versions
    ] == list(stream._transform(records=records))


def test_contacts_membership_transform(common_params):
    stream = ContactsListMemberships(**common_params)
    versions = [{"value": "Georgia", "timestamp": 1645135236625}]
    memberships = [{"membership": 1}]
    records = [
        {
            "vid": 1,
            "canonical-vid": 1,
            "portal-id": 1,
            "is-contact": True,
            "properties": {"hs_country": {"versions": versions}, "lastmodifieddate": {"value": 1645135236625}},
            "list-memberships": memberships,
        }
    ]
    assert [{"membership": 1, "canonical-vid": 1} for _ in versions] == list(stream._transform(records=records))
