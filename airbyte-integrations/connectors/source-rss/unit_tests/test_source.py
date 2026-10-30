#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import List

import requests
import tomllib
from source_rss import SourceRss
from source_rss.components import CustomExtractor

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


CONNECTOR_DIR = Path(__file__).parent.parent
FEED_URL = "https://example.com/feed.rss"
CONFIG = {"url": FEED_URL}


def _rss_feed(published_dates: List[datetime]) -> str:
    items = "".join(
        f"<item><title>Item {index}</title><link>https://example.com/{index}</link>"
        f"<guid>guid-{index}</guid><pubDate>{format_datetime(published)}</pubDate></item>"
        for index, published in enumerate(published_dates)
    )
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>Feed</title>{items}</channel></rss>'


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name("items").with_sync_mode(sync_mode)).build()


def test_poetry_packages_are_in_docker_build_context() -> None:
    """`docker-images/Dockerfile.python-connector.dockerignore` only copies `source_*` dirs, so `poetry install` fails on any other package include."""
    pyproject = tomllib.loads((CONNECTOR_DIR / "pyproject.toml").read_text())
    includes = [package["include"] for package in pyproject["tool"]["poetry"]["packages"]]
    assert includes == ["source_rss"]


def test_extractor_maps_items_with_utc_published() -> None:
    published = datetime(2026, 10, 20, 12, 30, tzinfo=timezone(timedelta(hours=2)))
    response = requests.Response()
    response._content = _rss_feed([published]).encode()

    records = list(CustomExtractor().extract_records(response))

    assert records == [
        {
            "title": "Item 0",
            "link": "https://example.com/0",
            "guid": "guid-0",
            "published": "2026-10-20T10:30:00+00:00",
        }
    ]


def test_check(requests_mock) -> None:
    requests_mock.get(FEED_URL, text=_rss_feed([datetime.now(timezone.utc)]))

    status = SourceRss(config=CONFIG).check(logger=None, config=CONFIG)

    assert status.status.name == "SUCCEEDED"


def test_incremental_read_uses_state(requests_mock) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    state_value = now - timedelta(hours=2)
    requests_mock.get(FEED_URL, text=_rss_feed([now - timedelta(hours=3), now - timedelta(hours=1)]))
    catalog = _catalog(SyncMode.incremental)
    state = StateBuilder().with_stream_state("items", {"published": state_value.strftime("%Y-%m-%dT%H:%M:%S%z")}).build()

    output = read(SourceRss(catalog=catalog, config=CONFIG, state=state), CONFIG, catalog, state)

    assert not output.errors
    assert [record.record.data["guid"] for record in output.records] == ["guid-1"]
    assert output.most_recent_state.stream_state.published == (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S%z")


def test_full_refresh_read_returns_items_from_last_23_hours(requests_mock) -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    requests_mock.get(FEED_URL, text=_rss_feed([now - timedelta(days=2), now - timedelta(hours=1)]))
    catalog = _catalog(SyncMode.full_refresh)

    output = read(SourceRss(catalog=catalog, config=CONFIG, state=None), CONFIG, catalog)

    assert not output.errors
    assert [record.record.data["guid"] for record in output.records] == ["guid-1"]
