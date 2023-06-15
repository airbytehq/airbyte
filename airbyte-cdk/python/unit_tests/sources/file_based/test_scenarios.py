#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Any, Dict, Union, List

import pytest
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.entrypoint import launch
from unit_tests.sources.file_based.scenarios.csv_scenarios import (
    invalid_csv_scenario,
    single_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
)
from unit_tests.sources.file_based.scenarios.csv_incremental_scenarios import (
    single_csv_input_state_is_earlier_scenario,
    single_csv_no_input_state_scenario,
    single_csv_input_state_is_later_scenario,
    multi_csv_same_timestamp_scenario,
    multi_csv_different_timestamps_scenario
)

scenarios = [
    invalid_csv_scenario,
    single_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
    single_csv_input_state_is_earlier_scenario,
    single_csv_no_input_state_scenario,
    single_csv_input_state_is_later_scenario,
    multi_csv_same_timestamp_scenario,
    multi_csv_different_timestamps_scenario
]


# FIXME: We should test the output of stream_slices

@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
def test_discover(capsys, tmp_path, json_spec, scenario):
    if scenario.expected_discover_error:
        with pytest.raises(scenario.expected_discover_error):
            discover(capsys, tmp_path, scenario)
    else:
        assert discover(capsys, tmp_path, scenario) == scenario.expected_catalog


@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
def test_read(capsys, tmp_path, json_spec, scenario):
    if scenario.incremental_scenario_config:
        return
    if scenario.expected_read_error:
        with pytest.raises(scenario.expected_read_error):
            read(capsys, tmp_path, scenario)
    else:
        output = read(capsys, tmp_path, scenario)
        expected_output = scenario.expected_records
        assert len(output) == len(expected_output)
        for actual, expected in zip(output, expected_output):
            assert actual["record"]["data"] == expected


@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
def test_read_incremental(capsys, tmp_path, json_spec, scenario):
    if scenario.incremental_scenario_config:
        if scenario.expected_read_error:
            with pytest.raises(scenario.expected_read_error):
                read_with_state(capsys, tmp_path, scenario)
        else:
            output = read_with_state(capsys, tmp_path, scenario)
            expected_output = scenario.expected_records
            assert len(output) == len(expected_output)
            for actual, expected in zip(output, expected_output):
                if "record" in actual:
                    print(f"actual_record: {actual}")
                    assert actual["record"]["data"] == expected
                elif "state" in actual:
                    print(f"actual_state: {actual}")
                    assert actual["state"]["data"] == expected


def discover(capsys, tmp_path, scenario) -> Dict[str, Any]:
    launch(
        scenario.source,
        ["discover", "--config", make_file(tmp_path / "config.json", scenario.config)],
    )
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["catalog"]


def read(capsys, tmp_path, scenario, types_to_keep = set(["RECORD"])):
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
        if msg["type"] in types_to_keep
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
            "--debug"
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
