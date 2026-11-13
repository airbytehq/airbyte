#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import responses
from source_arxiv.source import SourceArxiv


ARXIV_URL = "https://export.arxiv.org/api/query"


@responses.activate
def test_check_connection_success(config, xml_fixture):
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_1.xml"), status=200)

    assert SourceArxiv().check_connection(None, config) == (True, None)


@responses.activate
def test_check_connection_invalid_query(config):
    responses.add(responses.GET, ARXIV_URL, body="Bad request", status=400)

    is_successful, error = SourceArxiv().check_connection(None, config)

    assert not is_successful
    assert "400" in error


def test_check_connection_requires_search_query():
    is_successful, error = SourceArxiv().check_connection(None, {"max_results_per_page": 100})

    assert not is_successful
    assert "search_query" in error


def test_streams(config):
    streams = SourceArxiv().streams(config)

    assert [stream.name for stream in streams] == ["papers", "categories"]
