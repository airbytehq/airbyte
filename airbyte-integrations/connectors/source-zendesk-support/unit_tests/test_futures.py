#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from datetime import timedelta
from urllib.parse import urljoin

import pendulum
import pytest
import requests
import requests_mock
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException
from requests.exceptions import ConnectionError
from source_zendesk_support.source import BasicApiTokenAuthenticator
from source_zendesk_support.streams import Macros

STREAM_ARGS: dict = {
    "subdomain": "fake-subdomain",
    "start_date": "2021-01-27T00:00:00Z",
    "authenticator": BasicApiTokenAuthenticator("test@airbyte.io", "api_token"),
}


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


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
    "records_count, page_size, expected_futures_deque_len, expected_exception",
    [
        (1000, 10, 100, DefaultBackoffException),
        (0, 100, 0, DefaultBackoffException),
        (150, 100, 2, ConnectionError),
        (1, 100, 1, None),
        (101, 101, 2, None),
    ],
)
def test_read_records(mocker, records_count, page_size, expected_futures_deque_len, expected_exception):
    stream = Macros(**STREAM_ARGS)
    stream.page_size = page_size
    should_retry = bool(expected_exception)
    expected_records_count = min(page_size, records_count) if should_retry else records_count

    def record_gen(start=0, end=page_size):
        for i in range(start, end):
            yield {f"key{i}": f"val{i}", stream.cursor_field: (pendulum.parse("2020-01-01") + timedelta(days=i)).isoformat()}

    with requests_mock.Mocker() as m:
        count_url = urljoin(stream.url_base, f"{stream.path()}/count.json")
        m.get(count_url, text=json.dumps({"count": {"value": records_count}}))

        records_url = urljoin(stream.url_base, stream.path())
        responses = [
            {
                "status_code": 429 if should_retry else 200,
                "headers": {"X-Rate-Limit": "700"},
                "text": "{}"
                if should_retry
                else json.dumps({"macros": list(record_gen(page * page_size, min(records_count, (page + 1) * page_size)))}),
            }
            for page in range(expected_futures_deque_len)
        ]
        m.get(records_url, responses)

        if expected_exception is ConnectionError:
            mocker.patch.object(requests.Session, "send", side_effect=ConnectionError())
        if should_retry and expected_futures_deque_len:
            with pytest.raises(expected_exception):
                list(stream.read_records(sync_mode=SyncMode.full_refresh))
        else:
            assert list(stream.read_records(sync_mode=SyncMode.full_refresh)) == list(record_gen(end=expected_records_count))
