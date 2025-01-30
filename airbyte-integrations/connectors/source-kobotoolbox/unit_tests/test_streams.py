#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import json
import requests
import pytest
from source_kobotoolbox.source import KoboToolStream

API_URL = "https://kf.kobotoolbox.org/api/v2"
PAGINATION_LIMIT = 30000

stream_config = {
    "config": {"username": "username", "password": "my_password", "start_time": "2023-03-15T00:00:00.000+05:30"},
    "form_id": "my_form_id",
    "schema": {},
    "name": "my_form",
    "api_url": API_URL,
    "pagination_limit": PAGINATION_LIMIT,
    "auth_token": "my_token_123"
}

CURSOR = 'endtime'


@pytest.mark.parametrize('config', [(stream_config)])
def test_stream_base_url(config):
    stream = KoboToolStream(**config)
    assert stream.url_base == f"{config['api_url']}/assets/{config['form_id']}/"


@pytest.mark.parametrize('config', [(stream_config)])
def test_json_schema(config):
    stream = KoboToolStream(**config)
    assert stream.get_json_schema() == {}


@pytest.mark.parametrize('config, next_page_token', [(stream_config, None)])
def test_request_params(config, next_page_token):
    stream = KoboToolStream(**config)
    assert stream.request_params({}, None, next_page_token) == {
        'start': 0, 
        'limit': config['pagination_limit'], 
        "sort": json.dumps({CURSOR: 1}),
        "query": json.dumps({CURSOR: {"$gte": config['config']['start_time']}})
    }


@pytest.mark.parametrize('config, total_records, params, next_page_token', [
    (
        stream_config,
        50000,
        {'start': 100, 'limit': 100},
        {'start': '200', 'limit': '100'}
    ),
    (
        stream_config,
        1729,
        {'start': 1700, 'limit': 100},
        None
    )
])
def test_next_page_token(config, params, next_page_token, total_records):
    stream = KoboToolStream(**config)
    response = Mock(spec=requests.Response)

    def fetch_next_page(params, total_records=total_records):
        prev = None
        next1 = None
        if params['limit'] + params['start'] < total_records:
            next1 = {'limit': params['limit'], 'start': params['limit'] + params['start']}

        if params['start'] > 0:
            prev = params

        return (prev, next1)

    def fetch_request(response, params, url, total_records=total_records):

        (prev, next1) = fetch_next_page(params)

        if prev is not None:
            prev = f"{url}?limit={prev['limit']}&start={prev['start']}"

        if next1 is not None:
            next1 = f"{url}?limit={next1['limit']}&start={next1['start']}"

        response.json.return_value = {
            "count": total_records,
            "next": next1,
            "previous": prev,
            "results": []
        }

        return response

    url = stream.url_base + stream.path()

    response = fetch_request(response, params, url)

    assert next_page_token == stream.next_page_token(response)
