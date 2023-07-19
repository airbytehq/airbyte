#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import calendar
import copy
import re
from datetime import datetime
from unittest.mock import patch
from urllib.parse import parse_qsl, urlparse

import pendulum
import pytest
import pytz
import requests
from airbyte_cdk import AirbyteLogger
from source_zendesk_support.source import BasicApiTokenAuthenticator, SourceZendeskSupport
from source_zendesk_support.streams import (
    DATETIME_FORMAT,
    END_OF_STREAM_KEY,
    LAST_END_TIME_KEY,
    AccountAttributes,
    AttributeDefinitions,
    AuditLogs,
    BaseSourceZendeskSupportStream,
    Brands,
    CustomRoles,
    GroupMemberships,
    Groups,
    Macros,
    OrganizationMemberships,
    Organizations,
    PostCommentVotes,
    Posts,
    SatisfactionRatings,
    Schedules,
    SlaPolicies,
    SourceZendeskIncrementalExportStream,
    SourceZendeskSupportStream,
    Tags,
    TicketAudits,
    TicketComments,
    TicketFields,
    TicketForms,
    TicketMetricEvents,
    TicketMetrics,
    Tickets,
    TicketSkips,
    Users,
    UserSettingsStream,
)
from test_data.data import TICKET_EVENTS_STREAM_RESPONSE
from utils import read_full_refresh

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


@pytest.mark.parametrize(
    "config, expected",
    [(TEST_CONFIG, "aW50ZWdyYXRpb24tdGVzdEBhaXJieXRlLmlvL3Rva2VuOmFwaV90b2tlbg=="), (TEST_CONFIG_OAUTH, "test_access_token")],
    ids=["api_token", "oauth"],
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
        ok, _ = SourceZendeskSupport().check_connection(logger=AirbyteLogger, config=config)
        assert check_passed == ok
        if ok:
            mock_method.assert_called()


@pytest.mark.parametrize(
    "ticket_forms_response, status_code, expected_n_streams, expected_warnings",
    [
        ({"ticket_forms": [{"id": 1, "updated_at": "2021-07-08T00:05:45Z"}]}, 200, 27, []),
        (
                {"error": "Not sufficient permissions"},
                403,
                24,
                ["Skipping stream ticket_forms: Check permissions, error message: Not sufficient permissions."],
        ),
    ],
    ids=["forms_accessible", "forms_inaccessible"],
)
def test_full_access_streams(caplog, requests_mock, ticket_forms_response, status_code, expected_n_streams, expected_warnings):
    requests_mock.get("/api/v2/ticket_forms", status_code=status_code, json=ticket_forms_response)
    result = SourceZendeskSupport().streams(config=TEST_CONFIG)
    assert len(result) == expected_n_streams
    logged_warnings = iter([record for record in caplog.records if record.levelname == "ERROR"])
    for msg in expected_warnings:
        assert msg in next(logged_warnings).message


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


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


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        # valid state, expect the value of the state
        ({"updated_at": "2022-04-01"}, 1648771200),
        # invalid state, expect the start_date from STREAM_ARGS
        ({"updated_at": ""}, 1622505600),
        ({"updated_at": None}, 1622505600),
        ({"missing_cursor": "2022-04-01"}, 1622505600),
    ],
    ids=["state present", "empty string in state", "state is None", "cursor is not in the state object"],
)
def test_check_stream_state(stream_state, expected):
    result = Tickets(**STREAM_ARGS).check_stream_state(stream_state)
    assert result == expected


def test_parse_response_from_empty_json(requests_mock):
    requests_mock.get(STREAM_URL, text="", status_code=403)
    test_response = requests.get(STREAM_URL)
    output = Schedules(**STREAM_ARGS).parse_response(test_response, {})
    assert list(output) == []


def test_parse_response(requests_mock):
    requests_mock.get(STREAM_URL, json=TICKET_EVENTS_STREAM_RESPONSE)
    test_response = requests.get(STREAM_URL)
    output = TicketComments(**STREAM_ARGS).parse_response(test_response)
    # get the first parsed element from generator
    parsed_output = list(output)[0]
    # check, if we have all transformations correctly
    for entity in TicketComments.list_entities_from_event:
        assert True if entity in parsed_output else False


def test_retry(mocker):
    backoff_time_mock = mocker.Mock()
    with mocker.patch.object(SourceZendeskSupportStream, "backoff_time", return_value=backoff_time_mock):
        stream = SourceZendeskSupportStream(**STREAM_ARGS)
        stream._retry(request=mocker.Mock(), retries=0)
        assert not backoff_time_mock.called, "backoff_time should not have been called"


class TestAllStreams:
    @pytest.mark.parametrize(
        "expected_stream_cls",
        [
            (AuditLogs),
            (GroupMemberships),
            (Groups),
            (Macros),
            (Organizations),
            (Posts),
            (OrganizationMemberships),
            (SatisfactionRatings),
            (SlaPolicies),
            (Tags),
            (TicketAudits),
            (TicketComments),
            (TicketFields),
            (TicketForms),
            (TicketMetrics),
            (TicketSkips),
            (TicketMetricEvents),
            (Tickets),
            (Users),
            (Brands),
            (CustomRoles),
            (Schedules),
            (AccountAttributes),
            (AttributeDefinitions),
        ],
        ids=[
            "AuditLogs",
            "GroupMemberships",
            "Groups",
            "Macros",
            "Organizations",
            "Posts",
            "OrganizationMemberships",
            "SatisfactionRatings",
            "SlaPolicies",
            "Tags",
            "TicketAudits",
            "TicketComments",
            "TicketFields",
            "TicketForms",
            "TicketMetrics",
            "TicketSkips",
            "TicketMetricEvents",
            "Tickets",
            "Users",
            "Brands",
            "CustomRoles",
            "Schedules",
            "AccountAttributes",
            "AttributeDefinitions",
        ],
    )
    def test_streams(self, expected_stream_cls):
        with patch.object(TicketForms, "read_records", return_value=[{}]) as mocked_records:
            streams = SourceZendeskSupport().streams(TEST_CONFIG)
            mocked_records.assert_called()
            for stream in streams:
                if expected_stream_cls in streams:
                    assert isinstance(stream, expected_stream_cls)

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (AuditLogs, "audit_logs"),
            (GroupMemberships, "group_memberships"),
            (Groups, "groups"),
            (Macros, "macros"),
            (Organizations, "organizations"),
            (Posts, "community/posts"),
            (OrganizationMemberships, "organization_memberships"),
            (SatisfactionRatings, "satisfaction_ratings"),
            (SlaPolicies, "slas/policies.json"),
            (Tags, "tags"),
            (TicketAudits, "ticket_audits"),
            (TicketComments, "incremental/ticket_events.json"),
            (TicketFields, "ticket_fields"),
            (TicketForms, "ticket_forms"),
            (TicketMetrics, "ticket_metrics"),
            (TicketSkips, "skips.json"),
            (TicketMetricEvents, "incremental/ticket_metric_events"),
            (Tickets, "incremental/tickets.json"),
            (Users, "incremental/users.json"),
            (Brands, "brands"),
            (CustomRoles, "custom_roles"),
            (Schedules, "business_hours/schedules.json"),
            (AccountAttributes, "routing/attributes"),
            (AttributeDefinitions, "routing/attributes/definitions"),
        ],
        ids=[
            "AuditLogs",
            "GroupMemberships",
            "Groups",
            "Macros",
            "Organizations",
            "Posts",
            "OrganizationMemberships",
            "SatisfactionRatings",
            "SlaPolicies",
            "Tags",
            "TicketAudits",
            "TicketComments",
            "TicketFields",
            "TicketForms",
            "TicketMetrics",
            "TicketSkips",
            "TicketMetricEvents",
            "Tickets",
            "Users",
            "Brands",
            "CustomRoles",
            "Schedules",
            "AccountAttributes",
            "AttributeDefinitions",
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.path()
        assert result == expected


class TestSourceZendeskSupportStream:
    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Macros),
            (Organizations),
            (Posts),
            (Groups),
            (SatisfactionRatings),
            (TicketFields),
            (TicketMetrics),
        ],
        ids=[
            "Macros",
            "Organizations",
            "Posts",
            "Groups",
            "SatisfactionRatings",
            "TicketFields",
            "TicketMetrics",
        ],
    )
    def test_parse_response(self, requests_mock, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        stream_name = snake_case(stream.__class__.__name__)
        expected = [{"updated_at": "2022-03-17T16:03:07Z"}]
        requests_mock.get(STREAM_URL, json={stream_name: expected})
        test_response = requests.get(STREAM_URL)
        output = list(stream.parse_response(test_response, None))
        assert expected == output

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Macros),
            (Organizations),
            (Posts),
            (Groups),
            (SatisfactionRatings),
            (TicketFields),
            (TicketMetrics),
        ],
        ids=[
            "Macros",
            "Organizations",
            "Posts",
            "Groups",
            "SatisfactionRatings",
            "TicketFields",
            "TicketMetrics",
        ],
    )
    def test_url_base(self, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.url_base
        assert result == URL_BASE

    @pytest.mark.parametrize(
        "stream_cls, current_state, last_record, expected",
        [
            (Macros, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
            (Posts, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
            (
                Organizations,
                {"updated_at": "2022-03-17T16:03:07Z"},
                {"updated_at": "2023-03-17T16:03:07Z"},
                {"updated_at": "2023-03-17T16:03:07Z"},
            ),
            (Groups, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
            (SatisfactionRatings, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
            (TicketFields, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
            (TicketMetrics, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
        ],
        ids=[
            "Macros",
            "Posts",
            "Organizations",
            "Groups",
            "SatisfactionRatings",
            "TicketFields",
            "TicketMetrics",
        ],
    )
    def test_get_updated_state(self, stream_cls, current_state, last_record, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.get_updated_state(current_state, last_record)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Macros, None),
            (Posts, None),
            (Organizations, None),
            (Groups, None),
            (TicketFields, None),
        ],
        ids=[
            "Macros",
            "Posts",
            "Organizations",
            "Groups",
            "TicketFields",
        ],
    )
    def test_next_page_token(self, stream_cls, expected, mocker):
        stream = stream_cls(**STREAM_ARGS)
        posts_response = mocker.Mock()
        posts_response.json.return_value = {"next_page": None}
        result = stream.next_page_token(response=posts_response)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Macros, {"start_time": 1622505600}),
            (Posts, {"start_time": 1622505600}),
            (Organizations, {"start_time": 1622505600}),
            (Groups, {"start_time": 1622505600}),
            (TicketFields, {"start_time": 1622505600}),
        ],
        ids=[
            "Macros",
            "Posts",
            "Organizations",
            "Groups",
            "TicketFields",
        ],
    )
    def test_request_params(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.request_params(stream_state={})
        assert expected == result


class TestSourceZendeskSupportFullRefreshStream:
    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Tags),
            (SlaPolicies),
            (Brands),
            (CustomRoles),
            (Schedules),
            (UserSettingsStream),
            (AccountAttributes),
            (AttributeDefinitions)
        ],
        ids=[
            "Tags",
            "SlaPolicies",
            "Brands",
            "CustomRoles",
            "Schedules",
            "UserSettingsStream",
            "AccountAttributes",
            "AttributeDefinitions",
        ],
    )
    def test_url_base(self, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.url_base
        assert result == URL_BASE

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Tags),
            (SlaPolicies),
            (Brands),
            (CustomRoles),
            (Schedules),
            (UserSettingsStream),
            (AccountAttributes),
            (AttributeDefinitions),
        ],
        ids=[
            "Tags",
            "SlaPolicies",
            "Brands",
            "CustomRoles",
            "Schedules",
            "UserSettingsStream",
            "AccountAttributes",
            "AttributeDefinitions",
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
            (Tags, {"page[size]": 100}),
            (SlaPolicies, {}),
            (Brands, {"page[size]": 100}),
            (CustomRoles, {}),
            (Schedules, {"page[size]": 100}),
            (UserSettingsStream, {}),
            (AccountAttributes, {}),
            (AttributeDefinitions, {}),
        ],
        ids=[
            "Tags",
            "SlaPolicies",
            "Brands",
            "CustomRoles",
            "Schedules",
            "UserSettingsStream",
            "AccountAttributes",
            "AttributeDefinitions",
        ],
    )
    def test_request_params(self, stream_cls, expected_params):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.request_params(next_page_token=None, stream_state=None)
        assert expected_params == result


class TestSourceZendeskSupportCursorPaginationStream:
    @pytest.mark.parametrize(
        "stream_cls, current_state, last_record, expected",
        [
            (GroupMemberships, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
            (TicketForms, {}, {"updated_at": "2023-03-17T16:03:07Z"}, {"updated_at": "2023-03-17T16:03:07Z"}),
            (TicketMetricEvents, {}, {"time": "2024-03-17T16:03:07Z"}, {"time": "2024-03-17T16:03:07Z"}),
            (TicketAudits, {}, {"created_at": "2025-03-17T16:03:07Z"}, {"created_at": "2025-03-17T16:03:07Z"}),
            (OrganizationMemberships, {}, {"updated_at": "2025-03-17T16:03:07Z"}, {"updated_at": "2025-03-17T16:03:07Z"}),
            (TicketSkips, {}, {"updated_at": "2025-03-17T16:03:07Z"}, {"updated_at": "2025-03-17T16:03:07Z"}),
        ],
        ids=[
            "GroupMemberships",
            "TicketForms",
            "TicketMetricEvents",
            "TicketAudits",
            "OrganizationMemberships",
            "TicketSkips",
        ],
    )
    def test_get_updated_state(self, stream_cls, current_state, last_record, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.get_updated_state(current_state, last_record)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, response, expected",
        [
            (GroupMemberships, {}, None),
            (TicketForms, {}, None),
            (TicketMetricEvents, {}, None),
            (TicketAudits, {}, None),
            (
                TicketMetrics,
                {
                    "meta": {"has_more": True, "after_cursor": "<after_cursor>", "before_cursor": "<before_cursor>"},
                    "links": {
                        "prev": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bbefore%5D=<before_cursor>%3D&page%5Bsize%5D=2",
                        "next": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bafter%5D=<after_cursor>%3D&page%5Bsize%5D=2",
                    },
                },
                {"page[after]": "<after_cursor>"},
            ),
            (SatisfactionRatings, {}, None),
            (
                OrganizationMemberships,
                {
                    "meta": {"has_more": True, "after_cursor": "<after_cursor>", "before_cursor": "<before_cursor>"},
                    "links": {
                        "prev": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bbefore%5D=<before_cursor>%3D&page%5Bsize%5D=2",
                        "next": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bafter%5D=<after_cursor>%3D&page%5Bsize%5D=2",
                    },
                },
                {"page[after]": "<after_cursor>"},
            ),
            (
                    TicketSkips,
                    {
                        "meta": {"has_more": True, "after_cursor": "<after_cursor>", "before_cursor": "<before_cursor>"},
                        "links": {
                            "prev": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bbefore%5D=<before_cursor>%3D&page%5Bsize%5D=2",
                            "next": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bafter%5D=<after_cursor>%3D&page%5Bsize%5D=2",
                        },
                    },
                    {"page[after]": "<after_cursor>"},
            ),

        ],
        ids=[
            "GroupMemberships",
            "TicketForms",
            "TicketMetricEvents",
            "TicketAudits",
            "TicketMetrics",
            "SatisfactionRatings",
            "OrganizationMemberships",
            "TicketSkips",
        ],
    )
    def test_next_page_token(self, requests_mock, stream_cls, response, expected):
        stream = stream_cls(**STREAM_ARGS)
        # stream_name = snake_case(stream.__class__.__name__)
        requests_mock.get(STREAM_URL, json=response)
        test_response = requests.get(STREAM_URL)
        output = stream.next_page_token(test_response)
        assert output == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (GroupMemberships, 1622505600),
            (TicketForms, 1622505600),
            (TicketMetricEvents, 1622505600),
            (TicketAudits, 1622505600),
            (OrganizationMemberships, 1622505600),
            (TicketSkips, 1622505600),
        ],
        ids=[
            "GroupMemberships",
            "TicketForms",
            "TicketMetricEvents",
            "TicketAudits",
            "OrganizationMemberships",
            "TicketSkips"
        ],
    )
    def test_check_stream_state(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.check_stream_state()
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (GroupMemberships, {"sort_by": "asc", "start_time": 1622505600}),
            (TicketForms, {"start_time": 1622505600}),
            (TicketMetricEvents, {"start_time": 1622505600}),
            (TicketAudits, {"sort_by": "created_at", "sort_order": "desc", "limit": 1000}),
            (SatisfactionRatings, {"sort_by": "asc", "start_time": 1622505600}),
            (TicketMetrics, {"page[size]": 100, "start_time": 1622505600}),
            (OrganizationMemberships, {"page[size]": 100, "start_time": 1622505600}),
            (TicketSkips, {"page[size]": 100, "start_time": 1622505600}),
        ],
        ids=[
            "GroupMemberships",
            "TicketForms",
            "TicketMetricEvents",
            "TicketAudits",
            "SatisfactionRatings",
            "TicketMetrics",
            "OrganizationMemberships",
            "TicketSkips",
        ],
    )
    def test_request_params(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.request_params(stream_state=None, next_page_token=None)
        assert expected == result


class TestSourceZendeskIncrementalExportStream:
    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Users),
            (Tickets),
        ],
        ids=[
            "Users",
            "Tickets",
        ],
    )
    def test_check_start_time_param(self, stream_cls):
        expected = int(dict(parse_qsl(urlparse(STREAM_URL).query)).get("start_time"))
        stream = stream_cls(**STREAM_ARGS)
        result = stream.check_start_time_param(expected)
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Users, "incremental/users.json"),
            (Tickets, "incremental/tickets.json"),
        ],
        ids=[
            "Users",
            "Tickets",
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.path()
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (Users),
            (Tickets),
        ],
        ids=[
            "Users",
            "Tickets",
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
        "stream_cls, expected",
        [
            (Users, {"start_time": 1622505600}),
            (Tickets, {"start_time": 1622505600}),
        ],
        ids=[
            "Users",
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
            (Users),
            (Tickets),
        ],
        ids=[
            "Users",
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


class TestSourceZendeskSupportTicketEventsExportStream:
    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (TicketComments, True),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_update_event_from_record(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.update_event_from_record
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls",
        [
            (TicketComments),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_parse_response(self, requests_mock, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        stream_name = snake_case(stream.__class__.__name__)
        requests_mock.get(STREAM_URL, json={stream_name: []})
        test_response = requests.get(STREAM_URL)
        output = list(stream.parse_response(test_response))
        assert output == []

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (TicketComments, "created_at"),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_cursor_field(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.cursor_field
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (TicketComments, "ticket_events"),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_response_list_name(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.response_list_name
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (TicketComments, "child_events"),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_response_target_entity(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.response_target_entity
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (TicketComments, ["via_reference_id", "ticket_id", "timestamp"]),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_list_entities_from_event(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.list_entities_from_event
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (TicketComments, "Comment"),
        ],
        ids=[
            "TicketComments",
        ],
    )
    def test_event_type(self, stream_cls, expected):
        stream = stream_cls(**STREAM_ARGS)
        result = stream.event_type
        assert result == expected


def test_read_tickets_stream(requests_mock):
    requests_mock.get(
        "https://subdomain.zendesk.com/api/v2/incremental/tickets.json",
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
            ]
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


def test_read_post_comment_votes_stream(requests_mock):
    post_response = {
        "posts": [
            {"id": 7253375870607, "title": "Test_post", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}
        ]
    }
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts", json=post_response)

    post_comments_response = {
        "comments": [
            {"author_id": 89567, "body": "Test_comment for Test_post", "id": 35467, "post_id": 7253375870607}
        ]
    }
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts/7253375870607/comments", json=post_comments_response)

    votes = [{"id": 35467, "user_id": 888887, "value": -1}]
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts/7253375870607/comments/35467/votes",
                      json={"votes": votes})
    stream = PostCommentVotes(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    records = read_full_refresh(stream)
    assert records == votes
