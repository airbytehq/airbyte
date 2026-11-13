# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


BASE_URL = "https://api.assemblyai.com/v2/transcript"
MANIFEST = Path(__file__).parents[1] / "manifest.yaml"
if not MANIFEST.exists():
    MANIFEST = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
CONFIG = {"api_key": "test-api-key", "start_date": "2024-03-01T00:00:00Z", "subtitle_format": "srt"}


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))


def source(config=CONFIG):
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST), config=config)


def test_catalog_and_legacy_config():
    connector = source({**CONFIG, "request_id": "legacy-lemur-id"})
    assert {stream.name for stream in connector.discover(logging.getLogger(), CONFIG).streams} == {
        "transcripts",
        "transcript_sentences",
        "paragraphs",
        "transcript_subtitle",
    }
    assert "request_id" not in connector.spec(logging.getLogger()).connectionSpecification["properties"]


@pytest.mark.parametrize("suffix", [".036402", ".036402Z", "", "Z"])
def test_transcripts_auth_pagination_and_timestamp_formats(suffix):
    older_url = f"{BASE_URL}?limit=100&before_id=newest"
    with requests_mock.Mocker() as http:
        first = http.get(
            BASE_URL,
            request_headers={"Authorization": CONFIG["api_key"]},
            json={
                "transcripts": [{"id": "newest", "created": f"2024-03-11T13:25:48{suffix}"}],
                "page_details": {"prev_url": older_url, "next_url": None},
            },
        )
        older = http.get(
            older_url,
            request_headers={"Authorization": CONFIG["api_key"]},
            json={
                "transcripts": [{"id": "older", "created": f"2024-03-10T13:25:48{suffix}"}],
                "page_details": {"prev_url": None, "next_url": f"{BASE_URL}?after_id=older"},
            },
        )
        catalog = CatalogBuilder().with_stream("transcripts", SyncMode.incremental).build()
        output = read(source(), CONFIG, catalog)

    assert not output.errors
    assert [message.record.data["id"] for message in output.records] == ["newest", "older"]
    assert first.call_count == 1
    assert older.call_count == 1


@pytest.mark.parametrize(
    "stream,endpoint,response",
    [
        ("transcript_sentences", "sentences", {"sentences": [{"text": "hello", "start": 0, "end": 100}]}),
        ("paragraphs", "paragraphs", {"paragraphs": [{"text": "hello", "start": 0, "end": 100}]}),
        ("transcript_subtitle", "redacted-audio", {"status": "redacted_audio_ready", "redacted_audio_url": "https://example.com/audio"}),
    ],
)
def test_child_streams_use_raw_api_key(stream, endpoint, response):
    with requests_mock.Mocker() as http:
        http.get(
            BASE_URL,
            request_headers={"Authorization": CONFIG["api_key"]},
            json={"transcripts": [{"id": "transcript-id", "created": "2024-03-11T13:25:48.036402"}], "page_details": {"prev_url": None}},
        )
        child = http.get(f"{BASE_URL}/transcript-id/{endpoint}", request_headers={"Authorization": CONFIG["api_key"]}, json=response)
        output = read(source(), CONFIG, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())

    assert not output.errors
    assert len(output.records) == 1
    assert child.called
