# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Integration acceptance tests for source-tulip.

These tests run against a live Tulip API. They require valid credentials
in secrets/config.json (gitignored).

Run with:
    pytest integration_tests/acceptance.py -v --tb=short
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parent.parent
PYTHON = str(PROJECT_ROOT / ".venv_airbyte" / "bin" / "python")
MAIN = str(PROJECT_ROOT / "main.py")
CONFIG = str(PROJECT_ROOT / "secrets" / "config.json")
CATALOG = str(PROJECT_ROOT / "integration_tests" / "configured_catalog.json")


def _run_connector(*args, timeout=60):
    """Run the connector and return parsed JSONL messages."""
    result = subprocess.run(
        [PYTHON, MAIN, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PROJECT_ROOT),
    )
    messages = []
    for line in result.stdout.strip().split("\n"):
        if line:
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return messages, result.returncode


@pytest.fixture(scope="module")
def config_exists():
    if not Path(CONFIG).exists():
        pytest.skip("secrets/config.json not found — skipping integration tests")


class TestSpec:
    def test_outputs_valid_spec(self):
        messages, code = _run_connector("spec")
        assert code == 0
        spec_msgs = [m for m in messages if m.get("type") == "SPEC"]
        assert len(spec_msgs) == 1
        spec = spec_msgs[0]["spec"]
        assert "connectionSpecification" in spec
        conn_spec = spec["connectionSpecification"]
        assert "subdomain" in conn_spec["properties"]
        assert "api_key" in conn_spec["properties"]
        assert "api_secret" in conn_spec["properties"]


class TestCheck:
    def test_succeeds_with_valid_creds(self, config_exists):
        messages, code = _run_connector("check", "--config", CONFIG)
        assert code == 0
        status_msgs = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert len(status_msgs) == 1
        assert status_msgs[0]["connectionStatus"]["status"] == "SUCCEEDED"

    def test_fails_with_bad_creds(self, config_exists, tmp_path):
        bad_config = {
            "subdomain": "nonexistent-instance-xyz",
            "api_key": "invalid",
            "api_secret": "invalid",
        }
        bad_config_path = str(tmp_path / "bad_config.json")
        with open(bad_config_path, "w") as f:
            json.dump(bad_config, f)
        messages, code = _run_connector("check", "--config", bad_config_path)
        status_msgs = [m for m in messages if m.get("type") == "CONNECTION_STATUS"]
        assert len(status_msgs) == 1
        assert status_msgs[0]["connectionStatus"]["status"] == "FAILED"


class TestDiscover:
    def test_returns_catalog_with_streams(self, config_exists):
        messages, code = _run_connector("discover", "--config", CONFIG)
        assert code == 0
        catalog_msgs = [m for m in messages if m.get("type") == "CATALOG"]
        assert len(catalog_msgs) == 1
        streams = catalog_msgs[0]["catalog"]["streams"]
        assert len(streams) > 0

    def test_streams_have_incremental_support(self, config_exists):
        messages, _ = _run_connector("discover", "--config", CONFIG)
        catalog_msgs = [m for m in messages if m.get("type") == "CATALOG"]
        streams = catalog_msgs[0]["catalog"]["streams"]
        for stream in streams:
            assert "incremental" in stream["supported_sync_modes"]
            assert stream.get("source_defined_cursor") is True

    def test_streams_have_valid_schemas(self, config_exists):
        messages, _ = _run_connector("discover", "--config", CONFIG)
        catalog_msgs = [m for m in messages if m.get("type") == "CATALOG"]
        streams = catalog_msgs[0]["catalog"]["streams"]
        for stream in streams:
            schema = stream["json_schema"]
            assert schema["type"] == "object"
            props = schema["properties"]
            # All streams must have system fields
            assert "id" in props
            assert "_createdAt" in props
            assert "_updatedAt" in props
            assert "_sequenceNumber" in props


class TestRead:
    def test_reads_records(self, config_exists):
        messages, code = _run_connector(
            "read",
            "--config",
            CONFIG,
            "--catalog",
            CATALOG,
            timeout=120,
        )
        assert code == 0
        record_msgs = [m for m in messages if m.get("type") == "RECORD"]
        state_msgs = [m for m in messages if m.get("type") == "STATE"]
        assert len(record_msgs) > 0, "Expected at least one record"
        assert len(state_msgs) > 0, "Expected at least one state message"

    def test_records_have_expected_fields(self, config_exists):
        messages, _ = _run_connector(
            "read",
            "--config",
            CONFIG,
            "--catalog",
            CATALOG,
            timeout=120,
        )
        record_msgs = [m for m in messages if m.get("type") == "RECORD"]
        if record_msgs:
            data = record_msgs[0]["record"]["data"]
            assert "id" in data
            assert "_sequenceNumber" in data

    def test_incremental_returns_no_new_records(self, config_exists, tmp_path):
        """Run a full sync, save state, then re-run — should get 0 new records."""
        # First run: full sync
        messages, _ = _run_connector(
            "read",
            "--config",
            CONFIG,
            "--catalog",
            CATALOG,
            timeout=120,
        )
        state_msgs = [m for m in messages if m.get("type") == "STATE"]
        assert len(state_msgs) > 0

        # Save state from first run
        state_list = [msg["state"] for msg in state_msgs]
        state_path = str(tmp_path / "state.json")
        with open(state_path, "w") as f:
            json.dump(state_list, f)

        # Second run: incremental with state
        messages2, code = _run_connector(
            "read",
            "--config",
            CONFIG,
            "--catalog",
            CATALOG,
            "--state",
            state_path,
            timeout=120,
        )
        assert code == 0
        record_msgs2 = [m for m in messages2 if m.get("type") == "RECORD"]
        # Should have 0 new records since no data changed
        assert len(record_msgs2) == 0
