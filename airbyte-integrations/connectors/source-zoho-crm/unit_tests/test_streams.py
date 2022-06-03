#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import Mock

import pytest
from source_zoho_crm.streams import ZohoCrmStream
from source_zoho_crm.types import FieldMeta, ModuleMeta


@pytest.fixture
def stream_factory(mocker):
    def wrapper(stream_module=None):
        class FullRefreshZohoStream(ZohoCrmStream):
            url_base = "https://dummy.com"
            module = stream_module

        return FullRefreshZohoStream()

    return wrapper


@pytest.mark.parametrize(("next_page_token", "expected_result"), (({"page": 2}, {"page": 2}), (None, {})))
def test_request_params(stream_factory, next_page_token, expected_result):
    stream = stream_factory()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": next_page_token}
    assert stream.request_params(**inputs) == expected_result


@pytest.mark.parametrize(
    ("status", "content", "expected_token"),
    ((200, b'{"data": [{"name": "Chris"}], "info": {"page": 1, "more_records": true}}', {"page": 2}), (204, b"", None)),
)
def test_next_page_token(response_mocker, stream_factory, status, content, expected_token):
    stream = stream_factory()
    response = response_mocker(status, content)
    inputs = {"response": response}
    assert stream.next_page_token(**inputs) == expected_token


@pytest.mark.parametrize(
    ("status", "content", "expected_obj"),
    ((204, b"", None), (200, b'{"data": [{"Name": "Abraham Lincoln"}]}', {"Name": "Abraham Lincoln"})),
)
def test_parse_response(stream_factory, response_mocker, status, content, expected_obj):
    stream = stream_factory()
    inputs = {"response": response_mocker(status, content)}
    assert next(stream.parse_response(**inputs), None) == expected_obj


def test_request_headers(stream_factory):
    stream = stream_factory()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(stream_factory):
    stream = stream_factory()
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(stream_factory, http_status, should_retry):
    response_mock = Mock()
    response_mock.status_code = http_status
    stream = stream_factory()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(stream_factory):
    response_mock = Mock()
    stream = stream_factory()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


def test_dynamic_attrs(stream_factory):
    field = FieldMeta(
        json_type="string",
        api_name="Name",
        data_type="text",
        system_mandatory=True,
        display_label="Name",
        length=None,
        decimal_place=None,
        pick_list_values=[],
    )
    stream = stream_factory(ModuleMeta(api_name="Leads", module_name="Leads", api_supported=True, fields=[field]))
    assert stream.path() == "/crm/v2/Leads"
    assert stream.get_json_schema() == {
        "additionalProperties": True,
        "description": "Leads",
        "properties": {
            "Modified_Time": {"format": "date-time", "type": "string"},
            "Name": {"maxLength": None, "title": "Name", "type": ["null", "string"]},
            "id": {"type": "string"},
        },
        "required": ["id", "Modified_Time", "Name"],
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
    }
