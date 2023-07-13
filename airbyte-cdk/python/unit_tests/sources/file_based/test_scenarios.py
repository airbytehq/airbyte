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
from airbyte_cdk.models import SyncMode
from freezegun import freeze_time
from unit_tests.sources.file_based.scenarios.check_scenarios import (
    error_empty_stream_scenario,
    error_extension_mismatch_scenario,
    error_listing_files_scenario,
    error_multi_stream_scenario,
    error_reading_file_scenario,
    error_record_validation_user_provided_schema_scenario,
    success_csv_scenario,
    success_extensionless_scenario,
    success_multi_stream_scenario,
    success_user_provided_schema_scenario,
)
from unit_tests.sources.file_based.scenarios.csv_scenarios import (
    csv_custom_format_scenario,
    csv_legacy_format_scenario,
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
    empty_schema_inference_scenario,
    invalid_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
    multi_stream_custom_format,
    schemaless_csv_multi_stream_scenario,
    schemaless_csv_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
    single_csv_scenario,
)
from unit_tests.sources.file_based.scenarios.incremental_scenarios import (
    multi_csv_different_timestamps_scenario,
    multi_csv_include_missing_files_within_history_range,
    multi_csv_per_timestamp_scenario,
    multi_csv_remove_old_files_if_history_is_full_scenario,
    multi_csv_same_timestamp_more_files_than_history_size_scenario,
    multi_csv_same_timestamp_scenario,
    multi_csv_skip_file_if_already_in_history,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario,
    single_csv_file_is_skipped_if_same_modified_at_as_in_history,
    single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history,
    single_csv_input_state_is_earlier_scenario,
    single_csv_input_state_is_later_scenario,
    single_csv_no_input_state_scenario,
)
from unit_tests.sources.file_based.scenarios.parquet_scenarios import (
    multi_parquet_scenario,
    parquet_various_types_scenario,
    single_parquet_scenario,
)
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenario
from unit_tests.sources.file_based.scenarios.user_input_schema_scenarios import (
    multi_stream_user_input_schema_scenario_emit_nonconforming_records,
    multi_stream_user_input_schema_scenario_schema_is_invalid,
    multi_stream_user_input_schema_scenario_skip_nonconforming_records,
    single_stream_user_input_schema_scenario_emit_nonconforming_records,
    single_stream_user_input_schema_scenario_schema_is_invalid,
    single_stream_user_input_schema_scenario_skip_nonconforming_records,
    valid_multi_stream_user_input_schema_scenario,
    valid_single_stream_user_input_schema_scenario,
)
from unit_tests.sources.file_based.scenarios.validation_policy_scenarios import (
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    invalid_validation_policy,
    no_validation_policy,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
)

discover_scenarios = [
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
    invalid_csv_scenario,
    single_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
    single_csv_input_state_is_earlier_scenario,
    single_csv_no_input_state_scenario,
    single_csv_input_state_is_later_scenario,
    multi_csv_same_timestamp_scenario,
    multi_csv_different_timestamps_scenario,
    multi_csv_per_timestamp_scenario,
    multi_csv_skip_file_if_already_in_history,
    multi_csv_include_missing_files_within_history_range,
    multi_csv_remove_old_files_if_history_is_full_scenario,
    multi_csv_same_timestamp_more_files_than_history_size_scenario,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario,
    single_csv_file_is_skipped_if_same_modified_at_as_in_history,
    single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history,
    csv_custom_format_scenario,
    csv_legacy_format_scenario,
    multi_stream_custom_format,
    empty_schema_inference_scenario,
    single_parquet_scenario,
    multi_parquet_scenario,
    parquet_various_types_scenario,
    schemaless_csv_scenario,
    schemaless_csv_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
    single_stream_user_input_schema_scenario_schema_is_invalid,
    single_stream_user_input_schema_scenario_emit_nonconforming_records,
    single_stream_user_input_schema_scenario_skip_nonconforming_records,
    multi_stream_user_input_schema_scenario_emit_nonconforming_records,
    multi_stream_user_input_schema_scenario_skip_nonconforming_records,
    multi_stream_user_input_schema_scenario_schema_is_invalid,
    valid_multi_stream_user_input_schema_scenario,
    valid_single_stream_user_input_schema_scenario,
]


@pytest.mark.parametrize("scenario", discover_scenarios, ids=[s.name for s in discover_scenarios])
def test_discover(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_discover_error
    expected_logs = scenario.expected_logs
    if expected_exc:
        with pytest.raises(expected_exc) as exc:
            discover(capsys, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    else:
        output = discover(capsys, tmp_path, scenario)
        catalog, logs = output["catalog"], output["logs"]
        assert catalog == scenario.expected_catalog
        if expected_logs:
            expected_logs = expected_logs.get("discover", [])
            logs = [log for log in logs if log.get("log", {}).get("level") in ("ERROR", "WARN")]
            _verify_expected_logs(logs, expected_logs)


read_scenarios = discover_scenarios + [
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    invalid_validation_policy,
    no_validation_policy,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
]


@pytest.mark.parametrize("scenario", read_scenarios, ids=[s.name for s in read_scenarios])
@freeze_time("2023-06-09T00:00:00Z")
def test_read(capsys: CaptureFixture[str], caplog: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario):
    if scenario.incremental_scenario_config:
        run_test_read_incremental(capsys, caplog, tmp_path, scenario)
    else:
        run_test_read_full_refresh(capsys, caplog, tmp_path, scenario)


def run_test_read_full_refresh(capsys: CaptureFixture[str], caplog: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc) as exc:  # noqa
            read(capsys, caplog, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    else:
        output = read(capsys, caplog, tmp_path, scenario)
        _verify_read_output(output, scenario)


def run_test_read_incremental(capsys: CaptureFixture[str], caplog: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc):
            read_with_state(capsys, caplog, tmp_path, scenario)
    else:
        output = read_with_state(capsys, caplog, tmp_path, scenario)
        _verify_read_output(output, scenario)


def _verify_read_output(output, scenario):
    records, logs = output["records"], output["logs"]
    logs = [log for log in logs if log.get("level") in ("ERROR", "WARN", "WARNING")]
    expected_records = scenario.expected_records
    assert len(records) == len(expected_records)
    for actual, expected in zip(records, expected_records):
        if "record" in actual:
            for key, value in actual["record"]["data"].items():
                if isinstance(value, float):
                    assert math.isclose(value, expected["data"][key], abs_tol=1e-06)
                else:
                    assert value == expected["data"][key]
            assert actual["record"]["stream"] == expected["stream"]
        elif "state" in actual:
            assert actual["state"]["data"] == expected

    if scenario.expected_logs:
        expected_logs = scenario.expected_logs.get("read", [])
        assert len(logs) == len(expected_logs)
        _verify_expected_logs(logs, expected_logs)


def _verify_expected_logs(logs: List[Dict[str, Any]], expected_logs: List[Dict[str, Any]]):
    for actual, expected in zip(logs, expected_logs):
        actual_level, actual_message = actual["level"], actual["message"]
        expected_level, expected_message = expected["level"], expected["message"]
        assert actual_level == expected_level
        assert expected_message in actual_message


spec_scenarios = [
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
]


@pytest.mark.parametrize("scenario", spec_scenarios, ids=[c.name for c in spec_scenarios])
def test_spec(capsys, scenario):
    assert spec(capsys, scenario) == single_csv_scenario.expected_spec


check_scenarios = [
    error_empty_stream_scenario,
    error_extension_mismatch_scenario,
    error_listing_files_scenario,
    error_reading_file_scenario,
    error_record_validation_user_provided_schema_scenario,
    error_multi_stream_scenario,
    success_csv_scenario,
    success_extensionless_scenario,
    success_multi_stream_scenario,
    success_user_provided_schema_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
    valid_single_stream_user_input_schema_scenario,
]


@pytest.mark.parametrize("scenario", check_scenarios, ids=[c.name for c in check_scenarios])
def test_check(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_check_error

    if expected_exc:
        with pytest.raises(expected_exc):
            output = check(capsys, tmp_path, scenario)
            if expected_msg:
                # expected_msg is a string. what's the expected value field?
                assert expected_msg.value in output["message"]  # type: ignore
                assert output["status"] == scenario.expected_check_status

    else:
        output = check(capsys, tmp_path, scenario)
        assert output["status"] == scenario.expected_check_status


def spec(capsys, scenario):
    launch(
        scenario.source,
        ["spec"],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["spec"]


def check(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> Dict[str, Any]:
    launch(
        scenario.source,
        ["check", "--config", make_file(tmp_path / "config.json", scenario.config)],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["connectionStatus"]  # type: ignore


def discover(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> Dict[str, Any]:
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


def read(capsys: CaptureFixture[str], caplog: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> Dict[str, Any]:
    launch(
        scenario.source,
        [
            "read",
            "--config",
            make_file(tmp_path / "config.json", scenario.config),
            "--catalog",
            make_file(tmp_path / "catalog.json", scenario.configured_catalog(SyncMode.full_refresh)),
        ],
    )
    captured = capsys.readouterr().out.splitlines()
    logs = caplog.records
    return {
        "records": [
            msg
            for msg in (json.loads(line) for line in captured)
            if msg["type"] == "RECORD"
        ],
        "logs": [
            msg["log"]
            for msg in (json.loads(line) for line in captured)
            if msg["type"] == "LOG"
        ] + [{"level": log.levelname, "message": log.message} for log in logs]
    }


def read_with_state(capsys: CaptureFixture[str], caplog: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> Dict[str, List[Any]]:
    launch(
        scenario.source,
        [
            "read",
            "--config",
            make_file(tmp_path / "config.json", scenario.config),
            "--catalog",
            make_file(tmp_path / "catalog.json", scenario.configured_catalog(SyncMode.incremental)),
            "--state",
            make_file(tmp_path / "state.json", scenario.input_state()),
        ],
    )
    captured = capsys.readouterr()
    logs = caplog.records
    return {
        "records": [
            msg
            for msg in (json.loads(line) for line in captured.out.splitlines())
            if msg["type"] in ("RECORD", "STATE")
        ],
        "logs": [
            msg["log"]
            for msg in (json.loads(line) for line in captured.out.splitlines())
            if msg["type"] == "LOG"
        ] + [{"level": log.levelname, "message": log.message} for log in logs]
    }


def make_file(path: Path, file_contents: Optional[Union[Mapping[str, Any], List[Mapping[str, Any]]]]) -> str:
    path.write_text(json.dumps(file_contents))
    return str(path)


def get_error_message_from_exc(exc: ExceptionInfo[Any]) -> str:
    return str(exc.value.args[0])
