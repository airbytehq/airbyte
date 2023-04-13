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
    LineItems,
    MarketingEmails,
    Owners,
    Products,
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
        (LineItems, "line_item", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (MarketingEmails, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
        (Owners, "", {"updatedAt": "2022-02-25T16:43:11Z"}),
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
                    } | cursor_value
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
    is_form_submission = isinstance(stream, FormSubmissions)
    stream._sync_mode = SyncMode.full_refresh
    stream_url = stream.url + "/test_id" if is_form_submission else stream.url
    stream._sync_mode = None

    requests_mock.register_uri("GET", stream_url, responses)
    requests_mock.register_uri("GET", "/marketing/v3/forms", responses)
    requests_mock.register_uri("GET", "/email/public/v1/campaigns/test_id", responses)
    requests_mock.register_uri("GET", f"/properties/v2/{endpoint}/properties", properties_response)

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
                    {
                        "id": "test_id_1",
                        "createdAt": "2022-03-25T16:43:11Z",
                        "updatedAt": "2023-01-30T23:46:36.287Z"
                    },
                    {
                        "id": "test_id_2",
                        "createdAt": "2022-03-25T16:43:11Z",
                        "updatedAt": latest_cursor_value
                    },
                    {
                        "id": "test_id_3",
                        "createdAt": "2022-03-25T16:43:11Z",
                        "updatedAt": "2023-02-20T23:46:36.287Z"
                    },
                ],
            }
        }
    ]
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string",
                 "createdAt": "2023-01-30T23:46:24.355Z",
                 "updatedAt": "2023-01-30T23:46:36.287Z"
                 }
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]

    requests_mock.register_uri("GET", stream.url, responses)
    requests_mock.register_uri("GET", "/properties/v2/form/properties", properties_response)

    list(stream.read_records(SyncMode.incremental))
    assert stream.state == {stream.cursor_field: pendulum.parse(latest_cursor_value).to_rfc3339_string()}
