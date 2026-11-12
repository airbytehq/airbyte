# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import gzip
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import List, Optional
from unittest import TestCase

from freezegun import freeze_time

from airbyte_cdk.models import AirbyteStateBlob, FailureType, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONNECTOR_DIR = Path(__file__).parent.parent
sys.path.append(str(_CONNECTOR_DIR))

_MANIFEST_PATH = _CONNECTOR_DIR / "manifest.yaml"
_STREAM_NAME = "events"
_EXPORT_URL = "https://amplitude.com/api/2/export"
# Frozen "now" makes the default 24-hour request_time_range produce a single 20240101T00-20240101T23 window.
_NOW = "2024-01-01T23:00:00Z"
_CONFIG = {
    "api_key": "an-api-key",
    "secret_key": "a-secret-key",
    "start_date": "2024-01-01T00:00:00Z",
    "data_region": "Standard Server",
    "request_time_range": 24,
}
_FAILURE_MESSAGE = (
    "Amplitude's Export API rejects exports over 4GB (HTTP 400) and times out on very large ones (HTTP 504). "
    "An hour of data that large can only be exported with Amplitude's Amazon S3 export: "
    "https://amplitude.com/docs/data/destination-catalog/amazon-s3#run-a-manual-export. "
    "If 'request_time_range' is above 1024 hours, lower it so splitting can reach a one-hour window."
)


def _export_request(start: str, end: str) -> HttpRequest:
    return HttpRequest(url=_EXPORT_URL, query_params={"start": start, "end": end})


def _export_response(event_ids: List[str], server_upload_time: str) -> HttpResponse:
    events = "\n".join(
        json.dumps({"uuid": event_id, "server_upload_time": server_upload_time, "event_time": server_upload_time}) for event_id in event_ids
    )
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("export.json.gz", gzip.compress(events.encode()))
    return HttpResponse(archive.getvalue())


def _error_response(status_code: int) -> HttpResponse:
    return HttpResponse(json.dumps({"error": "an error"}), status_code=status_code)


def _read(expecting_exception: bool = False, stream_state: Optional[AirbyteStateBlob] = None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
    state = StateBuilder().with_stream_state(_STREAM_NAME, stream_state).build() if stream_state else None
    source = YamlDeclarativeSource(config=_CONFIG, catalog=catalog, state=state, path_to_yaml=str(_MANIFEST_PATH))
    return read(source, _CONFIG, catalog, state, expecting_exception)


def _event_ids(output: EntrypointOutput) -> List[str]:
    return sorted(message.record.data["uuid"] for message in output.records)


def _mock_split_into_halves(http_mocker: HttpMocker, status_code: int) -> None:
    http_mocker.get(_export_request("20240101T00", "20240101T23"), _error_response(status_code))
    http_mocker.get(_export_request("20240101T00", "20240101T11"), _export_response(["first-half"], "2024-01-01 05:00:00.123456"))
    http_mocker.get(_export_request("20240101T12", "20240101T23"), _export_response(["second-half"], "2024-01-01 20:00:00.123456"))


@freeze_time(_NOW)
class EventsRequestWindowSplittingTest(TestCase):
    @HttpMocker()
    def test_given_400_when_read_then_split_window_in_halves(self, http_mocker: HttpMocker) -> None:
        _mock_split_into_halves(http_mocker, 400)

        output = _read()

        assert not output.errors
        assert _event_ids(output) == ["first-half", "second-half"]

    @HttpMocker()
    def test_given_504_when_read_then_split_window_in_halves(self, http_mocker: HttpMocker) -> None:
        _mock_split_into_halves(http_mocker, 504)

        output = _read()

        assert not output.errors
        assert _event_ids(output) == ["first-half", "second-half"]

    @HttpMocker()
    def test_given_half_also_too_large_when_read_then_split_again(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_export_request("20240101T00", "20240101T23"), _error_response(400))
        http_mocker.get(_export_request("20240101T00", "20240101T11"), _error_response(400))
        http_mocker.get(_export_request("20240101T00", "20240101T05"), _export_response(["first-quarter"], "2024-01-01 03:00:00.123456"))
        http_mocker.get(_export_request("20240101T06", "20240101T11"), _export_response(["second-quarter"], "2024-01-01 08:00:00.123456"))
        http_mocker.get(_export_request("20240101T12", "20240101T23"), _export_response(["second-half"], "2024-01-01 20:00:00.123456"))

        output = _read()

        assert not output.errors
        assert _event_ids(output) == ["first-quarter", "second-half", "second-quarter"]

    @HttpMocker()
    def test_given_split_when_read_then_state_advances_to_latest_record_across_halves(self, http_mocker: HttpMocker) -> None:
        _mock_split_into_halves(http_mocker, 400)

        output = _read()

        assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"server_upload_time": "20240101T20"}

    @HttpMocker()
    def test_given_state_from_split_sync_when_next_sync_splits_partial_window_then_both_halves_read(self, http_mocker: HttpMocker) -> None:
        _mock_split_into_halves(http_mocker, 400)
        first_sync_state = _read().state_messages[-1].state.stream.stream_state
        # The 2-hour lookback restarts the window at 20240101T18 and "now" cuts it at 20240102T05.
        http_mocker.get(_export_request("20240101T18", "20240102T05"), _error_response(504))
        http_mocker.get(_export_request("20240101T18", "20240101T23"), _export_response(["late-arrival"], "2024-01-01 21:00:00.123456"))
        http_mocker.get(_export_request("20240102T00", "20240102T05"), _export_response(["next-day"], "2024-01-02 04:00:00.123456"))

        with freeze_time("2024-01-02T05:30:00Z"):
            output = _read(stream_state=first_sync_state)

        assert not output.errors
        assert _event_ids(output) == ["late-arrival", "next-day"]
        assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"server_upload_time": "20240102T04"}

    @HttpMocker()
    def test_given_always_too_large_when_read_then_transient_error_at_one_hour_window(self, http_mocker: HttpMocker) -> None:
        for start, end in [
            ("20240101T00", "20240101T23"),
            ("20240101T00", "20240101T11"),
            ("20240101T00", "20240101T05"),
            ("20240101T00", "20240101T02"),
            ("20240101T00", "20240101T00"),
        ]:
            http_mocker.get(_export_request(start, end), _error_response(400))

        output = _read(expecting_exception=True)

        assert not output.records
        assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"server_upload_time": "20240101T00"}
        # errors[0] is the stream's own error; the last error is the CDK's sync summary, always a config_error.
        assert output.errors[0].trace.error.failure_type == FailureType.transient_error
        assert _FAILURE_MESSAGE in output.errors[0].trace.error.message

    @HttpMocker()
    def test_given_second_half_always_too_large_when_read_then_first_half_emitted_without_checkpoint(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_export_request("20240101T00", "20240101T11"), _export_response(["first-half"], "2024-01-01 05:00:00.123456"))
        for start, end in [
            ("20240101T00", "20240101T23"),
            ("20240101T12", "20240101T23"),
            ("20240101T12", "20240101T17"),
            ("20240101T12", "20240101T14"),
            ("20240101T12", "20240101T12"),
        ]:
            http_mocker.get(_export_request(start, end), _error_response(400))

        output = _read(expecting_exception=True)

        assert _event_ids(output) == ["first-half"]
        assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"server_upload_time": "20240101T00"}
        assert output.errors[0].trace.error.failure_type == FailureType.transient_error

    @HttpMocker()
    def test_given_403_when_read_then_config_error_without_split(self, http_mocker: HttpMocker) -> None:
        request = _export_request("20240101T00", "20240101T23")
        http_mocker.get(request, _error_response(403))

        output = _read(expecting_exception=True)

        http_mocker.assert_number_of_calls(request, 1)
        assert output.errors[0].trace.error.failure_type == FailureType.config_error

    @HttpMocker()
    def test_given_404_when_read_then_ignored_without_split(self, http_mocker: HttpMocker) -> None:
        request = _export_request("20240101T00", "20240101T23")
        http_mocker.get(request, _error_response(404))

        output = _read()

        http_mocker.assert_number_of_calls(request, 1)
        assert not output.errors
        assert not output.records

    @HttpMocker()
    def test_given_404_on_one_half_when_read_then_other_half_read(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(_export_request("20240101T00", "20240101T23"), _error_response(400))
        http_mocker.get(_export_request("20240101T00", "20240101T11"), _error_response(404))
        http_mocker.get(_export_request("20240101T12", "20240101T23"), _export_response(["second-half"], "2024-01-01 20:00:00.123456"))

        output = _read()

        assert not output.errors
        assert _event_ids(output) == ["second-half"]
        assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"server_upload_time": "20240101T20"}

    @HttpMocker()
    def test_given_zero_microsecond_server_upload_time_when_read_then_state_advances_to_it(self, http_mocker: HttpMocker) -> None:
        # TransformDatetimesToRFC3339 drops the ".000000" of a whole-second timestamp: "2024-01-01T05:00:00+00:00".
        http_mocker.get(_export_request("20240101T00", "20240101T23"), _export_response(["whole-second"], "2024-01-01 05:00:00.000000"))

        output = _read()

        assert output.state_messages[-1].state.stream.stream_state.__dict__ == {"server_upload_time": "20240101T05"}
