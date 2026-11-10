# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging
from pathlib import Path

import pytest
import requests_mock
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder


_NOW = "2026-11-09T18:00:00Z"
_FEED_URL = "https://example.com/feed.rss"
_RESOURCES = Path(__file__).parent / "resource"

_RSS_RECORDS = [
    {
        "title": "Oldest story",
        "link": "https://example.com/news/oldest",
        "description": "",
        "author": "",
        "guid": "https://example.com/news/oldest",
        "published": "2026-11-09T03:00:00+00:00",
    },
    {
        "title": "Namespaced story",
        "link": "https://example.com/news/namespaced",
        "description": "<p>Full content</p>",
        "author": "John Writer",
        "category": "Science",
        "guid": "https://example.com/news/namespaced",
        "published": "2026-11-09T09:15:00+00:00",
    },
    {
        "title": "Newest story",
        "link": "https://example.com/news/newest",
        "description": "<p>Newest <b>story</b></p>",
        "author": "editor@example.com (Jane Editor)",
        "category": "World",
        "comments": "https://example.com/news/newest#comments",
        "enclosure": "https://example.com/audio/newest.mp3",
        "guid": "story-3",
        "published": "2026-11-09T16:30:00+00:00",
    },
]


def _feed(file_name: str) -> bytes:
    return (_RESOURCES / file_name).read_bytes()


def _read(url: str, sync_mode: SyncMode = SyncMode.full_refresh, state=None):
    config = {"url": url}
    catalog = CatalogBuilder().with_stream("items", sync_mode).build()
    return read(get_source(config, state), config, catalog, state)


def _records(output):
    return [message.record.data for message in output.records]


@pytest.mark.parametrize(
    "configured_url",
    [
        pytest.param("https://example.com/feed?key=test123&format=rss", id="query_string"),
        pytest.param("https://example.com/rss/dyn/breaking_news.rss", id="file_extension"),
        pytest.param("https://example.com/feeds/", id="trailing_slash"),
        pytest.param("https://example.com/feeds", id="no_trailing_slash"),
        pytest.param("https://example.com/feeds/top%20stories.xml?tag=a%2Fb&q=caf%C3%A9", id="percent_encoding"),
    ],
)
@freeze_time(_NOW)
def test_read_requests_the_configured_url_unchanged(configured_url):
    with requests_mock.Mocker() as http:
        http.get(requests_mock.ANY, content=_feed("rss2_namespaced.xml"), headers={"Content-Type": "application/rss+xml"})

        output = _read(configured_url)

    assert [request.url for request in http.request_history] == [configured_url]
    assert [record["guid"] for record in _records(output)] == [
        "https://example.com/news/oldest",
        "https://example.com/news/namespaced",
        "story-3",
    ]


@freeze_time(_NOW)
def test_read_rss_feed_maps_core_and_namespaced_elements():
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_feed("rss2_namespaced.xml"), headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL)

    assert _records(output) == _RSS_RECORDS


@pytest.mark.parametrize(
    "file_name, content_type, expected_records",
    [
        pytest.param(
            "rdf.xml",
            "application/rdf+xml",
            [
                {
                    "title": "First item",
                    "link": "https://example.org/items/1",
                    "description": "First description",
                    "guid": "https://example.org/items/1",
                    "published": "2026-11-08T20:00:00+00:00",
                },
                {
                    "title": "Second item",
                    "link": "https://example.org/items/2",
                    "description": "Second description",
                    "author": "Alice",
                    "category": "Tech",
                    "guid": "https://example.org/items/2",
                    "published": "2026-11-09T07:00:00+00:00",
                },
            ],
            id="rdf",
        ),
        pytest.param(
            "atom.xml",
            "application/atom+xml; charset=utf-8",
            [
                {
                    "title": "First &lt;post&gt;",
                    "link": "https://example.net/blog/posts/first",
                    "description": "First summary",
                    "author": "Carol",
                    "guid": "urn:uuid:entry-1",
                    "published": "2026-11-09T09:00:00+00:00",
                },
                {
                    "title": "Updated only entry",
                    "link": "https://example.net/blog/posts/updated-only",
                    "enclosure": "https://example.net/audio/ep2.mp3",
                    "description": "Media description",
                    "author": "Bob (bob@example.net)",
                    "category": "news",
                    "guid": "urn:uuid:entry-2",
                    "published": "2026-11-09T10:00:00+00:00",
                },
            ],
            id="atom",
        ),
    ],
)
@freeze_time(_NOW)
def test_read_rdf_and_atom_feeds(file_name, content_type, expected_records):
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_feed(file_name), headers={"Content-Type": content_type})

        output = _read(_FEED_URL)

    assert _records(output) == expected_records


@freeze_time(_NOW)
def test_read_recovers_malformed_feed_with_header_only_charset():
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_feed("malformed_latin1.xml"), headers={"Content-Type": "text/xml; charset=ISO-8859-1"})

        output = _read(_FEED_URL)

    assert _records(output) == [
        {
            "title": "Tom & Jerry \xa0\xa9 2026 \x0b\x01",
            "link": "https://example.com/a?x=1&y=2",
            "description": "Caf\xe9 \u2014 bare & ampersand",
            "guid": "broken-1",
            "published": "2026-11-09T10:00:00+00:00",
        }
    ]


@freeze_time(_NOW)
def test_non_feed_response_reads_no_records_logs_warning_and_passes_check():
    config = {"url": "https://example.com/"}
    with requests_mock.Mocker() as http:
        http.get(config["url"], content=_feed("not_a_feed.html"), headers={"Content-Type": "text/html; charset=utf-8"})

        output = _read(config["url"])
        check_status = get_source(config).check(logging.getLogger("airbyte"), config).status

    assert _records(output) == []
    assert not output.errors
    assert any("https://example.com/ could not be parsed as an RSS, RDF or Atom feed" in message.log.message for message in output.logs)
    assert check_status == Status.SUCCEEDED


@freeze_time(_NOW)
def test_incremental_read_resumes_from_legacy_state_value():
    state = StateBuilder().with_stream_state("items", {"published": "2026-11-09T09:15:00+00:00"}).build()
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_feed("rss2_namespaced.xml"), headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL, SyncMode.incremental, state)

    assert [record["guid"] for record in _records(output)] == ["https://example.com/news/namespaced", "story-3"]
    assert output.most_recent_state.stream_state.__dict__ == {"published": "2026-11-09T16:30:00+0000"}
