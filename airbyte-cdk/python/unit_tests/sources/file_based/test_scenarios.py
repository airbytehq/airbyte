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
from airbyte_cdk.models import AirbyteAnalyticsTraceMessage, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from pytest import LogCaptureFixture
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


def verify_read(
    capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario[AbstractSource]
) -> None:
    caplog.handler.setFormatter(AirbyteLogFormatter())
    if scenario.incremental_scenario_config:
        run_test_read_incremental(capsys, caplog, tmp_path, scenario)
    else:
        run_test_read_full_refresh(capsys, caplog, tmp_path, scenario)


def run_test_read_full_refresh(
    capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario[AbstractSource]
) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc) as exc:  # noqa
            read(capsys, caplog, tmp_path, scenario)
        if expected_msg:
            assert expected_msg in get_error_message_from_exc(exc)
    else:
        output = read(capsys, caplog, tmp_path, scenario)
        _verify_read_output(output, scenario)


def run_test_read_incremental(
    capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario[AbstractSource]
) -> None:
    expected_exc, expected_msg = scenario.expected_read_error
    if expected_exc:
        with pytest.raises(expected_exc):
            read_with_state(capsys, caplog, tmp_path, scenario)
    else:
        output = read_with_state(capsys, caplog, tmp_path, scenario)
        _verify_read_output(output, scenario)


def _verify_read_output(output: Dict[str, Any], scenario: TestScenario[AbstractSource]) -> None:
    records, logs = output["records"], output["logs"]
    logs = [log for log in logs if log.get("level") in scenario.log_levels]
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

    if scenario.expected_analytics:
        analytics = output["analytics"]

        _verify_analytics(analytics, scenario.expected_analytics)


def _verify_analytics(analytics: List[Dict[str, Any]], expected_analytics: Optional[List[AirbyteAnalyticsTraceMessage]]) -> None:
    if expected_analytics:
        for actual, expected in zip(analytics, expected_analytics):
            actual_type, actual_value = actual["type"], actual["value"]
            expected_type = expected.type
            expected_value = expected.value
            assert actual_type == expected_type
            assert actual_value == expected_value


def _verify_expected_logs(logs: List[Dict[str, Any]], expected_logs: Optional[List[Mapping[str, Any]]]) -> None:
    if expected_logs:
        for actual, expected in zip(logs, expected_logs):
            actual_level, actual_message = actual["level"], actual["message"]
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
                assert expected_msg.value in output["message"]  # type: ignore
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


def read(
    capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario[AbstractSource]
) -> Dict[str, Any]:
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
            "analytics": [
                msg["trace"]["analytics"]
                for msg in (json.loads(line) for line in captured)
                if msg["type"] == "TRACE" and msg["trace"]["type"] == "ANALYTICS"
            ],
        }


def read_with_state(
    capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario[AbstractSource]
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
