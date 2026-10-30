# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from datetime import datetime
from urllib.parse import urlencode

from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


URL = "https://api.mailersend.com/v1/activity/domain-id"


def epoch(value):
    return str(int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()))


CONFIG = {
    "api_token": "test-token",
    "domain_id": "domain-id",
    "start_date": int(epoch("2026-09-01T00:00:00Z")),
}


def query(start, end, page=None):
    params = {"date_from": epoch(start), "date_to": epoch(end), "limit": "100", "page_size": "100"}
    if page is not None:
        params["page"] = str(page)
    return params


def mock_page(requests_mock, params, records, status_code=200):
    requests_mock.get(
        f"{URL}?{urlencode(params)}",
        complete_qs=True,
        json={"data": records} if status_code == 200 else {"message": "The date to field is required."},
        status_code=status_code,
    )


def assert_requests(requests_mock, expected):
    actual = [request.qs for request in requests_mock.request_history]
    expected = [{key: [value] for key, value in params.items()} for params in expected]
    assert sorted(actual, key=lambda params: sorted(params.items())) == sorted(expected, key=lambda params: sorted(params.items()))


def read_activity(state=None, expecting_exception=False):
    catalog = CatalogBuilder().with_stream("activity", SyncMode.incremental).build()
    return read(
        get_source(CONFIG, catalog, state),
        CONFIG,
        catalog,
        state=state,
        expecting_exception=expecting_exception,
    )


@freeze_time("2026-09-03T12:00:00Z")
def test_activity_reads_daily_slices_and_iso_cursors(requests_mock):
    first = query("2026-09-01T00:00:00Z", "2026-09-01T23:59:59Z")
    next_page = query("2026-09-01T00:00:00Z", "2026-09-01T23:59:59Z", page=1)
    second = query("2026-09-02T00:00:00Z", "2026-09-02T23:59:59Z")
    third = query("2026-09-03T00:00:00Z", "2026-09-03T12:00:00Z")
    first_records = [{"id": str(i), "created_at": "2026-09-01T09:30:00.000000Z"} for i in range(100)]
    second_records = [{"id": "second", "created_at": "2026-09-02T09:30:00Z"}]
    third_records = [{"id": "third", "created_at": "2026-09-03T09:30:00.000000Z"}]
    mock_page(requests_mock, first, first_records)
    mock_page(requests_mock, next_page, [])
    mock_page(requests_mock, second, second_records)
    mock_page(requests_mock, third, third_records)

    output = read_activity()

    assert not output.errors
    assert sorted([message.record.data for message in output.records], key=lambda record: record["id"]) == sorted(
        first_records + second_records + third_records, key=lambda record: record["id"]
    )
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": epoch("2026-09-03T09:30:00Z")}
    assert_requests(requests_mock, [first, next_page, second, third])


@freeze_time("2026-09-03T12:00:00Z")
def test_activity_resumes_from_epoch_state(requests_mock):
    state = StateBuilder().with_stream_state("activity", {"created_at": epoch("2026-09-02T12:00:00Z")}).build()
    params = query("2026-09-02T12:00:00Z", "2026-09-03T12:00:00Z")
    records = [{"id": "resumed", "created_at": "2026-09-02T13:00:00.000000Z"}]
    mock_page(requests_mock, params, records)

    output = read_activity(state)

    assert not output.errors
    assert [message.record.data for message in output.records] == records
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": epoch("2026-09-02T13:00:00Z")}
    assert_requests(requests_mock, [params])


@freeze_time("2026-09-01T12:00:00Z")
def test_activity_empty_response(requests_mock):
    params = query("2026-09-01T00:00:00Z", "2026-09-01T12:00:00Z")
    mock_page(requests_mock, params, [])

    output = read_activity()

    assert not output.errors
    assert output.records == []
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": str(CONFIG["start_date"])}
    assert_requests(requests_mock, [params])


@freeze_time("2026-09-01T12:00:00Z")
def test_activity_api_error_does_not_advance_state(requests_mock, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    params = query("2026-09-01T00:00:00Z", "2026-09-01T12:00:00Z")
    mock_page(requests_mock, params, [], status_code=422)

    output = read_activity(expecting_exception=True)

    assert output.errors
    assert output.records == []
    assert output.most_recent_state.stream_state.__dict__ == {"created_at": str(CONFIG["start_date"])}
    assert_requests(requests_mock, [params] * 6)
