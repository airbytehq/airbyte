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
        "description": '<p>Newest <b>story</b> from <a href="https://example.com/?a=1&b=2">AT&T</a></p>',
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
def test_read_skips_items_without_a_parseable_date():
    feed = (
        b'<?xml version="1.0"?><rss version="2.0"><channel>'
        b"<item><title>Undated</title><guid>undated</guid></item>"
        b"<item><title>Bad date</title><guid>bad-date</guid><pubDate>not a date</pubDate></item>"
        b"<item><title>Out of range</title><guid>out-of-range</guid><pubDate>Mon, 09 Nov 2026 10:00:00 +2500</pubDate></item>"
        b"<item><title>Dated</title><guid>dated</guid><pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate></item>"
        b"</channel></rss>"
    )
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=feed, headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL)

    assert [record["guid"] for record in _records(output)] == ["dated"]
    assert not output.errors


@pytest.mark.parametrize(
    "body, content_type, expected_record",
    [
        pytest.param(
            '<?xml version="1.0" encoding="ISO-8859-1"?><rss version="2.0"><channel><item><title>Caf\xe9</title>'
            "<guid>declared-latin1</guid><pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>".encode("iso-8859-1"),
            "application/rss+xml",
            {"title": "Caf\xe9", "guid": "declared-latin1", "published": "2026-11-09T10:00:00+00:00"},
            id="declared_encoding_without_header_charset",
        ),
        pytest.param(
            '<?xml version="1.0"?><rss version="2.0"><channel><item><title>\u201cCaf\xe9\u201d \u2013 na\xefve</title>'
            "<guid>undeclared-cp1252</guid><pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>".encode("cp1252"),
            "text/xml",
            {"title": "\u201cCaf\xe9\u201d \u2013 na\xefve", "guid": "undeclared-cp1252", "published": "2026-11-09T10:00:00+00:00"},
            id="undeclared_single_byte_encoding",
        ),
        pytest.param(
            b'<rss version="2.0"><channel><item><title>Internal id</title><guid isPermaLink="false">https://example.com/ids/1</guid>'
            b"<pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>",
            "application/rss+xml",
            {"title": "Internal id", "guid": "https://example.com/ids/1", "published": "2026-11-09T10:00:00+00:00"},
            id="guid_is_permalink_false_is_not_a_link",
        ),
        pytest.param(
            b'<rss version="2.0"><channel><item><title>A&#1;B&#x0B;C</title><guid>control-references</guid>'
            b"<pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>",
            "application/rss+xml",
            {"title": "A\x01B\x0bC", "guid": "control-references", "published": "2026-11-09T10:00:00+00:00"},
            id="numeric_control_character_references",
        ),
        pytest.param(
            b'<feed version="0.3" xmlns="http://purl.org/atom/ns#"><entry><title>Atom 0.3 entry</title>'
            b'<link rel="alternate" type="text/html" href="https://example.net/atom03"/><id>tag:example.net,2026:atom03</id>'
            b"<issued>2026-11-09T10:00:00Z</issued></entry></feed>",
            "application/atom+xml",
            {
                "title": "Atom 0.3 entry",
                "link": "https://example.net/atom03",
                "guid": "tag:example.net,2026:atom03",
                "published": "2026-11-09T10:00:00+00:00",
            },
            id="atom_0_3",
        ),
        pytest.param(
            b'<feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss"><entry><id>media-no-slash</id>'
            b"<updated>2026-11-09T10:00:00Z</updated><media:group><media:description>Media desc</media:description></media:group>"
            b"</entry></feed>",
            "application/atom+xml",
            {"description": "Media desc", "guid": "media-no-slash", "published": "2026-11-09T10:00:00+00:00"},
            id="media_rss_namespace_without_trailing_slash",
        ),
        pytest.param(
            b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://my.netscape.com/rdf/simple/0.9/" '
            b'xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><title>RSS 0.90</title></channel>'
            b"<item><title>RSS 0.90 item</title><link>https://example.org/rss090</link>"
            b"<dc:date>2026-11-09T10:00:00Z</dc:date></item></rdf:RDF>",
            "application/rdf+xml",
            {"title": "RSS 0.90 item", "link": "https://example.org/rss090", "published": "2026-11-09T10:00:00+00:00"},
            id="rss_0_90",
        ),
    ],
)
@freeze_time(_NOW)
def test_read_decodes_and_maps_less_common_feed_variants(body, content_type, expected_record):
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=body, headers={"Content-Type": content_type})

        output = _read(_FEED_URL)

    assert _records(output) == [expected_record]


@pytest.mark.parametrize(
    "body, content_type, expected_warning",
    [
        pytest.param(
            _feed("not_a_feed.html"),
            "text/html; charset=utf-8",
            "https://example.com/ could not be parsed as an RSS, RDF or Atom feed",
            id="not_well_formed_html",
        ),
        pytest.param(
            b'<?xml version="1.0"?><opml version="2.0"><body><outline text="Example" xmlUrl="https://example.com/feed.rss"/></body></opml>',
            "text/x-opml",
            "https://example.com/ is not an RSS, RDF or Atom feed: its root element is <opml>",
            id="well_formed_opml",
        ),
    ],
)
@freeze_time(_NOW)
def test_non_feed_response_reads_no_records_logs_warning_and_passes_check(body, content_type, expected_warning):
    config = {"url": "https://example.com/"}
    with requests_mock.Mocker() as http:
        http.get(config["url"], content=body, headers={"Content-Type": content_type})

        output = _read(config["url"])
        check_status = get_source(config).check(logging.getLogger("airbyte"), config).status

    assert _records(output) == []
    assert not output.errors
    assert any(expected_warning in message.log.message for message in output.logs)
    assert check_status == Status.SUCCEEDED


@freeze_time(_NOW)
def test_incremental_read_resumes_from_legacy_state_value():
    state = StateBuilder().with_stream_state("items", {"published": "2026-11-09T09:15:00+00:00"}).build()
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_feed("rss2_namespaced.xml"), headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL, SyncMode.incremental, state)

    assert [record["guid"] for record in _records(output)] == ["https://example.com/news/namespaced", "story-3"]
    assert output.most_recent_state.stream_state.__dict__ == {"published": "2026-11-09T16:30:00+0000"}


def _rss(*items: str, namespaces: str = "") -> bytes:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" {namespaces}><channel><title>T</title>'
        + "".join(items)
        + "</channel></rss>"
    ).encode()


def test_future_dated_item_does_not_move_state_past_now():
    scheduled = "<item><guid>scheduled</guid><pubDate>Thu, 12 Nov 2026 10:00:00 GMT</pubDate></item>"
    today = "<item><guid>today</guid><pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate></item>"
    tomorrow = "<item><guid>tomorrow</guid><pubDate>Tue, 10 Nov 2026 12:00:00 GMT</pubDate></item>"
    headers = {"Content-Type": "application/rss+xml"}

    with requests_mock.Mocker() as http, freeze_time("2026-11-09T18:00:00Z"):
        http.get(_FEED_URL, content=_rss(scheduled, today), headers=headers)
        first = _read(_FEED_URL, SyncMode.incremental)
    state = StateBuilder().with_stream_state("items", first.most_recent_state.stream_state.__dict__).build()
    with requests_mock.Mocker() as http, freeze_time("2026-11-10T18:00:00Z"):
        http.get(_FEED_URL, content=_rss(scheduled, tomorrow, today), headers=headers)
        second = _read(_FEED_URL, SyncMode.incremental, state)

    assert [record["guid"] for record in _records(first)] == ["today"]
    assert first.most_recent_state.stream_state.__dict__ == {"published": "2026-11-09T10:00:00+0000"}
    assert [record["guid"] for record in _records(second)] == ["tomorrow"]


@pytest.mark.parametrize(
    "namespace",
    [
        pytest.param("http://backend.userland.com/rss2", id="userland_rss2"),
        pytest.param("http://blogs.law.harvard.edu/tech/rss", id="harvard_tech_rss"),
    ],
)
@freeze_time(_NOW)
def test_read_rss_feed_with_legacy_default_namespace(namespace):
    item = (
        "<item><title>Story</title><link>https://example.com/story</link><guid>story-1</guid>"
        "<pubDate>Mon, 09 Nov 2026 12:00:00 GMT</pubDate></item>"
    )
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_rss(item, namespaces=f'xmlns="{namespace}"'), headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL)

    assert _records(output) == [
        {"title": "Story", "link": "https://example.com/story", "guid": "story-1", "published": "2026-11-09T12:00:00+00:00"}
    ]


@freeze_time(_NOW)
def test_read_resolves_relative_links_against_channel_and_link_xml_base():
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_feed("rss2_xml_base.xml"), headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL)

    assert [(record["link"], record.get("enclosure")) for record in _records(output)] == [
        ("https://other.example/news/story-1", "https://other.example/news/audio/ep1.mp3"),
        ("https://other.example/posts/story-2", None),
    ]


_ATOM_XHTML_FEED = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>urn:uuid:xhtml-summary</id>
    <updated>2026-11-09T10:00:00Z</updated>
    <summary type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml"><p>Hi <a href="https://example.net/x">there</a></p></div></summary>
  </entry>
  <entry>
    <id>urn:uuid:xhtml-content</id>
    <updated>2026-11-09T11:00:00Z</updated>
    <content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">AT&amp;T <img src="https://example.net/i.png"/></div></content>
  </entry>
</feed>"""

_RSS_MIXED_CONTENT_FEED = b"""<rss version="2.0"><channel><item>
<guid>mixed-1</guid><pubDate>Mon, 09 Nov 2026 10:00:00 GMT</pubDate>
<description>AT&amp;T <b>x &amp; y</b></description>
</item></channel></rss>"""


@pytest.mark.parametrize(
    "feed, expected_descriptions",
    [
        pytest.param(
            _ATOM_XHTML_FEED,
            ['AT&amp;T <img src="https://example.net/i.png" />', '<p>Hi <a href="https://example.net/x">there</a></p>'],
            id="atom_xhtml",
        ),
        pytest.param(_RSS_MIXED_CONTENT_FEED, ["AT&amp;T <b>x &amp; y</b>"], id="rss_mixed_content"),
    ],
)
@freeze_time(_NOW)
def test_read_description_with_child_markup_keeps_published_html(feed, expected_descriptions):
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=feed, headers={"Content-Type": "application/xml"})

        output = _read(_FEED_URL)

    assert [record["description"] for record in _records(output)] == expected_descriptions


@pytest.mark.parametrize(
    "pub_date, published",
    [
        pytest.param("Mon, 09 Nov 2026 10:00:00 -05:00", "2026-11-09T15:00:00+00:00", id="colon_offset"),
        pytest.param("Mon, 09 Nov 2026 10:00:00 GMT+0530", "2026-11-09T04:30:00+00:00", id="gmt_offset"),
        pytest.param("Mon, 09 Nov 2026 10:00:00 PT", "2026-11-09T18:00:00+00:00", id="pt"),
        pytest.param("Mon, 09 Nov 2026 10:00:00 MEST", "2026-11-09T08:00:00+00:00", id="mest"),
    ],
)
@freeze_time("2026-11-09T20:00:00Z")
def test_read_applies_zone_offsets_that_email_utils_reads_as_naive(pub_date, published):
    item = f"<item><title>Zoned</title><pubDate>{pub_date}</pubDate></item>"
    with requests_mock.Mocker() as http:
        http.get(_FEED_URL, content=_rss(item), headers={"Content-Type": "application/rss+xml"})

        output = _read(_FEED_URL)

    assert _records(output) == [{"title": "Zoned", "published": published}]


@pytest.mark.parametrize(
    "namespaces, date_element",
    [
        pytest.param(
            'xmlns:dcterms="http://purl.org/dc/terms/"', "<dcterms:issued>2026-11-09T10:00:00Z</dcterms:issued>", id="dcterms_issued"
        ),
        pytest.param(
            'xmlns:atom="http://www.w3.org/2005/Atom"', "<atom:published>2026-11-09T10:00:00Z</atom:published>", id="atom_published"
        ),
        pytest.param("", "<published>2026-11-09T10:00:00Z</published>", id="unnamespaced_published"),
        pytest.param("", "<pubdate>Mon, 09 Nov 2026 10:00:00 GMT</pubdate>", id="lowercase_pubdate"),
    ],
)
@freeze_time(_NOW)
def test_read_rss_item_dated_by_other_published_elements(namespaces, date_element):
    with requests_mock.Mocker() as http:
        http.get(
            _FEED_URL,
            content=_rss(f"<item><guid>item-1</guid>{date_element}</item>", namespaces=namespaces),
            headers={"Content-Type": "application/rss+xml"},
        )

        output = _read(_FEED_URL)

    assert _records(output) == [{"guid": "item-1", "published": "2026-11-09T10:00:00+00:00"}]


@pytest.mark.parametrize("now", ["2026-11-09T18:00:00Z", "2026-11-10T18:00:00Z"])
def test_read_time_only_date_is_not_stamped_with_the_sync_date(now):
    items = (
        "<item><guid>time-only</guid><dc:date>10:00Z</dc:date></item>",
        f"<item><guid>dated</guid><dc:date>{now[:10]}T12:00:00Z</dc:date></item>",
    )
    with requests_mock.Mocker() as http, freeze_time(now):
        http.get(
            _FEED_URL,
            content=_rss(*items, namespaces='xmlns:dc="http://purl.org/dc/elements/1.1/"'),
            headers={"Content-Type": "application/rss+xml"},
        )
        output = _read(_FEED_URL)

    assert _records(output) == [{"guid": "dated", "published": f"{now[:10]}T12:00:00+00:00"}]
