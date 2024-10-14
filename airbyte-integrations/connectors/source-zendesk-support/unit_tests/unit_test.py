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
    AccountAttributes,
    ArticleComments,
    ArticleCommentVotes,
    Articles,
    ArticleVotes,
    AttributeDefinitions,
    AuditLogs,
    BaseZendeskSupportStream,
    Brands,
    CustomRoles,
    GroupMemberships,
    Groups,
    Macros,
    OrganizationMemberships,
    Organizations,
    PostCommentVotes,
    Posts,
    PostVotes,
    SatisfactionRatings,
    Schedules,
    SlaPolicies,
    SourceZendeskIncrementalExportStream,
    StatefulTicketMetrics,
    StatelessTicketMetrics,
    Tags,
    TicketAudits,
    TicketComments,
    TicketFields,
    TicketForms,
    TicketMetricEvents,
    TicketMetrics,
    TicketMetricsStateMigration,
    Tickets,
    TicketSkips,
    Topics,
    UserFields,
    Users,
    UserSettingsStream,
)
from test_data.data import TICKET_EVENTS_STREAM_RESPONSE
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


class TestAllStreams:
    def test_ticket_forms_exception_stream(self):
        with patch.object(TicketForms, "read_records", return_value=[{}]) as mocked_records:
            mocked_records.side_effect = Exception("The error")
            streams = SourceZendeskSupport().streams(TEST_CONFIG)
            assert not any([isinstance(stream, TicketForms) for stream in streams])

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (AuditLogs, "audit_logs"),
            (GroupMemberships, "group_memberships"),
            (Groups, "groups"),
            (Macros, "macros"),
            (Organizations, "incremental/organizations.json"),
            (Posts, "community/posts"),
            (OrganizationMemberships, "organization_memberships"),
            (SatisfactionRatings, "satisfaction_ratings"),
            (SlaPolicies, "slas/policies.json"),
            (Tags, "tags"),
            (TicketAudits, "ticket_audits"),
            (TicketComments, "incremental/ticket_events.json"),
            (TicketFields, "ticket_fields"),
            (TicketForms, "ticket_forms"),
            (StatefulTicketMetrics, "tickets/13/metrics"),
            (StatelessTicketMetrics, "ticket_metrics"),
            (TicketSkips, "skips.json"),
            (TicketMetricEvents, "incremental/ticket_metric_events"),
            (Tickets, "incremental/tickets/cursor.json"),
            (Users, "incremental/users/cursor.json"),
            (Topics, "community/topics"),
            (Brands, "brands"),
            (CustomRoles, "custom_roles"),
            (Schedules, "business_hours/schedules.json"),
            (AccountAttributes, "routing/attributes"),
            (AttributeDefinitions, "routing/attributes/definitions"),
            (UserFields, "user_fields"),
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
            "StatefulTicketMetrics",
            "StatelessTicketMetrics",
            "TicketSkips",
            "TicketMetricEvents",
            "Tickets",
            "Topics",
            "Users",
            "Brands",
            "CustomRoles",
            "Schedules",
            "AccountAttributes",
            "AttributeDefinitions",
            "UserFields",
        ],
    )
    def test_path(self, stream_cls, expected):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
        result = stream.path(stream_slice={"ticket_id": "13"})
        assert result == expected


class TestSourceZendeskSupportStream:
    @pytest.mark.parametrize(
        "stream_cls",
        [(Macros), (Posts), (Groups), (SatisfactionRatings), (TicketFields), (Topics)],
        ids=["Macros", "Posts", "Groups", "SatisfactionRatings", "TicketFields", "Topics"],
    )
    def test_parse_response(self, requests_mock, stream_cls):
        stream = stream_cls(**STREAM_ARGS)
        expected = [{"updated_at": "2022-03-17T16:03:07Z"}]
        response_field = stream.name

        requests_mock.get(STREAM_URL, json={response_field: expected})
        test_response = requests.get(STREAM_URL)

        output = list(stream.parse_response(test_response, None))

        expected = expected if isinstance(expected, list) else [expected]
        assert expected == output

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

    def test_attribute_definition_parse_response(self, requests_mock):
        stream = AttributeDefinitions(**STREAM_ARGS)
        conditions_all = {"subject": "number_of_incidents", "title": "Number of incidents"}
        conditions_any = {"subject": "brand", "title": "Brand"}
        response_json = {"definitions": {"conditions_all": [conditions_all], "conditions_any": [conditions_any]}}
        requests_mock.get(STREAM_URL, json=response_json)
        test_response = requests.get(STREAM_URL)
        output = list(stream.parse_response(test_response, None))
        expected_records = [
            {"condition": "all", "subject": "number_of_incidents", "title": "Number of incidents"},
            {"condition": "any", "subject": "brand", "title": "Brand"},
        ]
        assert expected_records == output

    @pytest.mark.parametrize(
        "stream_cls",
        [(Macros), (Organizations), (Posts), (Groups), (SatisfactionRatings), (TicketFields), (StatefulTicketMetrics), (Topics)],
        ids=["Macros", "Organizations", "Posts", "Groups", "SatisfactionRatings", "TicketFields", "StatefulTicketMetrics", "Topics"],
    )
    def test_url_base(self, stream_cls):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
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
            (Topics, {}, {"updated_at": "2022-03-17T16:03:07Z"}, {"updated_at": "2022-03-17T16:03:07Z"}),
        ],
        ids=["Macros", "Posts", "Organizations", "Groups", "SatisfactionRatings", "TicketFields", "Topics"],
    )
    def test_get_updated_state(self, stream_cls, current_state, last_record, expected):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
        result = stream.get_updated_state(current_state, last_record)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Macros, None),
            (Posts, None),
            (Organizations, {}),
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
            (Organizations, {"start_time": 1622505600}),
            (Groups, {"start_time": 1622505600}),
            (TicketFields, {"start_time": 1622505600}),
        ],
        ids=[
            "Macros",
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
        [(Tags), (SlaPolicies), (Brands), (CustomRoles), (Schedules), (UserSettingsStream), (AccountAttributes), (AttributeDefinitions)],
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
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
        result = stream.get_updated_state(current_state, last_record)
        assert expected == result

    @pytest.mark.parametrize(
        "stream_cls, response, expected",
        [
            (GroupMemberships, {}, None),
            (TicketForms, {}, None),
            (
                TicketMetricEvents,
                {
                    "meta": {"has_more": True, "after_cursor": "<after_cursor>", "before_cursor": "<before_cursor>"},
                    "links": {
                        "prev": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bbefore%5D=<before_cursor>%3D&page%5Bsize%5D=2",
                        "next": "https://subdomain.zendesk.com/api/v2/ticket_metrics.json?page%5Bafter%5D=<after_cursor>%3D&page%5Bsize%5D=2",
                    },
                },
                {"page[after]": "<after_cursor>"},
            ),
            (TicketAudits, {}, None),
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
            "SatisfactionRatings",
            "OrganizationMemberships",
            "TicketSkips",
        ],
    )
    def test_next_page_token(self, requests_mock, stream_cls, response, expected):
        stream = stream_cls(**STREAM_ARGS)
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
        ids=["GroupMemberships", "TicketForms", "TicketMetricEvents", "TicketAudits", "OrganizationMemberships", "TicketSkips"],
    )
    def test_check_stream_state(self, stream_cls, expected):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
        result = stream.get_stream_state_value()
        assert result == expected

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (GroupMemberships, {"page[size]": 100, "sort_by": "asc", "start_time": 1622505600}),
            (TicketForms, {"start_time": 1622505600}),
            (TicketMetricEvents, {"page[size]": 100, "start_time": 1622505600}),
            (TicketAudits, {"sort_by": "created_at", "sort_order": "desc", "limit": 200}),
            (SatisfactionRatings, {"page[size]": 100, "sort_by": "created_at", "start_time": 1622505600}),
            (OrganizationMemberships, {"page[size]": 100, "start_time": 1622505600}),
            (TicketSkips, {"page[size]": 100, "start_time": 1622505600}),
        ],
        ids=[
            "GroupMemberships",
            "TicketForms",
            "TicketMetricEvents",
            "TicketAudits",
            "SatisfactionRatings",
            "OrganizationMemberships",
            "TicketSkips",
        ],
    )
    def test_request_params(self, stream_cls, expected):
        stream = get_stream_instance(stream_cls, STREAM_ARGS)
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
        result = stream.validate_start_time(expected)
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
        assert output == {}

    @pytest.mark.parametrize(
        "stream_cls, expected",
        [
            (Users, {"start_time": 1622505600}),
            (Tickets, {"start_time": 1622505600}),
            (Articles, {"sort_by": "updated_at", "sort_order": "asc", "start_time": 1622505600}),
        ],
        ids=[
            "Users",
            "Tickets",
            "Articles",
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

    @pytest.mark.parametrize(
        "stream_cls, stream_slice, expected_path",
        [
            (ArticleVotes, {"parent": {"id": 1}}, "help_center/articles/1/votes"),
            (ArticleComments, {"parent": {"id": 1}}, "help_center/articles/1/comments"),
            (ArticleCommentVotes, {"parent": {"id": 1, "source_id": 1}}, "help_center/articles/1/comments/1/votes"),
        ],
        ids=[
            "ArticleVotes_path",
            "ArticleComments_path",
            "ArticleCommentVotes_path",
        ],
    )
    def test_path(self, stream_cls, stream_slice, expected_path):
        stream = stream_cls(**STREAM_ARGS)
        assert stream.path(stream_slice=stream_slice) == expected_path


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


def test_read_post_votes_stream(requests_mock):
    post_response = {
        "posts": [{"id": 7253375870607, "title": "Test_post", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}]
    }
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts", json=post_response)

    post_votes_response = {
        "votes": [
            {
                "author_id": 89567,
                "body": "Test_comment for Test_post",
                "id": 35467,
                "post_id": 7253375870607,
                "updated_at": "2023-01-02T00:00:00Z",
            }
        ]
    }
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts/7253375870607/votes", json=post_votes_response)

    stream = PostVotes(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    records = read_full_refresh(stream)
    assert records == post_votes_response.get("votes")


def test_read_post_comment_votes_stream(requests_mock):
    post_response = {
        "posts": [{"id": 7253375870607, "title": "Test_post", "created_at": "2023-01-01T00:00:00Z", "updated_at": "2023-01-01T00:00:00Z"}]
    }
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts", json=post_response)

    post_comments_response = {
        "comments": [
            {
                "author_id": 89567,
                "body": "Test_comment for Test_post",
                "id": 35467,
                "post_id": 7253375870607,
                "updated_at": "2023-01-02T00:00:00Z",
            }
        ]
    }
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts/7253375870607/comments", json=post_comments_response)

    votes = [{"id": 35467, "user_id": 888887, "value": -1, "updated_at": "2023-01-03T00:00:00Z"}]
    requests_mock.get("https://subdomain.zendesk.com/api/v2/community/posts/7253375870607/comments/35467/votes", json={"votes": votes})
    stream = PostCommentVotes(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    records = read_full_refresh(stream)
    assert records == votes


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
    request_history = requests_mock.get(
        "https://subdomain.zendesk.com/api/v2/incremental/ticket_metric_events",
        [{"json": first_page_response}, {"json": second_page_response}],
    )
    stream = TicketMetricEvents(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    read_full_refresh(stream)
    assert request_history.call_count == 2
    assert request_history.last_request.qs == {"page[after]": ["<after_cursor>"], "page[size]": ["100"], "start_time": ["1577836800"]}


@pytest.mark.parametrize("status_code", [(403), (404)])
def test_read_tickets_comment(requests_mock, status_code):
    request_history = requests_mock.get(
        "https://subdomain.zendesk.com/api/v2/incremental/ticket_events.json", status_code=status_code, json={"error": "wrong permissions"}
    )
    stream = TicketComments(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    read_full_refresh(stream)
    assert request_history.call_count == 1


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


def test_read_ticket_audits_504_error(requests_mock, caplog):
    requests_mock.get("https://subdomain.zendesk.com/api/v2/ticket_audits", status_code=504, text="upstream request timeout")
    stream = TicketAudits(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    expected_message = "Skipping stream `ticket_audits`. Timed out waiting for response: upstream request timeout..."
    read_full_refresh(stream)
    assert expected_message in (record.message for record in caplog.records if record.levelname == "ERROR")


@pytest.mark.parametrize(
    "start_date, stream_state, audits_response, expected",
    [
        ("2020-01-01T00:00:00Z", {}, [{"created_at": "2020-01-01T00:00:00Z"}], True),
        ("2020-01-01T00:00:00Z", {}, [{"created_at": "1990-01-01T00:00:00Z"}], False),
        ("2020-01-01T00:00:00Z", {"created_at": "2021-01-01T00:00:00Z"}, [{"created_at": "2022-01-01T00:00:00Z"}], True),
        ("2020-01-01T00:00:00Z", {"created_at": "2021-01-01T00:00:00Z"}, [{"created_at": "1990-01-01T00:00:00Z"}], False),
    ],
)
def test_validate_response_ticket_audits(start_date, stream_state, audits_response, expected):
    stream = TicketAudits(subdomain="subdomain", start_date=start_date)
    response_mock = Mock()
    response_mock.json.return_value = {"audits": audits_response}
    assert stream._validate_response(response_mock, stream_state) == expected


@pytest.mark.parametrize(
    "audits_response, expected",
    [
        ({"no_audits": []}, False),
        ({}, False),
    ],
)
def test_validate_response_ticket_audits_handle_empty_response(audits_response, expected):
    stream = TicketAudits(subdomain="subdomain", start_date="2020-01-01T00:00:00Z")
    response_mock = Mock()
    response_mock.json.return_value = audits_response
    assert stream._validate_response(response_mock, {}) == expected


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
