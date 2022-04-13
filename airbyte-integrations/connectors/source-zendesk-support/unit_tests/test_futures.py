#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from datetime import timedelta
from urllib.parse import urljoin

import pendulum
import pytest
import requests_mock
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from source_zendesk_support.source import BasicApiTokenAuthenticator
from source_zendesk_support.streams import Macros

STREAM_ARGS: dict = {
    "subdomain": "fake-subdomain",
    "start_date": "2021-01-27T00:00:00Z",
    "authenticator": BasicApiTokenAuthenticator("test@airbyte.io", "api_token"),
}


@pytest.mark.parametrize(
    "records_count,page_size,expected_futures_deque_len",
    [
        (1000, 100, 10),
        (1000, 10, 100),
        (0, 100, 0),
        (1, 100, 1),
        (101, 100, 2),
    ],
)
def test_proper_number_of_future_requests_generated(records_count, page_size, expected_futures_deque_len):
    stream = Macros(**STREAM_ARGS)
    stream.page_size = page_size

    with requests_mock.Mocker() as m:
        count_url = urljoin(stream.url_base, f"{stream.path()}/count.json")
        m.get(count_url, text=json.dumps({"count": {"value": records_count}}))
        records_url = urljoin(stream.url_base, stream.path())
        m.get(records_url)
        stream.generate_future_requests(sync_mode=SyncMode.full_refresh, cursor_field=stream.cursor_field)
        assert len(stream.future_requests) == expected_futures_deque_len


@pytest.mark.parametrize(
    "records_count,page_size,expected_futures_deque_len",
    [
        (10, 10, 10),
        (10, 100, 10),
        (10, 10, 0),
    ],
)
def test_parse_future_records(records_count, page_size, expected_futures_deque_len):
    stream = Macros(**STREAM_ARGS)
    stream.page_size = page_size
    expected_records = [
        {f"key{i}": f"val{i}", stream.cursor_field: (pendulum.parse("2020-01-01") + timedelta(days=i)).isoformat()}
        for i in range(records_count)
    ]

    with requests_mock.Mocker() as m:
        count_url = urljoin(stream.url_base, f"{stream.path()}/count.json")
        m.get(
            count_url,
            text=json.dumps({"count": {"value": records_count}}),
        )

        records_url = urljoin(stream.url_base, stream.path())
        m.get(records_url, text=json.dumps({stream.name: expected_records}))

        stream.generate_future_requests(sync_mode=SyncMode.full_refresh, cursor_field=stream.cursor_field)
        if not stream.future_requests and not expected_futures_deque_len:
            assert len(stream.future_requests) == 0 and not expected_records
        else:
            response = stream.future_requests[0]["future"].result()
            records = list(stream.parse_response(response, stream_state=None, stream_slice=None))
            assert records == expected_records


@pytest.mark.parametrize(
    "records_count,page_size,expected_futures_deque_len,should_retry",
    [
        (1000, 100, 10, True),
        (1000, 10, 100, True),
        # (0, 100, 0, True),
        # (1, 100, 1, False),
        # (101, 100, 2, False),
    ],
)
def test_read_records(records_count, page_size, expected_futures_deque_len, should_retry):
    stream = Macros(**STREAM_ARGS)
    stream.page_size = page_size
    expected_records = [
        {f"key{i}": f"val{i}", stream.cursor_field: (pendulum.parse("2020-01-01") + timedelta(days=i)).isoformat()}
        for i in range(page_size)
    ]

    with requests_mock.Mocker() as m:
        count_url = urljoin(stream.url_base, f"{stream.path()}/count.json")
        m.get(count_url, text=json.dumps({"count": {"value": records_count}}))

        records_url = urljoin(stream.url_base, stream.path())

        m.get(records_url, status_code=429 if should_retry else 200, headers={"X-Rate-Limit": "700"})

        if should_retry and expected_futures_deque_len:
            with pytest.raises(DefaultBackoffException):
                list(stream.read_records(sync_mode=SyncMode.full_refresh))
        else:
            assert list(stream.read_records(sync_mode=SyncMode.full_refresh)) == expected_records
