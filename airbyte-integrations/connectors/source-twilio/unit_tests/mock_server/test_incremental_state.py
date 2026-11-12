# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.twilio.com/2010-04-01"
CONFIG = {**TEST_CONFIG, "start_date": "2022-09-15T00:00:00Z"}


def _read(stream_name: str, state_blob: dict | None = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    state = StateBuilder().with_stream_state(stream_name, state_blob).build() if state_blob else None
    return read(get_source(CONFIG, state), CONFIG, catalog, state)


def _mock_accounts(http_mocker: HttpMocker, resource: str, uri: str) -> None:
    http_mocker.get(
        HttpRequest(url=f"{BASE}/Accounts.json", query_params={"PageSize": "1000"}),
        HttpResponse(body=json.dumps({"accounts": [{"sid": "AC123", "subresource_uris": {resource: uri}}]}), status_code=200),
    )


def _window_request(path: str, lower_key: str, upper_key: str, lower: str, upper: str) -> HttpRequest:
    return HttpRequest(url=f"{BASE}{path}", query_params={lower_key: lower, upper_key: upper, "PageSize": "1000"})


def _response(stream_name: str, records: list[dict]) -> HttpResponse:
    return HttpResponse(body=json.dumps({stream_name: records}), status_code=200)


@pytest.mark.parametrize(
    "stream_name,path,cursor_field,lower_key,upper_key",
    [
        pytest.param("messages", "/Accounts/AC123/Messages.json", "date_sent", "DateSent>", "DateSent<", id="messages"),
        pytest.param("recordings", "/Accounts/AC123/Recordings.json", "date_created", "DateCreated>", "DateCreated<", id="recordings"),
    ],
)
@HttpMocker()
def test_second_incremental_read_resumes_from_the_partition_cursor(
    http_mocker: HttpMocker, stream_name: str, path: str, cursor_field: str, lower_key: str, upper_key: str
):
    """
    A first read spanning several monthly request windows must leave the account's partition cursor at the
    newest record, so that the next read requests a single window starting there instead of the full history.
    """
    # The decorator's mocker instance is shared by every parametrized case, so drop the previous case's matchers.
    http_mocker.clear_all_matchers()
    uri = f"/2010-04-01{path}"
    partition = {"subresource_uri": uri, "parent_slice": {}}
    first_record = {"sid": "R1", cursor_field: "Thu, 20 Oct 2022 10:00:00 +0000"}
    second_record = {"sid": "R2", cursor_field: "Thu, 17 Nov 2022 10:00:00 +0000"}
    _mock_accounts(http_mocker, stream_name, uri)

    # First read, no state: three request windows, with the only record in the second one.
    first_read_windows = [
        (_window_request(path, lower_key, upper_key, "2022-09-15 00:00:00Z", "2022-10-14 23:59:59Z"), []),
        (_window_request(path, lower_key, upper_key, "2022-10-15 00:00:00Z", "2022-11-14 23:59:59Z"), [first_record]),
        (_window_request(path, lower_key, upper_key, "2022-11-15 00:00:00Z", "2022-11-16 12:03:11Z"), []),
    ]
    for request, records in first_read_windows:
        http_mocker.get(request, _response(stream_name, records))

    with freeze_time("2022-11-16 12:03:11+00:00"):
        first_output = _read(stream_name)

    assert not first_output.errors
    assert [record.record.data["sid"] for record in first_output.records] == ["R1"]
    first_state = first_output.most_recent_state.stream_state.__dict__
    assert first_state["states"] == [{"partition": partition, "cursor": {cursor_field: "2022-10-20 10:00:00Z"}}]
    assert first_state["state"] == {cursor_field: "2022-10-20 10:00:00Z"}

    # Second read, with the state of the first one: a single window starting at the partition cursor. The lower
    # bound is inclusive, so Twilio returns the boundary record R1 again; nothing older is requested.
    second_read_window = _window_request(path, lower_key, upper_key, "2022-10-20 10:00:00Z", "2022-11-18 12:03:11Z")
    http_mocker.get(second_read_window, _response(stream_name, [first_record, second_record]))

    with freeze_time("2022-11-18 12:03:11+00:00"):
        second_output = _read(stream_name, first_state)

    assert not second_output.errors
    assert [record.record.data["sid"] for record in second_output.records] == ["R1", "R2"]
    second_state = second_output.most_recent_state.stream_state.__dict__
    assert second_state["states"] == [{"partition": partition, "cursor": {cursor_field: "2022-11-17 10:00:00Z"}}]
    assert second_state["state"] == {cursor_field: "2022-11-17 10:00:00Z"}
    for request, _ in first_read_windows:
        http_mocker.assert_number_of_calls(request, 1)
    http_mocker.assert_number_of_calls(second_read_window, 1)
