#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import Status
from source_bamboo_hr.source import CustomReportsStream, EmployeesDirectoryStream, SourceBambooHr


@pytest.fixture
def config():
    return {"api_key": "foo", "subdomain": "bar", "authenticator": "baz", "custom_reports_include_default_fields": True}


def test_source_bamboo_hr_client_wrong_credentials():
    source = SourceBambooHr()
    result = source.check(logger=AirbyteLogger, config={"subdomain": "test", "api_key": "blah-blah"})
    assert result.status == Status.FAILED


@pytest.mark.parametrize(
    "custom_reports_fields,custom_reports_include_default_fields,available_fields,expected_message",
    [
        (
            "",
            False,
            {},
            "NullFieldsError('Field `custom_reports_fields` cannot be empty if `custom_reports_include_default_fields` is false.')",
        ),
        ("", True, {}, 'AvailableFieldsAccessDeniedError("You hasn\'t access to any report fields. Please check your access level.")'),
        (
            "Test",
            True,
            [{"name": "NewTest"}],
            "CustomFieldsAccessDeniedError('Access to fields: Test - denied. Please check your access level.')",
        ),
    ],
)
def test_check_failed(
    config, requests_mock, custom_reports_fields, custom_reports_include_default_fields, available_fields, expected_message
):
    config["custom_reports_fields"] = custom_reports_fields
    config["custom_reports_include_default_fields"] = custom_reports_include_default_fields
    requests_mock.get("https://api.bamboohr.com/api/gateway.php/bar/v1/meta/fields", json=available_fields)

    source = SourceBambooHr()
    result = source.check(logger=AirbyteLogger, config=config)

    assert result.status == Status.FAILED
    assert result.message == expected_message


def test_employees_directory_stream_url_base(config):
    stream = EmployeesDirectoryStream(config)
    assert stream.url_base == "https://api.bamboohr.com/api/gateway.php/bar/v1/"


def test_custom_reports_stream_get_json_schema_from_config(config):
    config["custom_reports_fields"] = "one,two , three"
    assert CustomReportsStream(config)._get_json_schema_from_config() == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "one": {"type": ["null", "string"]},
            "two": {"type": ["null", "string"]},
            "three": {"type": ["null", "string"]},
        },
    }


def test_custom_reports_stream_union_schemas():
    schema1 = {"properties": {"one": 1, "two": 2}}
    schema2 = {"properties": {"two": 2, "three": 3}}
    assert CustomReportsStream._union_schemas(schema1, schema2) == {"properties": {"one": 1, "two": 2, "three": 3}}


def test_custom_reports_stream_request_body_json(config):
    stream = CustomReportsStream(config)
    stream._schema = {"properties": {"one": 1, "two": 2}}
    assert stream.request_body_json() == {
        "title": "Airbyte",
        "fields": ["one", "two"],
    }
