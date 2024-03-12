# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import logging
import os
from typing import Any, Iterator, List, Mapping
from unittest import TestCase
from unittest.mock import Mock, patch

from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import (
    AirbyteAnalyticsTraceMessage,
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStreamState,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    Level,
    StreamDescriptor,
    TraceType,
    Type,
)


def _a_state_message(stream_name: str, stream_state: Mapping[str, Any]) -> AirbyteMessage:
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream_name), stream_state=AirbyteStateBlob(**stream_state))))


def _a_status_message(stream_name: str, status: AirbyteStreamStatus) -> AirbyteMessage:
    return AirbyteMessage(
        type=Type.TRACE,
        trace=AirbyteTraceMessage(
            type=TraceType.STREAM_STATUS,
            emitted_at=0,
            stream_status=AirbyteStreamStatusTraceMessage(
                stream_descriptor=StreamDescriptor(name=stream_name),
                status=status,
            ),
        ),
    )


_A_RECORD = AirbyteMessage(
    type=Type.RECORD, record=AirbyteRecordMessage(stream="stream", data={"record key": "record value"}, emitted_at=0)
)
_A_STATE_MESSAGE = _a_state_message("stream_name", {"state key": "state value for _A_STATE_MESSAGE"})
_A_LOG = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="This is an Airbyte log message"))
_AN_ERROR_MESSAGE = AirbyteMessage(
    type=Type.TRACE,
    trace=AirbyteTraceMessage(
        type=TraceType.ERROR,
        emitted_at=0,
        error=AirbyteErrorTraceMessage(message="AirbyteErrorTraceMessage message"),
    ),
)
_AN_ANALYTIC_MESSAGE = AirbyteMessage(
    type=Type.TRACE,
    trace=AirbyteTraceMessage(
        type=TraceType.ANALYTICS,
        emitted_at=0,
        analytics=AirbyteAnalyticsTraceMessage(type="an analytic type", value="an analytic value"),
    ),
)

_A_STREAM_NAME = "a stream name"
_A_CONFIG = {"config_key": "config_value"}
_A_CATALOG = ConfiguredAirbyteCatalog.parse_obj(
    {
        "streams": [
            {
                "stream": {
                    "name": "a_stream_name",
                    "json_schema": {},
                    "supported_sync_modes": ["full_refresh"],
                },
                "sync_mode": "full_refresh",
                "destination_sync_mode": "append",
            }
        ]
    }
)
_A_STATE = StateBuilder().with_stream_state(_A_STREAM_NAME, {"state_key": "state_value"}).build()
_A_LOG_MESSAGE = "a log message"


def _to_entrypoint_output(messages: List[AirbyteMessage]) -> Iterator[str]:
    return (message.json(exclude_unset=True) for message in messages)


def _a_mocked_source() -> AbstractSource:
    source = Mock(spec=AbstractSource)
    source.message_repository = None
    return source


def _validate_tmp_json_file(expected, file_path) -> None:
    with open(file_path) as file:
        assert json.load(file) == expected


def _validate_tmp_catalog(expected, file_path) -> None:
    assert ConfiguredAirbyteCatalog.parse_file(file_path) == expected


def _create_tmp_file_validation(entrypoint, expected_config, expected_catalog, expected_state):
    def _validate_tmp_files(self):
        _validate_tmp_json_file(expected_config, entrypoint.return_value.parse_args.call_args.args[0][2])
        _validate_tmp_catalog(expected_catalog, entrypoint.return_value.parse_args.call_args.args[0][4])
        _validate_tmp_json_file(expected_state, entrypoint.return_value.parse_args.call_args.args[0][6])
        return entrypoint.return_value.run.return_value

    return _validate_tmp_files


class EntrypointWrapperTest(TestCase):
    def setUp(self) -> None:
        self._a_source = _a_mocked_source()

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_when_read_then_ensure_parameters(self, entrypoint):
        entrypoint.return_value.run.side_effect = _create_tmp_file_validation(entrypoint, _A_CONFIG, _A_CATALOG, _A_STATE)

        read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)

        entrypoint.assert_called_once_with(self._a_source)
        entrypoint.return_value.run.assert_called_once_with(entrypoint.return_value.parse_args.return_value)
        assert entrypoint.return_value.parse_args.call_count == 1
        assert entrypoint.return_value.parse_args.call_args.args[0][0] == "read"
        assert entrypoint.return_value.parse_args.call_args.args[0][1] == "--config"
        assert entrypoint.return_value.parse_args.call_args.args[0][3] == "--catalog"

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_when_read_then_ensure_files_are_temporary(self, entrypoint):
        read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)

        assert not os.path.exists(entrypoint.return_value.parse_args.call_args.args[0][2])
        assert not os.path.exists(entrypoint.return_value.parse_args.call_args.args[0][4])
        assert not os.path.exists(entrypoint.return_value.parse_args.call_args.args[0][6])

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_logging_during_run_when_read_then_output_has_logs(self, entrypoint):
        def _do_some_logging(self):
            logging.getLogger("any logger").info(_A_LOG_MESSAGE)
            return entrypoint.return_value.run.return_value

        entrypoint.return_value.run.side_effect = _do_some_logging

        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)

        assert len(output.logs) == 1
        assert output.logs[0].log.message == _A_LOG_MESSAGE

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_record_when_read_then_output_has_record(self, entrypoint):
        entrypoint.return_value.run.return_value = _to_entrypoint_output([_A_RECORD])
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.records == [_A_RECORD]

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_state_message_when_read_then_output_has_state_message(self, entrypoint):
        entrypoint.return_value.run.return_value = _to_entrypoint_output([_A_STATE_MESSAGE])
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.state_messages == [_A_STATE_MESSAGE]

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_state_message_and_records_when_read_then_output_has_records_and_state_message(self, entrypoint):
        entrypoint.return_value.run.return_value = _to_entrypoint_output([_A_RECORD, _A_STATE_MESSAGE])
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.records_and_state_messages == [_A_RECORD, _A_STATE_MESSAGE]

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_many_state_messages_and_records_when_read_then_output_has_records_and_state_message(self, entrypoint):
        state_value = {"state_key": "last state value"}
        last_emitted_state = AirbyteStreamState(stream_descriptor=StreamDescriptor(name="stream_name"), stream_state=AirbyteStateBlob(**state_value))
        entrypoint.return_value.run.return_value = _to_entrypoint_output([_A_STATE_MESSAGE, _a_state_message("stream_name", state_value)])

        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)

        assert output.most_recent_state == last_emitted_state

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_log_when_read_then_output_has_log(self, entrypoint):
        entrypoint.return_value.run.return_value = _to_entrypoint_output([_A_LOG])
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.logs == [_A_LOG]

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_trace_message_when_read_then_output_has_trace_messages(self, entrypoint):
        entrypoint.return_value.run.return_value = _to_entrypoint_output([_AN_ANALYTIC_MESSAGE])
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.analytics_messages == [_AN_ANALYTIC_MESSAGE]

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_stream_statuses_when_read_then_return_statuses(self, entrypoint):
        status_messages = [
            _a_status_message(_A_STREAM_NAME, AirbyteStreamStatus.STARTED),
            _a_status_message(_A_STREAM_NAME, AirbyteStreamStatus.COMPLETE),
        ]
        entrypoint.return_value.run.return_value = _to_entrypoint_output(status_messages)
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.get_stream_statuses(_A_STREAM_NAME) == [AirbyteStreamStatus.STARTED, AirbyteStreamStatus.COMPLETE]

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_stream_statuses_for_many_streams_when_read_then_filter_other_streams(self, entrypoint):
        status_messages = [
            _a_status_message(_A_STREAM_NAME, AirbyteStreamStatus.STARTED),
            _a_status_message("another stream name", AirbyteStreamStatus.INCOMPLETE),
            _a_status_message(_A_STREAM_NAME, AirbyteStreamStatus.COMPLETE),
        ]
        entrypoint.return_value.run.return_value = _to_entrypoint_output(status_messages)
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert len(output.get_stream_statuses(_A_STREAM_NAME)) == 2

    @patch("airbyte_cdk.test.entrypoint_wrapper.print", create=True)
    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_unexpected_exception_when_read_then_print(self, entrypoint, print_mock):
        entrypoint.return_value.run.side_effect = ValueError("This error should be printed")
        read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert print_mock.call_count > 0

    @patch("airbyte_cdk.test.entrypoint_wrapper.print", create=True)
    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_expected_exception_when_read_then_do_not_print(self, entrypoint, print_mock):
        entrypoint.return_value.run.side_effect = ValueError("This error should be printed")
        read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE, expecting_exception=True)
        assert print_mock.call_count == 0

    @patch("airbyte_cdk.test.entrypoint_wrapper.AirbyteEntrypoint")
    def test_given_uncaught_exception_when_read_then_output_has_error(self, entrypoint):
        entrypoint.return_value.run.side_effect = ValueError("This error should be printed")
        output = read(self._a_source, _A_CONFIG, _A_CATALOG, _A_STATE)
        assert output.errors
