#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pytest
from airbyte_cdk.entrypoint import launch
from airbyte_cdk.models.airbyte_protocol import SyncMode
from freezegun import freeze_time
from unit_tests.sources.file_based.scenarios.csv_scenarios import (
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
    invalid_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
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

scenarios = [
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
]


@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
def test_discover(capsys, tmp_path, json_spec, scenario):
    if scenario.expected_discover_error:
        with pytest.raises(scenario.expected_discover_error):
            discover(capsys, tmp_path, scenario)
    else:
        assert discover(capsys, tmp_path, scenario) == scenario.expected_catalog


@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
@freeze_time("2023-06-09T00:00:00Z")
def test_read(capsys, tmp_path, json_spec, scenario):
    if scenario.incremental_scenario_config:
        run_test_read_incremental(capsys, tmp_path, scenario)
    else:
        run_test_read_full_refresh(capsys, tmp_path, scenario)


def run_test_read_full_refresh(capsys, tmp_path, scenario):
    if scenario.expected_read_error:
        with pytest.raises(scenario.expected_read_error):
            read(capsys, tmp_path, scenario)
    else:
        output = read(capsys, tmp_path, scenario)
        expected_output = scenario.expected_records
        assert len(output) == len(expected_output)
        for actual, expected in zip(output, expected_output):
            assert actual["record"]["data"] == expected["data"]
            assert actual["record"]["stream"] == expected["stream"]


def run_test_read_incremental(capsys, tmp_path, scenario):
    if scenario.expected_read_error:
        with pytest.raises(scenario.expected_read_error):
            read_with_state(capsys, tmp_path, scenario)
    else:
        output = read_with_state(capsys, tmp_path, scenario)
        expected_output = scenario.expected_records
        assert len(output) == len(expected_output)
        for actual, expected in zip(output, expected_output):
            if "record" in actual:
                assert actual["record"]["data"] == expected
            elif "state" in actual:
                assert actual["state"]["data"] == expected


def discover(capsys, tmp_path, scenario) -> Dict[str, Any]:
    launch(
        scenario.source,
        ["discover", "--config", make_file(tmp_path / "config.json", scenario.config)],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["catalog"]


def read(capsys, tmp_path, scenario):
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
    captured = capsys.readouterr()
    return [
        msg
        for msg in (json.loads(line) for line in captured.out.splitlines())
        if msg["type"] == "RECORD"
    ]


def read_with_state(capsys, tmp_path, scenario):
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
    return [
        msg
        for msg in (json.loads(line) for line in captured.out.splitlines())
        if msg["type"] in ("RECORD", "STATE")
    ]


def make_file(path: Path, file_contents: Union[Dict, List]) -> str:
    path.write_text(json.dumps(file_contents))
    return str(path)
