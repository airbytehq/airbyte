#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import calendar
from datetime import datetime
from urllib.parse import parse_qsl, urlparse

import pytz
import requests
from source_zendesk_support.streams import DATETIME_FORMAT, BaseSourceZendeskSupportStream

DATETIME_STR = "2021-07-22T06:55:55Z"
DATETIME_FROM_STR = datetime.strptime(DATETIME_STR, DATETIME_FORMAT)
STREAM_URL = "https://subdomain.zendesk.com/api/v2/stream.json?&start_time=1647532987&page=1"
STREAM_RESPONSE: dict = {
    "data": [],
    "next_page": "https://subdomain.zendesk.com/api/v2/stream.json?&start_time=1647532987&page=2",
    "count": 215,
    "end_of_stream": True,
    "end_time": 1647532987,
}


def test_str2datetime():
    expected = datetime.strptime(DATETIME_STR, DATETIME_FORMAT)
    output = BaseSourceZendeskSupportStream.str2datetime(DATETIME_STR)
    assert output == expected


def test_datetime2str():
    expected = datetime.strftime(DATETIME_FROM_STR.replace(tzinfo=pytz.UTC), DATETIME_FORMAT)
    output = BaseSourceZendeskSupportStream.datetime2str(DATETIME_FROM_STR)
    assert output == expected


def test_str2unixtime():
    expected = calendar.timegm(DATETIME_FROM_STR.utctimetuple())
    output = BaseSourceZendeskSupportStream.str2unixtime(DATETIME_STR)
    assert output == expected


def test_parse_next_page_number(requests_mock):
    expected = dict(parse_qsl(urlparse(STREAM_RESPONSE.get("next_page")).query)).get("page")
    requests_mock.get(STREAM_URL, json=STREAM_RESPONSE)
    test_response = requests.get(STREAM_URL)
    output = BaseSourceZendeskSupportStream._parse_next_page_number(test_response)
    assert output == expected
