#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import tempfile
from typing import Any, Mapping, MutableMapping

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources import Source


class MockSource(Source):
    def read(
        self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ):
        pass

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]):
        pass

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]):
        pass


@pytest.fixture
def source():
    return MockSource()


def test_read_state(source):
    state = {"updated_at": "yesterday"}

    with tempfile.NamedTemporaryFile("w") as state_file:
        state_file.write(json.dumps(state))
        state_file.flush()
        actual = source.read_state(state_file.name)
        assert state == actual


def test_read_state_nonexistent(source):
    assert {} == source.read_state("")


def test_read_catalog(source):
    configured_catalog = {
        "streams": [
            {
                "stream": {"name": "mystream", "json_schema": {"type": "object", "properties": {"k": "v"}}},
                "destination_sync_mode": "overwrite",
                "sync_mode": "full_refresh",
            }
        ]
    }
    expected = ConfiguredAirbyteCatalog.parse_obj(configured_catalog)
    with tempfile.NamedTemporaryFile("w") as catalog_file:
        catalog_file.write(expected.json(exclude_unset=True))
        catalog_file.flush()
        actual = source.read_catalog(catalog_file.name)
        assert actual == expected
