#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import responses
from source_arxiv.streams import CategoriesStream, PapersStream

from airbyte_cdk.models import SyncMode
from airbyte_cdk.utils import AirbyteTracedException


ARXIV_URL = "https://export.arxiv.org/api/query"


def _read(stream, stream_state=None):
    return list(stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state or {}))


@responses.activate
def test_papers_pagination(config, xml_fixture):
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_1.xml"), status=200)
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_2.xml"), status=200)

    records = _read(PapersStream(config=config))

    assert [record["id"] for record in records] == ["2401.00001v1", "2401.00002v1", "2401.00003v1"]
    assert responses.calls[0].request.url.endswith("start=0&max_results=2&sortBy=lastUpdatedDate&sortOrder=ascending")
    assert "start=2" in responses.calls[1].request.url


@responses.activate
def test_papers_incremental_cursor_advances(config, xml_fixture):
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_1.xml"), status=200)
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_2.xml"), status=200)

    stream = PapersStream(config=config)
    records = _read(stream)

    assert records[-1]["updated"] == "2024-01-04T00:00:00Z"
    assert stream.state == {"updated": "2024-01-04T00:00:00Z"}


@responses.activate
def test_papers_incremental_no_new_records(config, xml_fixture):
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_1.xml"), status=200)
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_2.xml"), status=200)

    records = _read(PapersStream(config=config), stream_state={"updated": "2024-01-04T00:00:00Z"})

    assert records == []


@responses.activate
def test_xml_parse_error(config, xml_fixture):
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_malformed.xml"), status=200)

    stream = PapersStream(config=config)

    try:
        _read(stream)
    except AirbyteTracedException as exc:
        assert "malformed Atom XML" in str(exc)
    else:
        raise AssertionError("Expected malformed XML to raise AirbyteTracedException")


@responses.activate
def test_rate_limit_backoff_429_retry(config, xml_fixture):
    responses.add(responses.GET, ARXIV_URL, body="Rate limited", status=429, headers={"Retry-After": "1"})
    responses.add(responses.GET, ARXIV_URL, body=xml_fixture("papers_page_2_empty.xml"), status=200)

    records = _read(PapersStream(config=config))

    assert records == []
    assert len(responses.calls) == 2
    assert responses.calls[0].response.status_code == 429


def test_categories_static_list():
    records = list(CategoriesStream().read_records(sync_mode=SyncMode.full_refresh))
    ids = {record["id"] for record in records}

    assert "cs.AI" in ids
    assert "math.PR" in ids
    assert all(record["name"] and record["group"] for record in records)
