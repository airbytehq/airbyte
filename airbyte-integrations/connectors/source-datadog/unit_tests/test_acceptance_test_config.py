# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml


UNIT_TESTS = Path(__file__).parent
ACCEPTANCE_TEST_CONFIG = UNIT_TESTS.parent / "acceptance-test-config.yml"


def test_every_stream_declared_empty_has_a_mock_test_file() -> None:
    # The standard tests do not read a stream listed under `empty_streams`, so only a mock test covers it.
    config = yaml.safe_load(ACCEPTANCE_TEST_CONFIG.read_text())
    declared_empty = {
        stream["name"] for entry in config["acceptance_tests"]["basic_read"]["tests"] for stream in entry.get("empty_streams") or []
    }
    with_a_mock_test = {path.stem.removeprefix("test_") for path in (UNIT_TESTS / "mock_server").glob("test_*.py")}

    assert declared_empty
    assert declared_empty - with_a_mock_test == set()
