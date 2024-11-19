#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import calendar
import copy
import logging
import re
from datetime import datetime
from unittest.mock import Mock, patch
from urllib.parse import parse_qsl, urlparse

import freezegun
import pendulum
import pytest
import pytz
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from source_zendesk_support.source import BasicApiTokenAuthenticator, SourceZendeskSupport
from source_zendesk_support.streams import (
    DATETIME_FORMAT,
    END_OF_STREAM_KEY,
    LAST_END_TIME_KEY,
    BaseZendeskSupportStream,
    StatefulTicketMetrics,
    StatelessTicketMetrics,
    TicketMetricsStateMigration,
    TicketMetrics,
    SourceZendeskIncrementalExportStream,
    Tickets,
    UserSettingsStream,
)
from test_data.data import TICKET_EVENTS_STREAM_RESPONSE
from conftest import find_stream
from utils import read_full_refresh

TICKET_SUBSTREAMS = [StatefulTicketMetrics]

# prepared config
STREAM_ARGS = {
    "subdomain": "sandbox",
    "start_date": "2021-06-01T00:00:00Z",
    "authenticator": BasicApiTokenAuthenticator("test@airbyte.io", "api_token"),
}

# raw config
TEST_CONFIG = {
    "subdomain": "sandbox",
    "start_date": "2021-06-01T00:00:00Z",
    "credentials": {"credentials": "api_token", "email": "integration-test@airbyte.io", "api_token": "api_token"},
}

# raw old config
TEST_OLD_CONFIG = {
    "auth_method": {"auth_method": "api_token", "email": "integration-test@airbyte.io", "api_token": "api_token"},
    "subdomain": "sandbox",
    "start_date": "2021-06-01T00:00:00Z",
}

TEST_CONFIG_WITHOUT_START_DATE = {
    "subdomain": "sandbox",
    "credentials": {"credentials": "api_token", "email": "integration-test@airbyte.io", "api_token": "api_token"},
}

# raw config oauth
TEST_CONFIG_OAUTH = {
    "subdomain": "sandbox",
    "start_date": "2021-06-01T00:00:00Z",
    "credentials": {"credentials": "oauth2.0", "access_token": "test_access_token"},
}

DATETIME_STR = "2021-07-22T06:55:55Z"
DATETIME_FROM_STR = datetime.strptime(DATETIME_STR, DATETIME_FORMAT)
STREAM_URL = "https://subdomain.zendesk.com/api/v2/stream.json?&start_time=1647532987&page=1"
URL_BASE = "https://sandbox.zendesk.com/api/v2/"


def snake_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_stream_instance(stream_class, args):
    if stream_class in TICKET_SUBSTREAMS:
        parent = Tickets(**args)
        return stream_class(parent=parent, **args)
    return stream_class(**args)


def test_date_time_format():
    assert DATETIME_FORMAT == "%Y-%m-%dT%H:%M:%SZ"


def test_last_end_time_key():
    assert LAST_END_TIME_KEY == "_last_end_time"


def test_end_of_stream_key():
    assert END_OF_STREAM_KEY == "end_of_stream"


def test_token_authenticator():
    # we expect base64 from creds input
    expected = "dGVzdEBhaXJieXRlLmlvL3Rva2VuOmFwaV90b2tlbg=="
    result = BasicApiTokenAuthenticator("test@airbyte.io", "api_token")
    assert result._token == expected


@pytest.mark.parametrize(
    "config",
    [(TEST_CONFIG), (TEST_CONFIG_OAUTH)],
    ids=["api_token", "oauth"],
)
def test_convert_config2stream_args(config):
    result = SourceZendeskSupport().convert_config2stream_args(config)
    assert "authenticator" in result


@freezegun.freeze_time("2022-01-01")
def test_default_start_date():
    result = SourceZendeskSupport().convert_config2stream_args(TEST_CONFIG_WITHOUT_START_DATE)
    assert result["start_date"] == "2020-01-01T00:00:00Z"


@pytest.mark.parametrize(
    "config, expected",
    [
        (TEST_CONFIG, "aW50ZWdyYXRpb24tdGVzdEBhaXJieXRlLmlvL3Rva2VuOmFwaV90b2tlbg=="),
        (TEST_CONFIG_OAUTH, "test_access_token"),
        (TEST_OLD_CONFIG, "aW50ZWdyYXRpb24tdGVzdEBhaXJieXRlLmlvL3Rva2VuOmFwaV90b2tlbg=="),
    ],
    ids=["api_token", "oauth", "old_config"],
)
def test_get_authenticator(config, expected):
    # we expect base64 from creds input
    result = SourceZendeskSupport().get_authenticator(config=config)
    assert result._token == expected


@pytest.mark.parametrize(
    "response, start_date, check_passed",
    [({"active_features": {"organization_access_enabled": True}}, "2020-01-01T00:00:00Z", True), ({}, "2020-01-00T00:00:00Z", False)],
    ids=["check_successful", "invalid_start_date"],
)
def test_check(response, start_date, check_passed):
    config = copy.deepcopy(TEST_CONFIG)
    config["start_date"] = start_date
    with patch.object(UserSettingsStream, "get_settings", return_value=response) as mock_method:
        ok, _ = SourceZendeskSupport().check_connection(logger=logging.Logger, config=config)
        assert check_passed == ok
        if ok:
            mock_method.assert_called()


@pytest.mark.parametrize(
    "ticket_forms_response, status_code, expected_n_streams, expected_warnings, reason",
    [
        ('{"ticket_forms": [{"id": 1, "updated_at": "2021-07-08T00:05:45Z"}]}', 200, 37, [], None),
        (
                '{"error": "Not sufficient permissions"}',
                403,
                34,
                [
                    "An exception occurred while trying to access TicketForms stream: Forbidden. You don't have permission to access this resource.. Skipping this stream."
                ],
                None,
        ),
        (
                "",
                404,
                34,
                [
                    "An exception occurred while trying to access TicketForms stream: Not found. The requested resource was not found on the server.. Skipping this stream."
                ],
                "Not Found",
        ),
    ],
    ids=["forms_accessible", "forms_inaccessible", "forms_not_exists"],
)
def test_full_access_streams(caplog, requests_mock, ticket_forms_response, status_code, expected_n_streams, expected_warnings, reason):
    requests_mock.get("/api/v2/ticket_forms", status_code=status_code, text=ticket_forms_response, reason=reason)
    result = SourceZendeskSupport().streams(config=TEST_CONFIG)
    assert len(result) == expected_n_streams
    logged_warnings = (record for record in caplog.records if record.levelname == "WARNING")
    for msg in expected_warnings:
        assert msg in next(logged_warnings).message


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_str_to_datetime():
    expected = datetime.strptime(DATETIME_STR, DATETIME_FORMAT)
    output = BaseZendeskSupportStream.str_to_datetime(DATETIME_STR)
    assert output == expected


def test_datetime_to_str():
    expected = datetime.strftime(DATETIME_FROM_STR.replace(tzinfo=pytz.UTC), DATETIME_FORMAT)
    output = BaseZendeskSupportStream.datetime_to_str(DATETIME_FROM_STR)
    assert output == expected


def test_str_to_unixtime():
    expected = calendar.timegm(DATETIME_FROM_STR.utctimetuple())
    output = BaseZendeskSupportStream.str_to_unixtime(DATETIME_STR)
    assert output == expected


def test_check_start_time_param():
    expected = 1626936955
    start_time = calendar.timegm(pendulum.parse(DATETIME_STR).utctimetuple())
    output = SourceZendeskIncrementalExportStream.validate_start_time(start_time)
    assert output == expected


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # valid state, expect the value of the state
        ({"generated_timestamp": 1648771200}, 1648771200),
        (None, 1622505600),
    ],
    ids=["state present", "state is None"],
)
def test_check_stream_state(stream_state, expected):
    result = Tickets(**STREAM_ARGS).get_stream_state_value(stream_state)
    assert result == expected


def test_parse_response(requests_mock):
    requests_mock.get("https://sandbox.zendesk.com/api/v2/incremental/ticket_events.json?include=comment_events&start_time=1622505600",
                      json=TICKET_EVENTS_STREAM_RESPONSE)
    ticket_comments_stream = find_stream("ticket_comments", TEST_CONFIG)
    output = ticket_comments_stream.read_only_records()
    # get the first parsed element from generator
    parsed_output = list(output)[0]
    # check, if we have all transformations correctly
    for entity in ["via_reference_id", "ticket_id", "timestamp"]:
        assert entity in parsed_output


class TestAllStreams:

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (StatefulTicketMetrics, "tickets/13/metrics"),
            (StatelessTicketMetrics, "ticket_metrics"),
            (Tickets, "incremental/tickets/cursor.json"),
        ],
        ids=[
            "StatefulTicketMetrics",
            "StatelessTicketMetrics",
            "Tickets",
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
        result = stream.path(stream_slice={"ticket_id": "13"})
        assert result == expected


class TestSourceZendeskSupportStream:

    def test_stateful_ticket_metrics_parse_response(self, requests_mock):
        parent = Tickets(**STREAM_ARGS)
        stream = StatefulTicketMetrics(parent=parent, **STREAM_ARGS)
        expected = {"ticket_id": 13, "_ab_updated_at": 1647532987}
        response_field = stream.response_list_name

        requests_mock.get(STREAM_URL, json={response_field: expected})
        test_response = requests.get(STREAM_URL)

        stream_slice = {"ticket_id": 13, "_ab_updated_at": 1647532987}
        output = list(stream.parse_response(response=test_response, stream_state=None, stream_slice=stream_slice))

        expected = expected if isinstance(expected, list) else [expected]
        assert expected == output

    #
    @pytest.mark.parametrize(
        "stream_cls",
        [(StatefulTicketMetrics), (StatelessTicketMetrics), (Tickets)],
        ids=["StatefulTicketMetrics", "StatelessTicketMetrics", "Tickets"],
    )
    def test_url_base(self, stream_cls):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
        result = stream.url_base
        assert result == URL_BASE


class TestSourceZendeskSupportFullRefreshStream:
    @pytest.mark.parametrize(
        "stream_cls",
        [(UserSettingsStream)],
        ids=[
            "UserSettingsStream",
        ],
    )
    def test_url_base(self, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.url_base
        assert result == URL_BASE

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (UserSettingsStream),

        ],
        ids=[
            "UserSettingsStream",
        ],
    )
    def test_next_page_token(self, requests_mock, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        stream_name = snake_case(stream.__class__.__name__)
        requests_mock.get(STREAM_URL, json={stream_name: {}})
        test_response = requests.get(STREAM_URL)
        output = stream.next_page_token(test_response)
        assert output is None

    @pytest.mark.parametrize(
        "stream_cls, expected_params",
        [
            (UserSettingsStream, {}),
        ],
        ids=[
            "UserSettingsStream",
        ],
    )
    def test_request_params(self, stream_cls, expected_params):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.request_params(next_page_token=None, stream_state=None)
        assert expected_params == result


class TestSourceZendeskIncrementalExportStream:
    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Tickets),
        ],
        ids=[
            "Tickets",
        ],
    )
    def test_check_start_time_param(self, stream_cls):
        expected = int(dict(parse_qsl(urlparse(STREAM_URL).query)).get("start_time"))
        stream = stream_cls(**STREAM_ARGS)
        result = stream.validate_start_time(expected)
        assert result == expected



    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Tickets),
        ],
        ids=[
            "Tickets",
        ],
    )
    def test_next_page_token(self, requests_mock, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        stream_name = snake_case(stream.__class__.__name__)
        requests_mock.get(STREAM_URL, json={stream_name: {}})
        test_response = requests.get(STREAM_URL)
        output = stream.next_page_token(test_response)
        assert output == {}

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Tickets, {"start_time": 1622505600}),
        ],
        ids=[
            "Tickets",
        ],
    )
    def test_request_params(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.request_params(next_page_token=None, stream_state=None)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Tickets),
        ],
        ids=[
            "Tickets",
        ],
    )
    def test_parse_response(self, requests_mock, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        stream_name = snake_case(stream.__class__.__name__)
        expected = [{"updated_at": "2022-03-17T16:03:07Z"}]
        requests_mock.get(STREAM_URL, json={stream_name: expected})
        test_response = requests.get(STREAM_URL)
        output = list(stream.parse_response(test_response))
        assert expected == output

def test_read_tickets_stream(requests_mock):
    requests_mock.get(
        "https://subdomain.zendesk.com/api/v2/incremental/tickets/cursor.json",
        json={
            "tickets": [
                {"custom_fields": []},
                {},
                {
                    "custom_fields": [
                        {"id": 360023382300, "value": None},
                        {"id": 360004841380, "value": "customer_tickets"},
                        {"id": 360022469240, "value": "5"},
                        {"id": 360023712840, "value": False},
                    ]
                },
            ],
            "end_of_stream": True,
        },
    )

    stream = Tickets(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    records = read_full_refresh(stream)
    assert records == [
        {"custom_fields": []},
        {},
        {
            "custom_fields": [
                {"id": 360023382300, "value": None},
                {"id": 360004841380, "value": "customer_tickets"},
                {"id": 360022469240, "value": "5"},
                {"id": 360023712840, "value": "False"},
            ]
        },
    ]


def test_read_ticket_metric_events_request_params(requests_mock):
    first_page_response = {
        "ticket_metric_events": [
            {"id": 1, "ticket_id": 123, "metric": "agent_work_time", "instance_id": 0, "type": "measure", "time": "2020-01-01T01:00:00Z"},
            {
                "id": 2,
                "ticket_id": 123,
                "metric": "pausable_update_time",
                "instance_id": 0,
                "type": "measure",
                "time": "2020-01-01T01:00:00Z",
            },
            {"id": 3, "ticket_id": 123, "metric": "reply_time", "instance_id": 0, "type": "measure", "time": "2020-01-01T01:00:00Z"},
            {
                "id": 4,
                "ticket_id": 123,
                "metric": "requester_wait_time",
                "instance_id": 1,
                "type": "activate",
                "time": "2020-01-01T01:00:00Z",
            },
        ],
        "meta": {"has_more": True, "after_cursor": "<after_cursor>", "before_cursor": "<before_cursor>"},
        "links": {
            "prev": "https://subdomain.zendesk.com/api/v2/incremental/ticket_metric_events.json?page%5Bbefore%5D=<before_cursor>&page%5Bsize%5D=100&start_time=1577836800",
            "next": "https://subdomain.zendesk.com/api/v2/incremental/ticket_metric_events.json?page%5Bafter%5D=<after_cursor>&page%5Bsize%5D=100&start_time=1577836800",
        },
        "end_of_stream": False,
    }

    second_page_response = {
        "ticket_metric_events": [
            {
                "id": 5163373143183,
                "ticket_id": 130,
                "metric": "reply_time",
                "instance_id": 1,
                "type": "fulfill",
                "time": "2022-07-18T16:39:48Z",
            },
            {
                "id": 5163373143311,
                "ticket_id": 130,
                "metric": "requester_wait_time",
                "instance_id": 0,
                "type": "measure",
                "time": "2022-07-18T16:39:48Z",
            },
        ],
        "meta": {"has_more": False, "after_cursor": "<before_cursor>", "before_cursor": "<before_cursor>"},
        "links": {
            "prev": "https://subdomain.zendesk.com/api/v2/incremental/ticket_metric_events.json?page%5Bbefore%5D=<before_cursor>&page%5Bsize%5D=100&start_time=1577836800",
            "next": "https://subdomain.zendesk.com/api/v2/incremental/ticket_metric_events.json?page%5Bbefore%5D=<before_cursor>&page%5Bsize%5D=100&start_time=1577836800",
        },
        "end_of_stream": True,
    }
    # Register both URLs with `requests_mock`
    requests_mock.get(
        "https://sandbox.zendesk.com/api/v2/incremental/ticket_metric_events?page%5Bsize%5D=100&start_time=1622505600",
        json=first_page_response
    )
    requests_mock.get(
        "https://subdomain.zendesk.com/api/v2/incremental/ticket_metric_events.json?page%5Bafter%5D=%3Cafter_cursor%3E&page%5Bsize%5D=100&start_time=1577836800",
        json=second_page_response
    )
    stream = find_stream("ticket_metric_events", TEST_CONFIG)
    records = list(stream.read_only_records())
    assert len(records) == 6
    # also ticket_forms was requested
    assert requests_mock.call_count == 3
    assert requests_mock.last_request.qs == {"page[after]": ["<after_cursor>"], "page[size]": ["100"], "start_time": ["1577836800"]}


def test_read_non_json_error(requests_mock, caplog):
    requests_mock.get("https://subdomain.zendesk.com/api/v2/incremental/tickets/cursor.json", text="not_json_response")
    stream = Tickets(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    expected_message = (
        "Skipping stream tickets: Non-JSON response received. Please ensure that you have enough permissions for this stream."
    )
    read_full_refresh(stream)
    assert expected_message in (record.message for record in caplog.records if record.levelname == "ERROR")

class TestTicketMetrics:

    @pytest.mark.parametrize(
            "state, expected_implemented_stream",
            [
                ({"_ab_updated_at": 1727334000}, StatefulTicketMetrics),
                ({}, StatelessTicketMetrics),
            ]
    )
    def test_get_implemented_stream(self, state, expected_implemented_stream):
        stream = get_stream_instance(TicketMetrics, STREAM_ARGS)
        implemented_stream = stream._get_implemented_stream(state)
        assert isinstance(implemented_stream, expected_implemented_stream)

    @pytest.mark.parametrize(
            "sync_mode, state, expected_implemented_stream",
            [
                (SyncMode.incremental, {"_ab_updated_at": 1727334000}, StatefulTicketMetrics),
                (SyncMode.full_refresh, {}, StatelessTicketMetrics),
                (SyncMode.incremental, {}, StatelessTicketMetrics),
            ]
    )
    def test_stream_slices(self, sync_mode, state, expected_implemented_stream):
        stream = get_stream_instance(TicketMetrics, STREAM_ARGS)
        slices = list(stream.stream_slices(sync_mode=sync_mode, stream_state=state))
        assert isinstance(stream.implemented_stream, expected_implemented_stream)


class TestStatefulTicketMetrics:
    @pytest.mark.parametrize(
        "stream_state, response, expected_slices",
        [
            (
                {},
                {"tickets": [{"id": "13", "generated_timestamp": pendulum.parse(STREAM_ARGS["start_date"]).int_timestamp}, {"id": "80", "generated_timestamp": pendulum.parse(STREAM_ARGS["start_date"]).int_timestamp}]},
                [
                    {"ticket_id": "13", "_ab_updated_at": pendulum.parse(STREAM_ARGS["start_date"]).int_timestamp},
                    {"ticket_id": "80", "_ab_updated_at": pendulum.parse(STREAM_ARGS["start_date"]).int_timestamp},
                ],
            ),
            (
                {"_ab_updated_state": pendulum.parse("2024-04-17T19:34:06Z").int_timestamp},
                {"tickets": [{"id": "80", "generated_timestamp": pendulum.parse("2024-04-17T19:34:06Z").int_timestamp}]},
                [{"ticket_id": "80", "_ab_updated_at": pendulum.parse("2024-04-17T19:34:06Z").int_timestamp}],
            ),
            ({"_ab_updated_state": pendulum.parse("2024-04-17T19:34:06Z").int_timestamp}, {"tickets": []}, []),
        ],
        ids=[
            "read_without_state",
            "read_with_state",
            "read_with_abnormal_state",
        ],
    )
    def test_stream_slices(self, requests_mock, stream_state, response, expected_slices):
        stream = get_stream_instance(StatefulTicketMetrics, STREAM_ARGS)
        requests_mock.get(f"https://sandbox.zendesk.com/api/v2/incremental/tickets/cursor.json", json=response)
        assert list(stream.stream_slices(sync_mode=SyncMode.incremental, stream_state=stream_state)) == expected_slices

    def test_read_with_error(self, requests_mock):
        stream = get_stream_instance(StatefulTicketMetrics, STREAM_ARGS)
        requests_mock.get(
            f"https://sandbox.zendesk.com/api/v2/tickets/13/metrics",
            json={"error": "RecordNotFound", "description": "Not found"}
        )

        records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice={"ticket_id": "13"}))

        assert records == []

    @pytest.mark.parametrize(
        "status_code, response_action",
        (
                (200, ResponseAction.SUCCESS),
                (404, ResponseAction.IGNORE),
                (403, ResponseAction.IGNORE),
                (500, ResponseAction.RETRY),
                (429, ResponseAction.RATE_LIMITED),
        )
    )
    def test_should_retry(self, status_code: int, response_action: bool):
        stream = get_stream_instance(StatefulTicketMetrics, STREAM_ARGS)
        mocked_response = requests.Response()
        mocked_response.status_code = status_code
        assert stream.get_error_handler().interpret_response(mocked_response).response_action == response_action

    @pytest.mark.parametrize(
        "current_stream_state, record_cursor_value, expected",
        [
            ({ "_ab_updated_at": 1727334000}, 1727420400, { "_ab_updated_at": 1727420400}),
            ({ "_ab_updated_at": 1727334000}, 1700000000, { "_ab_updated_at": 1727334000}),
        ]
    )
    def test_get_updated_state(self, current_stream_state, record_cursor_value, expected):
        stream = get_stream_instance(StatefulTicketMetrics, STREAM_ARGS)
        latest_record = { "id": 1, "_ab_updated_at": record_cursor_value}
        output_state = stream._get_updated_state(current_stream_state=current_stream_state, latest_record=latest_record)
        assert output_state == expected


class TestStatelessTicketMetrics:
    @pytest.mark.parametrize(
            "start_date, response, expected",
            [
                (
                    "2023-01-01T00:00:00Z",
                    { "ticket_metrics": [{"id": 1, "ticket_id": 999, "updated_at": "2023-02-01T00:00:00Z"}, {"id": 2, "ticket_id": 1000, "updated_at": "2024-02-01T00:00:00Z"}]},
                    [
                        {"id": 1, "ticket_id": 999, "updated_at": "2023-02-01T00:00:00Z", "_ab_updated_at": pendulum.parse("2023-02-01T00:00:00Z").int_timestamp},
                        {"id": 2, "ticket_id": 1000, "updated_at": "2024-02-01T00:00:00Z", "_ab_updated_at": pendulum.parse("2024-02-01T00:00:00Z").int_timestamp}
                    ]
                ),
                (
                    "2024-01-01T00:00:00Z",
                    { "ticket_metrics": [{"id": 1, "ticket_id": 999, "updated_at": "2023-02-01T00:00:00Z"}, {"id": 2, "ticket_id": 1000, "updated_at": "2024-02-01T00:00:00Z"}]},
                    [
                        {"id": 2, "ticket_id": 1000, "updated_at": "2024-02-01T00:00:00Z", "_ab_updated_at": pendulum.parse("2024-02-01T00:00:00Z").int_timestamp}
                    ]
                )
            ]
    )
    def test_parse_response(self, requests_mock, start_date, response, expected):
        stream_args = copy.deepcopy(STREAM_ARGS)
        stream_args.update({"start_date": start_date})
        stream = StatelessTicketMetrics(**stream_args)
        requests_mock.get(STREAM_URL, json=response)
        test_response = requests.get(STREAM_URL)
        output = list(stream.parse_response(test_response, {}))
        assert expected == output

    @pytest.mark.parametrize(
            "has_more, expected",
            [
                (True, {"page[after]": "nextpagecursor"}),
                (False, None)
            ]
    )
    def test_next_page_token(self, mocker, has_more, expected):
        stream = StatelessTicketMetrics(**STREAM_ARGS)
        ticket_metrics_response = mocker.Mock()
        ticket_metrics_response.json.return_value = {"meta": { "after_cursor": "nextpagecursor", "has_more": has_more}}
        result = stream.next_page_token(response=ticket_metrics_response)
        assert expected == result

    def test_get_updated_state(self):
        stream = StatelessTicketMetrics(**STREAM_ARGS)
        stream._most_recently_updated_record = {"id": 2, "ticket_id": 1000, "updated_at": "2024-02-01T00:00:00Z", "_ab_updated_at": pendulum.parse("2024-02-01T00:00:00Z").int_timestamp}
        output_state = stream._get_updated_state(current_stream_state={}, latest_record={})
        expected_state = { "_ab_updated_at": pendulum.parse("2024-02-01T00:00:00Z").int_timestamp}
        assert output_state == expected_state





@pytest.mark.parametrize(
    "initial_state_cursor_field",
    [
        "generated_timestamp",
        "_ab_updated_at"
    ]
)
def test_ticket_metrics_state_migrataion(initial_state_cursor_field):
    state_migrator = TicketMetricsStateMigration()
    initial_state = {initial_state_cursor_field: 1672531200}
    expected_state = {"_ab_updated_at": 1672531200}
    output_state = state_migrator.migrate(initial_state)
    assert output_state == expected_state
