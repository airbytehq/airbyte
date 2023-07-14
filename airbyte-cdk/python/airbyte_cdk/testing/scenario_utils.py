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

from airbyte_cdk.testing.scenario_builder import TestScenario


def test_discover(capsys: CaptureFixture[str], tmp_path: PosixPath, json_spec: Mapping[str, Any], scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_discover_error
    if expected_exc:
        with pytest.raises(expected_exc) as exc:
            discover(capsys, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    else:
        assert discover(capsys, tmp_path, scenario) == scenario.expected_catalog



def test_read(capsys: CaptureFixture[str], tmp_path: PosixPath, json_spec: Mapping[str, Any], scenario: TestScenario) -> None:
    if scenario.incremental_scenario_config:
        run_test_read_incremental(capsys, tmp_path, scenario)
    else:
        run_test_read_full_refresh(capsys, tmp_path, scenario)


def run_test_read_full_refresh(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    expected_records = scenario.expected_records
    expected_logs = scenario.expected_logs
    if expected_exc:
        with pytest.raises(expected_exc) as exc:  # noqa
            read(capsys, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    else:
        output = read(capsys, tmp_path, scenario)
        records, logs = output["records"], output["logs"]
        assert len(records) == len(expected_records)
        assert len(logs) == len(expected_logs)
        assert_expected_records_match_output(records, expected_records)
        assert_expected_logs_match_output(logs, expected_logs)


def assert_expected_records_match_output(output: List[Mapping[str, Any]], expected_output: List[Mapping[str, Any]]) -> None:
    mismatch = []
    for actual, expected in zip(output, expected_output):
        for key, value in actual["record"]["data"].items():
            if isinstance(value, float):
                assert math.isclose(value, expected["data"][key], abs_tol=1e-06)
            else:
                assert value == expected["data"][key]

        assert actual["record"]["stream"] == expected["stream"]


def assert_expected_logs_match_output(logs: List[Mapping[str, Any]], expected_logs: List[Mapping[str, Any]]) -> None:
    for actual, expected in zip(logs, expected_logs):
        assert actual["log"]["level"] == expected["level"]
        assert actual["log"]["message"] == expected["message"]


def run_test_read_incremental(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc):
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


def test_check(capsys: CaptureFixture[str], tmp_path: PosixPath, json_spec: Mapping[str, Any], scenario: TestScenario) -> None:
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
    captured = capsys.readouterr()
    return json.loads(captured.out.splitlines()[0])["catalog"]  # type: ignore


def read(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> Dict[str, Any]:
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
    return {
        "records": [
            msg
            for msg in (json.loads(line) for line in captured)
            if msg["type"] == "RECORD"
        ],
        "logs": [
            msg
            for msg in (json.loads(line) for line in captured)
            if msg["type"] == "LOG"
        ]
    }


def read_with_state(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> List[Dict[str, Any]]:
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


def make_file(path: Path, file_contents: Optional[Union[Mapping[str, Any], List[Mapping[str, Any]]]]) -> str:
    path.write_text(json.dumps(file_contents))
    return str(path)


def get_error_message_from_exc(exc: ExceptionInfo[Any]) -> str:
    return str(exc.value.args[0])
