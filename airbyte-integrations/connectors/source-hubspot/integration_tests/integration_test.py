"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from pathlib import Path
from typing import Mapping, Any, Tuple, List

import pytest
from airbyte_protocol import ConfiguredAirbyteCatalog, Type
from base_python import AirbyteLogger
from source_hubspot.source import SourceHubspot


HERE = Path(__file__).parent.absolute()


@pytest.fixture(scope="session", name="config")
def config_fixture() -> Mapping[str, Any]:
    config_filename = HERE.parent / "secrets" / "config.json"

    if not config_filename.exists():
        raise RuntimeError(f"Please provide credentials in {config_filename}")

    with open(str(config_filename)) as json_file:
        return json.load(json_file)


@pytest.fixture(scope="session", name="configured_catalog")
def configured_catalog_fixture() -> ConfiguredAirbyteCatalog:
    catalog_filename = HERE.parent / "sample_files" / "configured_catalog_deals.json"

    return ConfiguredAirbyteCatalog.parse_file(str(catalog_filename))


def read_stream(generator) -> Tuple[List, List]:
    records = []
    state = []

    for message in generator:
        if message.type == Type.RECORD:
            records.append(message)
        elif message.type == Type.STATE:
            state.append(message)

    return records, state


def test_deals_read(config, configured_catalog_fixture):
    """Read should return some records"""
    records, states = read_stream(SourceHubspot().read(AirbyteLogger(), config, configured_catalog_fixture))

    assert len(records) > 0
    assert not states


def test_second_read(config):
    """Second read should return same records as the first one"""
    records1, states1 = read_stream(SourceHubspot().read(AirbyteLogger(), config, configured_catalog_fixture))
    records2, states2 = read_stream(SourceHubspot().read(AirbyteLogger(), config, configured_catalog_fixture))

    assert records1 == records2
    assert states1 == states2

