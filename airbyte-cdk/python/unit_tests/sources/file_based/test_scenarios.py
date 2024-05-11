#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import math
from pathlib import Path, PosixPath
from typing import Any, Dict, List, Mapping, Optional, Union

import pytest
from _pytest.capture import CaptureFixture
from _pytest.reports import ExceptionInfo
from airbyte_cdk.entrypoint import launch
from airbyte_cdk.models import AirbyteAnalyticsTraceMessage, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.file_based.stream.concurrent.cursor import AbstractConcurrentFileBasedCursor
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.utils import message_utils
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import AirbyteLogMessage, AirbyteMessage, ConfiguredAirbyteCatalog
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenario


def verify_discover(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario[AbstractSource]) -> None:
    expected_exc, expected_msg = scenario.expected_discover_error
    expected_logs = scenario.expected_logs
    if expected_exc:
        with pytest.raises(expected_exc) as exc:
            discover(capsys, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    elif scenario.expected_catalog:
        output = discover(capsys, tmp_path, scenario)
        catalog, logs = output["catalog"], output["logs"]
        assert catalog == scenario.expected_catalog
        if expected_logs:
            discover_logs = expected_logs.get("discover")
            logs = [log for log in logs if log.get("log", {}).get("level") in ("ERROR", "WARN")]
            _verify_expected_logs(logs, discover_logs)


def verify_read(scenario: TestScenario[AbstractSource]) -> None:
    if scenario.incremental_scenario_config:
        run_test_read_incremental(scenario)
    else:
        run_test_read_full_refresh(scenario)


def run_test_read_full_refresh(scenario: TestScenario[AbstractSource]) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    output = read(scenario)
    if expected_exc:
        assert_exception(expected_exc, output)
        if expected_msg:
            assert expected_msg in output.errors[-1].trace.error.internal_message
    else:
        _verify_read_output(output, scenario)


def run_test_read_incremental(scenario: TestScenario[AbstractSource]) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    output = read_with_state(scenario)
    if expected_exc:
        assert_exception(expected_exc, output)
    else:
        _verify_read_output(output, scenario)


def assert_exception(expected_exception: type[BaseException], output: EntrypointOutput) -> None:
    assert expected_exception.__name__ in output.errors[-1].trace.error.stack_trace


def _verify_read_output(output: EntrypointOutput, scenario: TestScenario[AbstractSource]) -> None:
    records_and_state_messages, log_messages = output.records_and_state_messages, output.logs
    logs = [message.log for message in log_messages if message.log.level.value in scenario.log_levels]
    if scenario.expected_records is None:
        return

    expected_records = [r for r in scenario.expected_records] if scenario.expected_records else []

    sorted_expected_records = sorted(
        filter(lambda e: "data" in e, expected_records),
        key=lambda record: ",".join(
            f"{k}={v}" for k, v in sorted(record["data"].items(), key=lambda items: (items[0], items[1])) if k != "emitted_at"
        ),
    )
    sorted_records = sorted(
        filter(lambda r: r.record, records_and_state_messages),
        key=lambda record: ",".join(
            f"{k}={v}" for k, v in sorted(record.record.data.items(), key=lambda items: (items[0], items[1])) if k != "emitted_at"
        ),
    )

    assert len(sorted_records) == len(sorted_expected_records)

    for actual, expected in zip(sorted_records, sorted_expected_records):
        if actual.record:
            assert len(actual.record.data) == len(expected["data"])
            for key, value in actual.record.data.items():
                if isinstance(value, float):
                    assert math.isclose(value, expected["data"][key], abs_tol=1e-04)
                else:
                    assert value == expected["data"][key]
            assert actual.record.stream == expected["stream"]

    expected_states = list(filter(lambda e: "data" not in e, expected_records))
    states = list(filter(lambda r: r.state, records_and_state_messages))
    assert len(states) > 0, "No state messages emitted. Successful syncs should emit at least one stream state."
    _verify_state_record_counts(sorted_records, states)

    if hasattr(scenario.source, "cursor_cls") and issubclass(scenario.source.cursor_cls, AbstractConcurrentFileBasedCursor):
        # Only check the last state emitted because we don't know the order the others will be in.
        # This may be needed for non-file-based concurrent scenarios too.
        assert states[-1].state.stream.stream_state.dict() == expected_states[-1]
    else:
        for actual, expected in zip(states, expected_states):  # states should be emitted in sorted order
            assert actual.state.stream.stream_state.dict() == expected

    if scenario.expected_logs:
        read_logs = scenario.expected_logs.get("read")
        assert len(logs) == (len(read_logs) if read_logs else 0)
        _verify_expected_logs(logs, read_logs)

    if scenario.expected_analytics:
        analytics = output.analytics_messages

        _verify_analytics(analytics, scenario.expected_analytics)


def _verify_state_record_counts(records: List[AirbyteMessage], states: List[AirbyteMessage]) -> None:
    actual_record_counts = {}
    for record in records:
        stream_descriptor = message_utils.get_stream_descriptor(record)
        actual_record_counts[stream_descriptor] = actual_record_counts.get(stream_descriptor, 0) + 1

    state_record_count_sums = {}
    for state_message in states:
        stream_descriptor = message_utils.get_stream_descriptor(state_message)
        state_record_count_sums[stream_descriptor] = (
            state_record_count_sums.get(stream_descriptor, 0)
            + state_message.state.sourceStats.recordCount
        )

    for stream, actual_count in actual_record_counts.items():
        assert actual_count == state_record_count_sums.get(stream)

    # We can have extra keys in state_record_count_sums if we processed a stream and reported 0 records
    extra_keys = state_record_count_sums.keys() - actual_record_counts.keys()
    for stream in extra_keys:
        assert state_record_count_sums[stream] == 0


def _verify_analytics(analytics: List[AirbyteMessage], expected_analytics: Optional[List[AirbyteAnalyticsTraceMessage]]) -> None:
    if expected_analytics:
        assert len(analytics) == len(
            expected_analytics), \
            f"Number of actual analytics messages ({len(analytics)}) did not match expected ({len(expected_analytics)})"
        for actual, expected in zip(analytics, expected_analytics):
            actual_type, actual_value = actual.trace.analytics.type, actual.trace.analytics.value
            expected_type = expected.type
            expected_value = expected.value
            assert actual_type == expected_type
            assert actual_value == expected_value


def _verify_expected_logs(logs: List[AirbyteLogMessage], expected_logs: Optional[List[Mapping[str, Any]]]) -> None:
    if expected_logs:
        for actual, expected in zip(logs, expected_logs):
            actual_level, actual_message = actual.level.value, actual.message
            expected_level = expected["level"]
            expected_message = expected["message"]
            assert actual_level == expected_level
            assert expected_message in actual_message


def verify_spec(capsys: CaptureFixture[str], scenario: TestScenario[AbstractSource]) -> None:
    assert spec(capsys, scenario) == scenario.expected_spec


def verify_check(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario[AbstractSource]) -> None:
    expected_exc, expected_msg = scenario.expected_check_error

    if expected_exc:
        with pytest.raises(expected_exc):
            output = check(capsys, tmp_path, scenario)
            if expected_msg:
                # expected_msg is a string. what's the expected value field?
                assert expected_msg in output["message"]  # type: ignore
                assert output["status"] == scenario.expected_check_status

    else:
        output = check(capsys, tmp_path, scenario)
        assert output["status"] == scenario.expected_check_status


def spec(capsys: CaptureFixture[str], scenario: TestScenario[AbstractSource]) -> Mapping[str, Any]:
    launch(
        scenario.source,
        ["spec"],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["spec"]  # type: ignore


def check(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario[AbstractSource]) -> Dict[str, Any]:
    launch(
        scenario.source,
        ["check", "--config", make_file(tmp_path / "config.json", scenario.config)],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["connectionStatus"]  # type: ignore


def discover(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario[AbstractSource]) -> Dict[str, Any]:
    launch(
        scenario.source,
        ["discover", "--config", make_file(tmp_path / "config.json", scenario.config)],
    )
    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    [catalog] = [o["catalog"] for o in output if o.get("catalog")]  # type: ignore
    return {
        "catalog": catalog,
        "logs": [o["log"] for o in output if o.get("log")],
    }


def read(scenario: TestScenario[AbstractSource]) -> EntrypointOutput:
    return entrypoint_read(
        scenario.source,
        scenario.config,
        ConfiguredAirbyteCatalog.parse_obj(scenario.configured_catalog(SyncMode.full_refresh)),
    )


def read_with_state(scenario: TestScenario[AbstractSource]) -> EntrypointOutput:
    return entrypoint_read(
        scenario.source,
        scenario.config,
        ConfiguredAirbyteCatalog.parse_obj(scenario.configured_catalog(SyncMode.incremental)),
        scenario.input_state(),
    )


def make_file(path: Path, file_contents: Optional[Union[Mapping[str, Any], List[Mapping[str, Any]]]]) -> str:
    path.write_text(json.dumps(file_contents))
    return str(path)


def get_error_message_from_exc(exc: ExceptionInfo[Any]) -> str:
    if isinstance(exc.value, AirbyteTracedException):
        return exc.value.message
    return str(exc.value.args[0])
