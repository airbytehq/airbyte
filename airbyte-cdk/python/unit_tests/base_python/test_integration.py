import json
from pathlib import Path
from typing import Mapping, Any, MutableMapping, Iterable

import pytest

from airbyte_cdk import AirbyteConnectionStatus, Status, ConfiguredAirbyteCatalog, AirbyteMessage, AirbyteCatalog
from airbyte_cdk.base_python import AirbyteLogger

from airbyte_cdk.base_python.integration import AirbyteSpec, Integration, Source
import tempfile


class TestAirbyteSpec:
    VALID_SPEC = {
        "documentationUrl": "https://google.com",
        "connectionSpecification": {
            "type": "object",
            "required": ["api_token"],
            "additionalProperties": False,
            "properties": {"api_token": {"type": "string"}}
        }
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


class MockIntegration(Integration):
    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        pass


class TestIntegration:
    mock_config = {'bogus': 'file'}

    @pytest.fixture
    def nonempty_file(self):
        with tempfile.NamedTemporaryFile("w") as file:
            file.write(json.dumps(self.mock_config))
            file.flush()
            yield file

    @pytest.fixture
    def integration(self):
        return MockIntegration()

    def test_read_config(self, nonempty_file, integration: Integration):
        actual = integration.read_config(nonempty_file.name)
        assert self.mock_config == actual

    def test_write_config(self, integration):
        config_path = Path(tempfile.gettempdir()) / 'config.json'
        integration.write_config(self.mock_config, config_path)
        with open(config_path, 'r') as actual:
            assert self.mock_config == json.loads(actual.read())


class MockSource(Source):
    def read(self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None):
        pass

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]):
        pass

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]):
        pass


class TestSource:
    @pytest.fixture
    def source(self):
        return MockSource()

    def test_read_state(self, source):
        state = {'updated_at': 'yesterday'}

        with tempfile.NamedTemporaryFile('w') as state_file:
            state_file.write(json.dumps(state))
            state_file.flush()
            actual = source.read_state(state_file.name)
            assert state == actual

    def test_read_state_nonexistent(self, source):
        assert {} == source.read_state('')

    def test_read_catalog(self, source):
        configured_catalog = {'streams': [{
            'stream': {'name': 'mystream', 'json_schema': {'type': 'object', 'properties': {'k': 'v'}}},
            'destination_sync_mode': 'overwrite',
            'sync_mode': 'full_refresh'}]
        }
        expected = ConfiguredAirbyteCatalog.parse_obj(configured_catalog)
        with tempfile.NamedTemporaryFile('w') as catalog_file:
            catalog_file.write(expected.json(exclude_unset=True))
            catalog_file.flush()
            actual = source.read_catalog(catalog_file.name)
            assert actual == expected
