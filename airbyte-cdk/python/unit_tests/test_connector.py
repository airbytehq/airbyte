#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

import pytest
from airbyte_cdk import AirbyteSpec, Connector
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus


class TestAirbyteSpec:
    VALID_SPEC = {
        "documentationUrl": "https://google.com",
        "connectionSpecification": {
            "type": "object",
            "required": ["api_token"],
            "additionalProperties": False,
            "properties": {"api_token": {"type": "string"}},
        },
    }

    def test_from_file(self):
        expected = self.VALID_SPEC
        with tempfile.NamedTemporaryFile("w") as f:
            f.write(json.dumps(self.VALID_SPEC))
            f.flush()
            actual = AirbyteSpec.from_file(f.name)
            assert expected == json.loads(actual.spec_string)

    def test_from_file_nonexistent(self):
        with pytest.raises(OSError):
            AirbyteSpec.from_file("/tmp/i do not exist")


class MockConnector(Connector):
    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        pass


@pytest.fixture()
def mock_config():
    return {"bogus": "file"}


@pytest.fixture
def nonempty_file(mock_config):
    with tempfile.NamedTemporaryFile("w") as file:
        file.write(json.dumps(mock_config))
        file.flush()
        yield file


@pytest.fixture
def integration():
    return MockConnector()


def test_read_config(nonempty_file, integration: Connector, mock_config):
    actual = integration.read_config(nonempty_file.name)
    assert mock_config == actual


def test_write_config(integration, mock_config):
    config_path = Path(tempfile.gettempdir()) / "config.json"
    integration.write_config(mock_config, config_path)
    with open(config_path, "r") as actual:
        assert mock_config == json.loads(actual.read())
