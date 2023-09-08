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
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from freezegun import freeze_time
from pytest import LogCaptureFixture
from unit_tests.sources.file_based.scenarios.avro_scenarios import (
    avro_all_types_scenario,
    avro_file_with_double_as_number_scenario,
    multiple_avro_combine_schema_scenario,
    multiple_streams_avro_scenario,
    single_avro_scenario,
)
from unit_tests.sources.file_based.scenarios.check_scenarios import (
    error_empty_stream_scenario,
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
    csv_autogenerate_column_names_scenario,
    csv_custom_bool_values_scenario,
    csv_custom_delimiter_in_double_quotes_scenario,
    csv_custom_delimiter_with_escape_char_scenario,
    csv_custom_format_scenario,
    csv_custom_null_values_scenario,
    csv_double_quote_is_set_scenario,
    csv_escape_char_is_set_scenario,
    csv_multi_stream_scenario,
    csv_newline_in_values_not_quoted_scenario,
    csv_newline_in_values_quoted_value_scenario,
    csv_single_stream_scenario,
    csv_skip_after_header_scenario,
    csv_skip_before_and_after_header_scenario,
    csv_skip_before_header_scenario,
    csv_string_are_not_null_if_strings_can_be_null_is_false_scenario,
    csv_string_can_be_null_with_input_schemas_scenario,
    csv_string_not_null_if_no_null_values_scenario,
    csv_strings_can_be_null_not_quoted_scenario,
    earlier_csv_scenario,
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
from unit_tests.sources.file_based.scenarios.jsonl_scenarios import (
    invalid_jsonl_scenario,
    jsonl_multi_stream_scenario,
    jsonl_user_input_schema_scenario,
    multi_jsonl_stream_n_bytes_exceeds_limit_for_inference,
    multi_jsonl_stream_n_file_exceeds_limit_for_inference,
    multi_jsonl_with_different_keys_scenario,
    schemaless_jsonl_multi_stream_scenario,
    schemaless_jsonl_scenario,
    single_jsonl_scenario,
)
from unit_tests.sources.file_based.scenarios.parquet_scenarios import (
    multi_parquet_scenario,
    parquet_file_with_decimal_as_float_scenario,
    parquet_file_with_decimal_as_string_scenario,
    parquet_file_with_decimal_no_config_scenario,
    parquet_various_types_scenario,
    parquet_with_invalid_config_scenario,
    single_parquet_scenario,
    single_partitioned_parquet_scenario,
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
    earlier_csv_scenario,
    multi_stream_custom_format,
    empty_schema_inference_scenario,
    single_parquet_scenario,
    multi_parquet_scenario,
    parquet_various_types_scenario,
    parquet_file_with_decimal_no_config_scenario,
    parquet_file_with_decimal_as_string_scenario,
    parquet_file_with_decimal_as_float_scenario,
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
    single_jsonl_scenario,
    multi_jsonl_with_different_keys_scenario,
    multi_jsonl_stream_n_file_exceeds_limit_for_inference,
    multi_jsonl_stream_n_bytes_exceeds_limit_for_inference,
    invalid_jsonl_scenario,
    jsonl_multi_stream_scenario,
    jsonl_user_input_schema_scenario,
    schemaless_jsonl_scenario,
    schemaless_jsonl_multi_stream_scenario,
    csv_string_can_be_null_with_input_schemas_scenario,
    csv_string_are_not_null_if_strings_can_be_null_is_false_scenario,
    csv_string_not_null_if_no_null_values_scenario,
    csv_strings_can_be_null_not_quoted_scenario,
    csv_newline_in_values_quoted_value_scenario,
    csv_escape_char_is_set_scenario,
    csv_double_quote_is_set_scenario,
    csv_custom_delimiter_with_escape_char_scenario,
    csv_custom_delimiter_in_double_quotes_scenario,
    csv_skip_before_header_scenario,
    csv_skip_after_header_scenario,
    csv_skip_before_and_after_header_scenario,
    csv_custom_bool_values_scenario,
    csv_custom_null_values_scenario,
    single_avro_scenario,
    avro_all_types_scenario,
    multiple_avro_combine_schema_scenario,
    multiple_streams_avro_scenario,
    avro_file_with_double_as_number_scenario,
    csv_newline_in_values_not_quoted_scenario,
    csv_autogenerate_column_names_scenario,
    parquet_with_invalid_config_scenario,
    single_partitioned_parquet_scenario,
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
            discover_logs = expected_logs.get("discover")
            logs = [log for log in logs if log.get("log", {}).get("level") in ("ERROR", "WARN")]
            _verify_expected_logs(logs, discover_logs)


read_scenarios = discover_scenarios + [
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
]


@pytest.mark.parametrize("scenario", read_scenarios, ids=[s.name for s in read_scenarios])
@freeze_time("2023-06-09T00:00:00Z")
def test_read(capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario) -> None:
    caplog.handler.setFormatter(AirbyteLogFormatter())
    if scenario.incremental_scenario_config:
        run_test_read_incremental(capsys, caplog, tmp_path, scenario)
    else:
        run_test_read_full_refresh(capsys, caplog, tmp_path, scenario)


def run_test_read_full_refresh(capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc) as exc:  # noqa
            read(capsys, caplog, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    else:
        output = read(capsys, caplog, tmp_path, scenario)
        _verify_read_output(output, scenario)


def run_test_read_incremental(capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc):
            read_with_state(capsys, caplog, tmp_path, scenario)
    else:
        output = read_with_state(capsys, caplog, tmp_path, scenario)
        _verify_read_output(output, scenario)


def _verify_read_output(output: Dict[str, Any], scenario: TestScenario) -> None:
    records, logs = output["records"], output["logs"]
    logs = [log for log in logs if log.get("level") in ("ERROR", "WARN", "WARNING")]
    expected_records = scenario.expected_records
    assert len(records) == len(expected_records)
    for actual, expected in zip(records, expected_records):
        if "record" in actual:
            assert len(actual["record"]["data"]) == len(expected["data"])
            for key, value in actual["record"]["data"].items():
                if isinstance(value, float):
                    assert math.isclose(value, expected["data"][key], abs_tol=1e-04)
                else:
                    assert value == expected["data"][key]
            assert actual["record"]["stream"] == expected["stream"]
        elif "state" in actual:
            assert actual["state"]["data"] == expected

    if scenario.expected_logs:
        read_logs = scenario.expected_logs.get("read")
        assert len(logs) == (len(read_logs) if read_logs else 0)
        _verify_expected_logs(logs, read_logs)


def _verify_expected_logs(logs: List[Dict[str, Any]], expected_logs: Optional[List[Mapping[str, Any]]]) -> None:
    if expected_logs:
        for actual, expected in zip(logs, expected_logs):
            actual_level, actual_message = actual["level"], actual["message"]
            expected_level = expected["level"]
            expected_message = expected["message"]
            assert actual_level == expected_level
            assert expected_message in actual_message


spec_scenarios = [
    single_csv_scenario,
]


@pytest.mark.parametrize("scenario", spec_scenarios, ids=[c.name for c in spec_scenarios])
def test_spec(capsys: CaptureFixture[str], scenario: TestScenario) -> None:
    assert spec(capsys, scenario) == scenario.expected_spec


check_scenarios = [
    error_empty_stream_scenario,
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
    single_avro_scenario,
    earlier_csv_scenario,
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


def spec(capsys: CaptureFixture[str], scenario: TestScenario) -> Mapping[str, Any]:
    launch(
        scenario.source,
        ["spec"],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["spec"]  # type: ignore


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


def read(capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario) -> Dict[str, Any]:
    with caplog.handler.stream as logger_stream:
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
        captured = capsys.readouterr().out.splitlines() + logger_stream.getvalue().split("\n")[:-1]

        return {
            "records": [msg for msg in (json.loads(line) for line in captured) if msg["type"] == "RECORD"],
            "logs": [msg["log"] for msg in (json.loads(line) for line in captured) if msg["type"] == "LOG"],
        }


def read_with_state(
    capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario
) -> Dict[str, List[Any]]:
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
        "records": [msg for msg in (json.loads(line) for line in captured.out.splitlines()) if msg["type"] in ("RECORD", "STATE")],
        "logs": [msg["log"] for msg in (json.loads(line) for line in captured.out.splitlines()) if msg["type"] == "LOG"]
        + [{"level": log.levelname, "message": log.message} for log in logs],
    }


def make_file(path: Path, file_contents: Optional[Union[Mapping[str, Any], List[Mapping[str, Any]]]]) -> str:
    path.write_text(json.dumps(file_contents))
    return str(path)


def get_error_message_from_exc(exc: ExceptionInfo[Any]) -> str:
    if isinstance(exc.value, AirbyteTracedException):
        return exc.value.message
    return str(exc.value.args[0])
