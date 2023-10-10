#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from pathlib import PosixPath

import pytest
from _pytest.capture import CaptureFixture
from freezegun import freeze_time
from pytest import LogCaptureFixture
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenario
from unit_tests.sources.file_based.test_scenarios import verify_discover, verify_read
from unit_tests.sources.streams.concurrent.scenarios.thread_based_concurrent_stream_scenarios import (
    test_concurrent_cdk_multiple_streams,
    test_concurrent_cdk_single_stream,
)

scenarios = [
    test_concurrent_cdk_single_stream,
    test_concurrent_cdk_multiple_streams,
]


@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
@freeze_time("2023-06-09T00:00:00Z")
def test_concurrent_read(capsys: CaptureFixture[str], caplog: LogCaptureFixture, tmp_path: PosixPath, scenario: TestScenario) -> None:
    verify_read(capsys, caplog, tmp_path, scenario)


@pytest.mark.parametrize("scenario", scenarios, ids=[s.name for s in scenarios])
def test_concurrent_discover(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario) -> None:
    verify_discover(capsys, tmp_path, scenario)
