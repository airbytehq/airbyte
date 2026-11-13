#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
from packaging.specifiers import SpecifierSet
from source_freshcaller.source import SourceFreshcaller

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type


logger = logging.getLogger("airbyte")
sample_config = {
    "api_key": "YOUR_FRESHCALLER_API_KEY",
    "start_date": "2021-08-02T00:00:00Z",
    "domain": "sample-domain",
}


def test_python_constraint_allows_base_image_python():
    tomllib = pytest.importorskip("tomllib")
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    python_constraint = tomllib.loads(pyproject_path.read_text())["tool"]["poetry"]["dependencies"]["python"]
    specifier = SpecifierSet(python_constraint)

    assert "3.13.14" in specifier
    assert "3.10.0" in specifier


def test_spec():
    source = SourceFreshcaller(catalog=None, config={}, state=None)

    spec = source.spec(logger).connectionSpecification

    assert spec["required"] == ["domain", "api_key"]


def test_streams():
    source = SourceFreshcaller(catalog=None, config=sample_config, state=None)

    streams = source.streams(sample_config)

    assert {stream.name for stream in streams} == {"users", "teams", "calls", "call_metrics"}


def test_read_users_full_refresh(requests_mock):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name="users", json_schema={}, supported_sync_modes=[SyncMode.full_refresh]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )
    url = f"https://{sample_config['domain']}.freshcaller.com/api/v1/users"
    requests_mock.get(url, json={"users": [{"id": 1}, {"id": 2}]})
    source = SourceFreshcaller(catalog=catalog, config=sample_config, state=None)

    messages = list(source.read(logger=logger, config=sample_config, catalog=catalog))
    records = [message.record.data for message in messages if message.type == Type.RECORD]

    assert [record["id"] for record in records] == [1, 2]
    assert len(requests_mock.request_history) == 1
    request = requests_mock.request_history[0]
    assert request.headers["X-Api-Auth"] == sample_config["api_key"]
    assert request.headers["Accept"] == "application/json"
    parsed_url = urlsplit(request.url)
    assert (parsed_url.scheme, parsed_url.netloc, parsed_url.path) == (
        "https",
        f"{sample_config['domain']}.freshcaller.com",
        "/api/v1/users",
    )
    assert parse_qs(parsed_url.query) == {"per_page": ["1000"]}
