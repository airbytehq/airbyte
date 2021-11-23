#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from urllib.parse import quote_plus

import pytest
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_google_search_console.streams import ROW_LIMIT, SearchAnalyticsByDate


class MockResponse:
    def __init__(self, data_field: str, count: int):
        self.value = {data_field: [0 for i in range(count)]}

    def json(self):
        return self.value


@pytest.mark.parametrize(
    "count, expected",
    [
        (ROW_LIMIT, ROW_LIMIT),
        (ROW_LIMIT - 1, 0),
        (0, 0),
    ],
)
def test_pagination(count, expected):
    stream = SearchAnalyticsByDate(NoAuth(), ["https://example.com"], "start_date", "end_date")
    response = MockResponse(stream.data_field, count)
    stream.next_page_token(response)
    assert stream.start_row == expected


@pytest.mark.parametrize(
    "site_urls, sync_mode",
    [
        (["https://example1.com", "https://example2.com"], SyncMode.full_refresh),
        (["https://example1.com", "https://example2.com"], SyncMode.incremental),
        (["https://example.com"], SyncMode.full_refresh),
        (["https://example.com"], SyncMode.incremental),
    ],
)
def test_slice(site_urls, sync_mode):
    stream = SearchAnalyticsByDate(NoAuth(), site_urls, "start_date", "end_date")

    search_types = stream.search_types
    stream_slice = stream.stream_slices(sync_mode=sync_mode)

    for site_url in site_urls:
        for search_type in search_types:
            expected = {"site_url": quote_plus(site_url), "search_type": search_type}

            assert expected == next(stream_slice)


@pytest.mark.parametrize(
    "current_stream_state, latest_record, expected",
    [
        (
            {"https://example.com": {"web": {"date": "2023-01-01"}}},
            {"site_url": "https://example.com", "search_type": "web", "date": "2021-01-01"},
            {"https://example.com": {"web": {"date": "2023-01-01"}}, "date": "2023-01-01"},
        ),
        (
            {},
            {"site_url": "https://example.com", "search_type": "web", "date": "2021-01-01"},
            {"https://example.com": {"web": {"date": "2021-01-01"}}, "date": "2021-01-01"},
        ),
        (
            {"https://example.com": {"web": {"date": "2021-01-01"}}},
            {"site_url": "https://example.com", "search_type": "web", "date": "2022-01-01"},
            {"https://example.com": {"web": {"date": "2022-01-01"}}, "date": "2022-01-01"},
        ),
    ],
)
def test_state(current_stream_state, latest_record, expected):
    stream = SearchAnalyticsByDate(NoAuth(), ["https://example.com"], "start_date", "end_date")

    value = stream.get_updated_state(current_stream_state, latest_record)
    assert value == expected
