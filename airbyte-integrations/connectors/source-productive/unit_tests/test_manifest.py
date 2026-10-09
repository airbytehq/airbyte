# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import requests
import yaml

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, Type
from airbyte_cdk.sources.declarative.concurrent_declarative_source import ConcurrentDeclarativeSource


CONFIG = {"api_key": "test-key", "organization_id": "123"}
LOGGER = logging.getLogger(__name__)


@pytest.fixture
def source():
    manifest = yaml.safe_load((Path(__file__).parents[1] / "manifest.yaml").read_text())
    return ConcurrentDeclarativeSource(source_config=manifest, config=CONFIG, catalog=None, state=None)


def test_spec_and_discovery(source):
    spec = source.spec(LOGGER).connectionSpecification
    assert set(spec["required"]) == {"api_key", "organization_id"}
    streams = {stream.name: stream for stream in source.discover(LOGGER, CONFIG).streams}
    assert len(streams) == 56
    assert "project_assignments" not in streams
    assert "memberships" in streams
    assert streams["boards"].source_defined_primary_key == [["id"]]


def test_requests_use_organization_header_and_boards_reads_paginated_folders(source, monkeypatch):
    requests_sent = []

    def send(session, request, **kwargs):
        url = urlparse(request.url)
        query = parse_qs(url.query)
        assert url.scheme == "https"
        assert url.netloc == "api.productive.io"
        assert request.headers["X-Auth-Token"] == CONFIG["api_key"]
        assert request.headers["X-Organization-Id"] == CONFIG["organization_id"]
        assert "X-Organization-Id" not in query
        assert url.path not in {"/api/v2/project_assignments", "/api/v2/boards"}
        requests_sent.append(url.path)
        records = []
        if url.path == "/api/v2/folders":
            assert query["page[size]"] == ["10"]
            page = int(query["page[number]"][0])
            assert page in {1, 2}
            ids = range(1, 11) if page == 1 else [11]
            records = [{"id": str(i), "type": "folders", "attributes": {"name": f"Folder {i}"}} for i in ids]
        response = requests.Response()
        response.status_code = 200
        response.headers["Content-Type"] = "application/json"
        response._content = json.dumps({"data": records}).encode()
        response.request = request
        response.url = request.url
        return response

    monkeypatch.setattr(requests.Session, "send", send)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
            for stream in source.discover(LOGGER, CONFIG).streams
        ]
    )
    messages = list(source.read(LOGGER, CONFIG, catalog))
    assert not [message for message in messages if message.type == Type.TRACE and message.trace.error]
    records = [message.record for message in messages if message.type == Type.RECORD and message.record.stream == "boards"]
    assert len(records) == 11
    assert [record.data["id"] for record in records] == [str(i) for i in range(1, 12)]
    assert all(record.data["type"] == "folders" for record in records)
    assert len(set(requests_sent)) == 56
    assert requests_sent.count("/api/v2/folders") == 2
