#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import SyncMode
from source_pipedrive.streams import (
    Activities,
    ActivityFields,
    DealFields,
    Deals,
    Leads,
    OrganizationFields,
    Organizations,
    PersonFields,
    Persons,
    PipedriveStream,
    Pipelines,
    Stages,
)

PIPEDRIVE_URL_BASE = "https://api.pipedrive.com/v1/"


def test_cursor_field_incremental(config_incremental):
    stream = PipedriveStream(**config_incremental)

    assert stream.cursor_field == "update_time"


def test_cursor_field_refresh(config_refresh):
    stream = PipedriveStream(**config_refresh)

    assert stream.cursor_field == []


def test_path_incremental(config_incremental):
    stream = PipedriveStream(**config_incremental)

    assert stream.path() == "recents"


def test_path_refresh(config_refresh):
    stream = PipedriveStream(**config_refresh)

    assert stream.path() == "pipedriveStream"


@pytest.mark.parametrize(
    "stream, endpoint",
    [
        (ActivityFields, "activityFields"),
        (DealFields, "dealFields"),
        (OrganizationFields, "organizationFields"),
        (PersonFields, "personFields"),
        (Leads, "leads"),
    ],
)
def test_streams_full_refresh(stream, endpoint, requests_mock, config_refresh):
    body = {
        "success": "true",
        "data": [{"id": 1, "update_time": "2020-10-14T11:30:36.551Z"}, {"id": 2, "update_time": "2020-10-14T11:30:36.551Z"}],
    }

    response = setup_response(200, body)

    api_token = config_refresh.get("authenticator").get("api_token")
    requests_mock.register_uri("GET", PIPEDRIVE_URL_BASE + endpoint + "?limit=50&api_token=" + api_token, response)

    stream = stream(**config_refresh)
    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    assert records


@pytest.mark.parametrize(
    "stream",
    [
        Activities,
        Deals,
        Organizations,
        Persons,
        Pipelines,
        Stages,
        # Users
    ],
)
def test_streams_incremental_sync(stream, requests_mock, config_incremental):
    body = {
        "success": "true",
        "data": [{"id": 1, "update_time": "2020-10-14T11:30:36.551Z"}, {"id": 2, "update_time": "2020-11-14T11:30:36.551Z"}],
    }

    response = setup_response(200, body)

    api_token = config_incremental.get("authenticator").get("api_token")
    requests_mock.register_uri("GET", PIPEDRIVE_URL_BASE + "recents?limit=50&api_token=" + api_token, response)

    stream = stream(**config_incremental)
    records = stream.read_records(sync_mode=SyncMode.incremental)
    stream_state = {}
    for record in records:
        stream_state = stream.get_updated_state(stream_state, latest_record=record)

    assert records
    assert stream_state["update_time"] == "2020-11-14T11:30:36.551Z"


def setup_response(status, body):
    return [
        {"json": body, "status_code": status},
    ]
