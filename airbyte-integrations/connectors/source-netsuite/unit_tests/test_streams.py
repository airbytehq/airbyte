#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
import requests
from source_netsuite.streams import NetsuiteStream

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models import FailureType


def _make_stream(object_name: str = "journalentry") -> NetsuiteStream:
    """Build a minimal `NetsuiteStream` instance for testing."""
    stream = NetsuiteStream.__new__(NetsuiteStream)
    stream.object_name = object_name
    stream.base_url = "https://test.suitetalk.api.netsuite.com"
    stream.start_datetime = "2024-01-01T00:00:00Z"
    stream.window_in_days = 30
    stream.schemas = {}
    stream._records_attempted = 0
    stream._user_error_skipped = 0
    stream.index_datetime_format = 0
    stream.raise_on_http_errors = True
    stream._session = MagicMock()
    return stream


def _make_response(status_code: int, json_data: dict) -> MagicMock:
    """Build a mock `requests.Response`."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


_USER_ERROR_JSON = {
    "o:errorDetails": [
        {
            "o:errorCode": "USER_ERROR",
            "detail": "Error while accessing a resource. This record has been locked by a user defined workflow.",
        }
    ]
}


# ---------------------------------------------------------------------------
# _track_skipped_record
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "json_body, expected_skipped",
    [
        pytest.param(
            _USER_ERROR_JSON,
            1,
            id="user_error_increments_counter",
        ),
        pytest.param(
            {"o:errorDetails": [{"o:errorCode": "INVALID_PARAMETER", "detail": "some issue"}]},
            0,
            id="other_error_code_no_increment",
        ),
        pytest.param(
            {"o:errorDetails": []},
            0,
            id="empty_error_details_no_increment",
        ),
        pytest.param(
            {},
            0,
            id="missing_error_details_no_increment",
        ),
    ],
)
def test_track_skipped_record(json_body, expected_skipped):
    stream = _make_stream()
    response = _make_response(400, json_body)

    stream._track_skipped_record(response)

    assert stream._user_error_skipped == expected_skipped


def test_track_skipped_record_malformed_json():
    stream = _make_stream()
    response = MagicMock(spec=requests.Response)
    response.status_code = 400
    response.json.side_effect = ValueError("No JSON")

    stream._track_skipped_record(response)

    assert stream._user_error_skipped == 0


# ---------------------------------------------------------------------------
# fetch_record
# ---------------------------------------------------------------------------


def test_fetch_record_yields_on_200():
    stream = _make_stream()
    ok_resp = _make_response(200, {"id": "42", "type": "journalentry"})
    stream._send_request = MagicMock(return_value=ok_resp)

    results = list(stream.fetch_record({"links": [{"href": "https://test/record/42"}]}, {}))

    assert len(results) == 1
    assert results[0]["id"] == "42"
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 0


def test_fetch_record_skips_and_tracks_user_error():
    stream = _make_stream()
    err_resp = _make_response(400, _USER_ERROR_JSON)
    stream._send_request = MagicMock(return_value=err_resp)

    results = list(stream.fetch_record({"links": [{"href": "https://test/record/99"}]}, {}))

    assert results == []
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 1


def test_fetch_record_does_not_track_non_400():
    stream = _make_stream()
    resp_500 = _make_response(500, {})
    stream._send_request = MagicMock(return_value=resp_500)

    results = list(stream.fetch_record({"links": [{"href": "https://test/record/1"}]}, {}))

    assert results == []
    assert stream._records_attempted == 1
    assert stream._user_error_skipped == 0


# ---------------------------------------------------------------------------
# _emit_skipped_records_summary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attempted, skipped, should_raise",
    [
        pytest.param(100, 0, False, id="no_skips_no_warning"),
        pytest.param(100, 10, False, id="10pct_skipped_warning_only"),
        pytest.param(200, 100, False, id="exactly_50pct_no_raise"),
        pytest.param(100, 51, True, id="51pct_raises_traced_exception"),
        pytest.param(200, 101, True, id="50.5pct_raises_traced_exception"),
        pytest.param(10, 10, True, id="100pct_raises_traced_exception"),
    ],
)
def test_emit_skipped_records_summary(attempted, skipped, should_raise):
    stream = _make_stream()
    stream._records_attempted = attempted
    stream._user_error_skipped = skipped

    if should_raise:
        with pytest.raises(AirbyteTracedException) as exc_info:
            stream._emit_skipped_records_summary()
        assert exc_info.value.failure_type == FailureType.system_error
        assert str(skipped) in exc_info.value.message
        assert "workflow locks" in exc_info.value.message
    else:
        stream._emit_skipped_records_summary()


def test_emit_skipped_records_summary_warning_content(caplog):
    stream = _make_stream("salesorder")
    stream._records_attempted = 10
    stream._user_error_skipped = 3

    with caplog.at_level(logging.WARNING, logger="airbyte"):
        stream._emit_skipped_records_summary()

    assert len(caplog.records) >= 1
    warning_msg = caplog.records[-1].message
    assert "salesorder" in warning_msg
    assert "3 of 10" in warning_msg
    assert "workflow" in warning_msg.lower()


# ---------------------------------------------------------------------------
# should_retry — typo fix verification
# ---------------------------------------------------------------------------


def test_should_retry_user_error_corrected_spelling(caplog):
    stream = _make_stream()
    response = _make_response(400, _USER_ERROR_JSON)

    with caplog.at_level(logging.ERROR, logger="airbyte"):
        result = stream.should_retry(response)

    assert result is False
    error_msgs = [r.message for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(error_msgs) >= 1
    assert "occurred" in error_msgs[0]
    assert "occured" not in error_msgs[0]


# ---------------------------------------------------------------------------
# Integration: mixed OK and USER_ERROR across multiple records
# ---------------------------------------------------------------------------


def test_fetch_record_accumulation_mixed_responses():
    stream = _make_stream()
    ok_resp = _make_response(200, {"id": "1", "type": "journalentry"})
    err_resp = _make_response(400, _USER_ERROR_JSON)
    call_count = 0

    def mock_send_request(prep_req, kwargs):
        nonlocal call_count
        call_count += 1
        return ok_resp if call_count % 2 == 1 else err_resp

    stream._send_request = mock_send_request

    all_results = []
    for i in range(6):
        all_results.extend(stream.fetch_record({"links": [{"href": f"https://test/record/{i}"}]}, {}))

    assert stream._records_attempted == 6
    assert stream._user_error_skipped == 3
    assert len(all_results) == 3
