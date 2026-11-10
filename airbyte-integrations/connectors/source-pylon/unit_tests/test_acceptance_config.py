# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import socket
from pathlib import Path
from unittest.mock import patch

import requests
import yaml
from conftest import get_source

from airbyte_cdk.test.entrypoint_wrapper import _run_command, discover


def test_acceptance_spec_and_discover_are_offline(manifest_path: Path) -> None:
    root = manifest_path.parent
    acceptance = yaml.safe_load((root / "acceptance-test-config.yml").read_text())
    assert "bypass_reason" not in acceptance
    sections = acceptance["acceptance_tests"]
    for section in ("connection", "basic_read", "incremental", "full_refresh"):
        assert "unit_tests/mock_server" in sections[section]["bypass_reason"]
    with (
        patch.object(requests.Session, "send", side_effect=AssertionError("Network access is forbidden")),
        patch.object(socket.socket, "connect", side_effect=AssertionError("Network access is forbidden")),
    ):
        for section in ("spec", "discovery"):
            config = json.loads((root / sections[section]["tests"][0]["config_path"]).read_text())
            source = get_source(config)
            if section == "spec":
                output = _run_command(source, ["spec"])
                assert len(output.spec_messages) == 1
            else:
                output = discover(source, config)
                assert len(output.catalog.catalog.streams) == 15
            assert output.errors == []
