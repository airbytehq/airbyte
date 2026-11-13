# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
import re
from unittest.mock import patch

import requests
from requests.exceptions import ChunkedEncodingError

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.conftest import create_source
from unit_tests.mock_server.helpers import (
    API_BASE,
    build_incremental_query,
    build_stream_response,
    get_customer_client_query,
    mock_accessible_accounts,
    mock_incremental_stream,
    mock_oauth,
    setup_full_refresh_parent_mocks,
)


_CUSTOMER_ID = "1234567890"
_STREAM_NAME = "ad_group"

_RECORD_FIRST_HALF = {
    "campaign": {"id": "700001"},
    "adGroup": {
        "id": "400001",
        "name": "Ad Group First Half",
        "status": "ENABLED",
        "campaign": f"customers/{_CUSTOMER_ID}/campaigns/700001",
    },
    "segments": {"date": "2024-01-03"},
    "metrics": {"costMicros": "1000000"},
}

_RECORD_SECOND_HALF = {
    "campaign": {"id": "700001"},
    "adGroup": {
        "id": "400002",
        "name": "Ad Group Second Half",
        "status": "ENABLED",
        "campaign": f"customers/{_CUSTOMER_ID}/campaigns/700001",
    },
    "segments": {"date": "2024-01-10"},
    "metrics": {"costMicros": "2000000"},
}

_RECORD_SINGLE_DAY = {
    "campaign": {"id": "700001"},
    "adGroup": {
        "id": "400003",
        "name": "Ad Group Single Day",
        "status": "ENABLED",
        "campaign": f"customers/{_CUSTOMER_ID}/campaigns/700001",
    },
    "segments": {"date": "2024-01-01"},
    "metrics": {"costMicros": "500000"},
}


def test_chunked_encoding_error_triggers_slice_split():
    """
    When ChunkedEncodingError occurs on the first read, GoogleAdsRetriever
    splits the 14-day date range into two 7-day sub-slices and retries each.
    """
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-01",
            end_date="2024-01-07",
            response=build_stream_response([_RECORD_FIRST_HALF]),
        )
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-08",
            end_date="2024-01-14",
            response=build_stream_response([_RECORD_SECOND_HALF]),
        )

        original_read_pages = SimpleRetriever._read_pages
        call_count = 0

        def read_pages_raising_first_call(self, records_generator_fn, stream_slice):
            nonlocal call_count
            cursor = getattr(stream_slice, "cursor_slice", {})
            is_target = cursor.get("start_time") == "2024-01-01" and cursor.get("end_time") == "2024-01-14"
            if is_target:
                call_count += 1
                if call_count == 1:
                    raise ChunkedEncodingError("simulated midstream break")
            yield from original_read_pages(self, records_generator_fn, stream_slice)

        with patch.object(SimpleRetriever, "_read_pages", read_pages_raising_first_call):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 2
    ad_group_ids = sorted(r.record.data["ad_group.id"] for r in output.records)
    assert ad_group_ids == [400001, 400002]


def test_chunked_encoding_error_retries_on_minimum_slice():
    """
    When ChunkedEncodingError occurs on a 1-day (minimum) slice that cannot
    be split further, GoogleAdsRetriever retries the same slice and succeeds.
    """
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-01").build()

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-01",
            end_date="2024-01-01",
            response=build_stream_response([_RECORD_SINGLE_DAY]),
        )

        original_read_pages = SimpleRetriever._read_pages
        call_count = 0

        def read_pages_failing_twice(self, records_generator_fn, stream_slice):
            nonlocal call_count
            cursor = getattr(stream_slice, "cursor_slice", {})
            is_target = cursor.get("start_time") == "2024-01-01" and cursor.get("end_time") == "2024-01-01"
            if is_target:
                call_count += 1
                if call_count <= 2:
                    raise ChunkedEncodingError("simulated transient error")
            yield from original_read_pages(self, records_generator_fn, stream_slice)

        with patch.object(SimpleRetriever, "_read_pages", read_pages_failing_twice):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    assert output.records[0].record.data["ad_group.id"] == 400003


_CUSTOMER_A = "1111111111"
_CUSTOMER_B = "2222222222"


def _customer_client_response_for(customer_ids):
    return HttpResponse(
        body=json.dumps(
            [
                {
                    "results": [
                        {
                            "customerClient": {
                                "clientCustomer": f"customers/{customer_id}",
                                "level": "1",
                                "id": customer_id,
                                "manager": False,
                                "timeZone": "America/New_York",
                                "status": "ENABLED",
                            }
                        }
                        for customer_id in customer_ids
                    ]
                }
            ]
        ),
        status_code=200,
    )


def _record(customer_id: str, ad_group_id: str, date: str) -> dict:
    return {
        "campaign": {"id": "700001"},
        "adGroup": {
            "id": ad_group_id,
            "name": f"Ad Group {ad_group_id}",
            "status": "ENABLED",
            "campaign": f"customers/{customer_id}/campaigns/700001",
        },
        "segments": {"date": date},
        "metrics": {"costMicros": "1000000"},
    }


def test_chunked_encoding_error_on_one_customer_splits_only_that_customer():
    """
    Two customers under one manager. Customer B's 14-day window drops mid-stream: the CDK splits it and reads
    both halves. Customer A is read once. Each customer ends with its own cursor.
    """
    # `customer_id` lists the client accounts to sync (CustomerClientFilter drops any other client); the
    # manager they are listed under is the accessible account.
    config = (
        ConfigBuilder().with_customer_id(f"{_CUSTOMER_A},{_CUSTOMER_B}").with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    )

    with HttpMocker() as http_mocker:
        mock_oauth(http_mocker)
        mock_accessible_accounts(http_mocker, customer_ids=[_CUSTOMER_ID])
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream", body=json.dumps({"query": get_customer_client_query()})
            ),
            _customer_client_response_for([_CUSTOMER_A, _CUSTOMER_B]),
        )
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            customer_id=_CUSTOMER_A,
            start_date="2024-01-01",
            end_date="2024-01-14",
            response=build_stream_response([_record(_CUSTOMER_A, "400010", "2024-01-10")]),
        )
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            customer_id=_CUSTOMER_B,
            start_date="2024-01-01",
            end_date="2024-01-07",
            response=build_stream_response([_record(_CUSTOMER_B, "400003", "2024-01-03")]),
        )
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            customer_id=_CUSTOMER_B,
            start_date="2024-01-08",
            end_date="2024-01-14",
            response=build_stream_response([_record(_CUSTOMER_B, "400012", "2024-01-12")]),
        )

        original_read_pages = SimpleRetriever._read_pages

        def read_pages_dropping_customer_b_full_window(self, records_generator_fn, stream_slice):
            cursor = getattr(stream_slice, "cursor_slice", {})
            # the partition carries the parent's `clientCustomer` resource name, not the bare id
            is_customer_b = stream_slice.partition.get("customer_id") == f"customers/{_CUSTOMER_B}"
            if is_customer_b and cursor.get("start_time") == "2024-01-01" and cursor.get("end_time") == "2024-01-14":
                raise ChunkedEncodingError("simulated midstream break")
            yield from original_read_pages(self, records_generator_fn, stream_slice)

        with patch.object(SimpleRetriever, "_read_pages", read_pages_dropping_customer_b_full_window):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)

    assert sorted(r.record.data["ad_group.id"] for r in output.records) == [400003, 400010, 400012]
    final_state = output.most_recent_state.stream_state.__dict__
    states = {state["partition"]["customer_id"]: state["cursor"]["segments.date"] for state in final_state["states"]}
    assert states == {f"customers/{_CUSTOMER_A}": "2024-01-10", f"customers/{_CUSTOMER_B}": "2024-01-12"}


def test_drop_raised_while_decoding_the_response_body_splits_the_window():
    """
    The real failure point: the request succeeds and the body breaks while GoogleAdsStreamingDecoder reads it (requests
    raises ChunkedEncodingError from iter_content). The error reaches GoogleAdsRetriever unwrapped, so the full window is
    sent once and then split.
    """
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    full_window_request = HttpRequest(
        url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
        body=json.dumps({"query": build_incremental_query(_STREAM_NAME, "2024-01-01", "2024-01-14")}),
    )
    original_iter_content = requests.models.Response.iter_content

    def iter_content_breaking_the_full_window(self, *args, **kwargs):
        body = getattr(self.request, "body", None) or b""
        if "BETWEEN '2024-01-01' AND '2024-01-14'" in (body.decode() if isinstance(body, bytes) else body):

            def broken_stream():
                raise ChunkedEncodingError("Connection broken: IncompleteRead(0 bytes read)")
                yield

            return broken_stream()
        return original_iter_content(self, *args, **kwargs)

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(full_window_request, build_stream_response([_RECORD_FIRST_HALF, _RECORD_SECOND_HALF]))
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-01",
            end_date="2024-01-07",
            response=build_stream_response([_RECORD_FIRST_HALF]),
        )
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-08",
            end_date="2024-01-14",
            response=build_stream_response([_RECORD_SECOND_HALF]),
        )

        with patch.object(requests.models.Response, "iter_content", iter_content_breaking_the_full_window):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)
        http_mocker.assert_number_of_calls(full_window_request, 1)

    assert sorted(r.record.data["ad_group.id"] for r in output.records) == [400001, 400002]
    final_state = output.most_recent_state.stream_state.__dict__
    states = {state["partition"]["customer_id"]: state["cursor"]["segments.date"] for state in final_state["states"]}
    assert states == {f"customers/{_CUSTOMER_ID}": "2024-01-10"}


def test_drop_after_records_were_emitted_replays_them_and_keeps_the_latest_cursor():
    """A large report drops after its first row was emitted: the split re-emits that row (at-least-once)."""
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        for start_date, end_date, records in [
            ("2024-01-01", "2024-01-14", [_RECORD_FIRST_HALF, _RECORD_SECOND_HALF]),
            ("2024-01-01", "2024-01-07", [_RECORD_FIRST_HALF]),
            ("2024-01-08", "2024-01-14", [_RECORD_SECOND_HALF]),
        ]:
            mock_incremental_stream(
                http_mocker, _STREAM_NAME, start_date=start_date, end_date=end_date, response=build_stream_response(records)
            )

        original_read_pages = SimpleRetriever._read_pages

        def read_pages_dropping_after_first_record(self, records_generator_fn, stream_slice):
            records = original_read_pages(self, records_generator_fn, stream_slice)
            cursor = stream_slice.cursor_slice
            if self.name == _STREAM_NAME and cursor.get("start_time") == "2024-01-01" and cursor.get("end_time") == "2024-01-14":
                yield next(iter(records))
                raise ChunkedEncodingError("simulated midstream break")
            yield from records

        with patch.object(SimpleRetriever, "_read_pages", read_pages_dropping_after_first_record):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog)

    assert [r.record.data["ad_group.id"] for r in output.records] == [400001, 400001, 400002]
    final_state = output.most_recent_state.stream_state.__dict__
    states = {state["partition"]["customer_id"]: state["cursor"]["segments.date"] for state in final_state["states"]}
    assert states == {f"customers/{_CUSTOMER_ID}": "2024-01-10"}


def test_drop_that_persists_at_the_one_day_floor_fails_without_checkpointing_the_window():
    """
    Every window containing 2024-01-08 drops: 01..14 >> 01..07 (read) and 08..14 >> 08..10 >> 08..08, which is retried
    3 times and then fails as a transient error. The partition is never closed, so no state moves past the start.
    """
    config = ConfigBuilder().with_start_date("2024-01-01").with_end_date("2024-01-14").build()
    read_windows = []

    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        mock_incremental_stream(
            http_mocker,
            _STREAM_NAME,
            start_date="2024-01-01",
            end_date="2024-01-07",
            response=build_stream_response([_RECORD_FIRST_HALF]),
        )

        original_read_pages = SimpleRetriever._read_pages

        def read_pages_dropping_windows_with_jan_8(self, records_generator_fn, stream_slice):
            if self.name == _STREAM_NAME:
                start, end = stream_slice.cursor_slice.get("start_time"), stream_slice.cursor_slice.get("end_time")
                read_windows.append((start, end))
                if start <= "2024-01-08" <= end:
                    raise ChunkedEncodingError("simulated midstream break")
            yield from original_read_pages(self, records_generator_fn, stream_slice)

        with patch.object(SimpleRetriever, "_read_pages", read_pages_dropping_windows_with_jan_8):
            catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
            source = create_source(config=config, catalog=catalog)
            output = read(source, config=config, catalog=catalog, expecting_exception=True)

    assert read_windows == [
        ("2024-01-01", "2024-01-14"),
        ("2024-01-01", "2024-01-07"),
        ("2024-01-08", "2024-01-14"),
        ("2024-01-08", "2024-01-10"),
        *[("2024-01-08", "2024-01-08")] * 4,
    ]
    assert [r.record.data["ad_group.id"] for r in output.records] == [400001]
    stream_errors = [
        (e.trace.error.failure_type, e.trace.error.message)
        for e in output.errors
        if e.trace.error.stream_descriptor and e.trace.error.stream_descriptor.name == _STREAM_NAME
    ]
    assert stream_errors == [
        (
            FailureType.transient_error,
            "Response stream was interrupted. The slice is already at minimum size (1 day) and 3 retries were exhausted.",
        )
    ]
    emitted = [
        json.dumps(m.state.stream.stream_state.__dict__, default=vars)
        for m in output.state_messages
        if m.state.stream.stream_descriptor.name == _STREAM_NAME
    ]
    assert not [date for state in emitted for date in re.findall(r'"segments\.date": "([0-9-]+)"', state) if date >= "2024-01-03"]
