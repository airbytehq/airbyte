#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest
from requests import Response


_RESOURCE_DIR = Path(__file__).parent / "resource"


def _create_response(fixture_name: str) -> Response:
    response = Response()
    response._content = (_RESOURCE_DIR / fixture_name).read_bytes()
    response.url = f"https://example.com/{fixture_name}"
    return response


def test_rss2_feed(components_module):
    extractor = components_module.CustomExtractor()
    records = list(extractor.extract_records(_create_response("rss2.xml")))

    assert records == [
        {
            "title": "Full Featured Item",
            "link": "https://example.com/full",
            "description": "<p>HTML <b>description</b> with CDATA</p>",
            "author": "john@example.com (John Doe)",
            "category": "Tech",
            "comments": "https://example.com/full#comments",
            "enclosure": "https://example.com/audio.mp3",
            "guid": "full-456",
            "published": "2023-01-03T23:30:00+00:00",
        },
        {
            "title": "No PubDate Item",
            "link": "https://example.com/nodate",
            "description": "Item without a pubDate",
            "author": "jane@example.com (Jane Doe)",
            "guid": "nodate-123",
        },
        {
            "title": "Older Than Channel",
            "link": "https://example.com/older",
            "description": "Old item",
            "guid": "https://example.com/older",
            "published": "2023-01-01T12:00:00+00:00",
        },
    ]


def test_atom_feed(components_module):
    extractor = components_module.CustomExtractor()
    records = list(extractor.extract_records(_create_response("atom.xml")))

    assert records == [
        {
            "title": "Atom Entry Two",
            "link": "https://example.com/entry2",
            "description": "Summary of entry two",
            "author": "Bob Jones",
            "category": "News",
            "guid": "https://example.com/entry2",
            "published": "2023-01-03T10:00:00+00:00",
        },
        {
            "title": "Atom Entry One",
            "link": "https://example.com/entry1",
            "description": "Summary of entry one",
            "author": "Alice Smith",
            "category": "Updates",
            "guid": "https://example.com/entry1",
            "published": "2023-01-02T10:00:00+00:00",
        },
    ]


def test_rss2_single_item_feed(components_module):
    extractor = components_module.CustomExtractor()
    records = list(extractor.extract_records(_create_response("rss2_single.xml")))

    assert records == [
        {
            "title": "Only Item",
            "link": "https://example.com/only",
            "description": "The only item",
            "guid": "https://example.com/only",
            "published": "2023-01-05T09:15:00+00:00",
        }
    ]


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Wed, 02 Oct 2002 13:00:00 GMT", "2002-10-02T13:00:00+00:00"),
        ("Tue, 03 Jan 2023 18:30:00 EST", "2023-01-03T23:30:00+00:00"),
        ("2023-01-02T10:00:00Z", "2023-01-02T10:00:00+00:00"),
        ("2023-01-02T10:00:00+02:00", "2023-01-02T08:00:00+00:00"),
        ("garbage", None),
    ],
)
def test_to_iso_utc(components_module, value, expected):
    assert components_module._to_iso_utc(value) == expected


def test_invalid_xml_raises(components_module):
    extractor = components_module.CustomExtractor()
    response = Response()
    response._content = b"<html>not a feed"
    response.url = "https://example.com/not-a-feed"

    with pytest.raises(ValueError, match="not a valid RSS/Atom feed"):
        list(extractor.extract_records(response))
