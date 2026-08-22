# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import pytest
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.decoders import XmlDecoder
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.utils.reading import read_records


CONFIG = {
    "search_query": "cat:cs.AI",
    "page_size": 2,
}


def _source(manifest_path: Path) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(manifest_path), config=CONFIG)


def _atom_feed(start_index: int, *entries: str) -> str:
    joined_entries = "\n".join(entries)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>3</opensearch:totalResults>
  <opensearch:startIndex>{start_index}</opensearch:startIndex>
  <opensearch:itemsPerPage>2</opensearch:itemsPerPage>
  {joined_entries}
</feed>"""


def _entry(identifier: str, title: str) -> str:
    return f"""
  <entry>
    <id>http://arxiv.org/abs/{identifier}</id>
    <updated>2024-01-02T00:00:00Z</updated>
    <published>2024-01-01T00:00:00Z</published>
    <title>{title}</title>
    <summary>Example summary for {identifier}.</summary>
    <author><name>Example Author</name></author>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <arxiv:primary_category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <link href="http://arxiv.org/abs/{identifier}" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/{identifier}" rel="related" type="application/pdf"/>
  </entry>"""


def test_papers_stream_parses_atom_xml_and_offsets_pages(manifest_path: Path, requests_mock) -> None:
    requested_starts: list[str] = []

    def respond(request: requests.PreparedRequest, context: Any) -> str:
        query = parse_qs(urlparse(request.url).query)
        requested_starts.append(query["start"][0])
        assert query["search_query"] == ["cat:cs.AI"]
        assert query["max_results"] == ["2"]
        context.headers["Content-Type"] = "application/atom+xml"
        if query["start"] == ["0"]:
            return _atom_feed(0, _entry("2401.00001v1", "First paper"), _entry("2401.00002v1", "Second paper"))
        return _atom_feed(2, _entry("2401.00003v1", "Third paper"))

    requests_mock.get("https://export.arxiv.org/api/query", text=respond)

    output = read_records(_source(manifest_path), CONFIG, "papers", SyncMode.full_refresh)

    assert requested_starts == ["0", "2"]
    assert [record.record.data["id"] for record in output.records] == [
        "http://arxiv.org/abs/2401.00001v1",
        "http://arxiv.org/abs/2401.00002v1",
        "http://arxiv.org/abs/2401.00003v1",
    ]
    assert output.records[0].record.data["category"]["@term"] == "cs.AI"
    assert output.records[0].record.data["arxiv:primary_category"]["@term"] == "cs.AI"


@pytest.mark.parametrize(
    ("response_body", "expected_record_count"),
    [
        pytest.param(_atom_feed(0, _entry("2401.00001v1", "Single paper")), 1, id="single_entry"),
        pytest.param(_atom_feed(0), 0, id="no_entries"),
    ],
)
def test_xml_decoder_shapes_match_papers_extractor(response_body: str, expected_record_count: int, requests_mock) -> None:
    requests_mock.get("https://export.arxiv.org/api/query", text=response_body)

    response = requests.get("https://export.arxiv.org/api/query", timeout=10)
    decoded = next(XmlDecoder(parameters={}).decode(response))
    entries = decoded["feed"].get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]

    assert len(entries) == expected_record_count
