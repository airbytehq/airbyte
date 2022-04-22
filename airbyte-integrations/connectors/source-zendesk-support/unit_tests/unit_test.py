#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import calendar
from datetime import datetime
from urllib.parse import parse_qsl, urlparse

import pendulum
import pytest
import pytz
import requests
from source_zendesk_support.source import BasicApiTokenAuthenticator
from source_zendesk_support.streams import (
    DATETIME_FORMAT,
    END_OF_STREAM_KEY,
    BaseSourceZendeskSupportStream,
    SourceZendeskIncrementalExportStream,
    TicketComments,
    Tickets,
)

# config
STREAM_ARGS = {
    "subdomain": "test",
    "start_date": "2022-01-27T00:00:00Z",
    "authenticator": BasicApiTokenAuthenticator("test@airbyte.io", "api_token"),
}

DATETIME_STR = "2021-07-22T06:55:55Z"
DATETIME_FROM_STR = datetime.strptime(DATETIME_STR, DATETIME_FORMAT)
STREAM_URL = "https://subdomain.zendesk.com/api/v2/stream.json?&start_time=1647532987&page=1"
STREAM_RESPONSE: dict = {
    "ticket_events": [
        {
            "child_events": [
                {
                    "id": 99999,
                    "via": {},
                    "via_reference_id": None,
                    "type": "Comment",
                    "author_id": 10,
                    "body": "test_comment",
                    "html_body": '<div class="zd-comment" dir="auto">test_comment<br/></div>',
                    "plain_body": "test_comment",
                    "public": True,
                    "attachments": [],
                    "audit_id": 123456,
                    "created_at": "2022-03-17T16:03:07Z",
                    "event_type": "Comment",
                }
            ],
            "id": 999999,
            "ticket_id": 3,
            "timestamp": 1647532987,
            "created_at": "2022-03-17T16:03:07Z",
            "updater_id": 9999999,
            "via": "Web form",
            "system": {},
            "metadata": {},
            "event_type": "Audit",
        }
    ],
    "next_page": "https://subdomain.zendesk.com/api/v2/stream.json?&start_time=1122334455&page=2",
    "count": 215,
    "end_of_stream": False,
    "end_time": 1647532987,
}
TEST_STREAM = TicketComments(**STREAM_ARGS)


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


def test_check_start_time_param():
    expected = 1626936955
    start_time = calendar.timegm(pendulum.parse(DATETIME_STR).utctimetuple())
    output = SourceZendeskIncrementalExportStream.check_start_time_param(start_time)
    assert output == expected


def test_parse_next_page_number(requests_mock):
    expected = dict(parse_qsl(urlparse(STREAM_RESPONSE.get("next_page")).query)).get("page")
    requests_mock.get(STREAM_URL, json=STREAM_RESPONSE)
    test_response = requests.get(STREAM_URL)
    output = BaseSourceZendeskSupportStream._parse_next_page_number(test_response)
    assert output == expected


def test_next_page_token(requests_mock):
    # mocking the logic of next_page_token
    if STREAM_RESPONSE.get(END_OF_STREAM_KEY) is False:
        expected = {"created_at": 1122334455}
    else:
        expected = None
    requests_mock.get(STREAM_URL, json=STREAM_RESPONSE)
    test_response = requests.get(STREAM_URL)
    output = TEST_STREAM.next_page_token(test_response)
    assert expected == output


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # valid state, expect the value of the state
        ({"updated_at": "2022-04-01"}, 1648771200),
        # invalid state, expect the start_date from STREAM_ARGS
        ({"updated_at": ""}, 1643241600),
        ({"updated_at": None}, 1643241600),
        ({"missing_cursor": "2022-04-01"}, 1643241600),
    ],
    ids=["state present", "empty string in state", "state is None", "cursor is not in the state object"],
)
def test_check_stream_state(stream_state, expected):
    result = Tickets(**STREAM_ARGS).check_stream_state(stream_state)
    assert result == expected


def test_request_params(requests_mock):
    expected = {"start_time": calendar.timegm(pendulum.parse(STREAM_ARGS.get("start_date")).utctimetuple()), "include": "comment_events"}
    stream_state = None
    requests_mock.get(STREAM_URL, json=STREAM_RESPONSE)
    test_response = requests.get(STREAM_URL)
    next_page_token = TEST_STREAM.next_page_token(test_response)
    output = TEST_STREAM.request_params(stream_state, next_page_token)
    assert expected == output


def test_parse_response(requests_mock):
    requests_mock.get(STREAM_URL, json=STREAM_RESPONSE)
    test_response = requests.get(STREAM_URL)
    output = TEST_STREAM.parse_response(test_response)
    # get the first parsed element from generator
    parsed_output = list(output)[0]
    # check, if we have all transformations correctly
    for entity in TicketComments.list_entities_from_event:
        assert True if entity in parsed_output else False
