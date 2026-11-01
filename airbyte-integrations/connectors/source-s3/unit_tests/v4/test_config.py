#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

import pytest
from pydantic.v1.error_wrappers import ValidationError
from source_s3.v4.config import SECTIONS, Config


logger = logging.Logger("")

DEFAULT_CREDENTIALS = {"auth_type": "default_credentials"}
IAM_USER_CREDENTIALS = {
    "auth_type": "iam_user",
    "aws_access_key_id": "access_key",
    "aws_secret_access_key": "secret_access_key",
}


@pytest.mark.parametrize(
    "kwargs, is_cloud, expected_error",
    [
        pytest.param({"bucket": "test", "credentials": DEFAULT_CREDENTIALS, "streams": []}, False, None, id="required-fields"),
        pytest.param(
            {"bucket": "test", "credentials": IAM_USER_CREDENTIALS, "streams": []},
            True,
            None,
            id="config-created-with-aws-info",
        ),
        pytest.param(
            {"bucket": "test", "credentials": DEFAULT_CREDENTIALS, "streams": [], "endpoint": "https://test.com"},
            False,
            None,
            id="config-created-with-endpoint",
        ),
        pytest.param(
            {"bucket": "test", "credentials": DEFAULT_CREDENTIALS, "streams": [], "endpoint": "http://test.com"},
            True,
            ValidationError,
            id="http-endpoint-error",
        ),
        pytest.param(
            {"bucket": "test", "credentials": DEFAULT_CREDENTIALS, "streams": [], "endpoint": "http://test.com"},
            False,
            None,
            id="http-endpoint-error",
        ),
        pytest.param(
            {
                "bucket": "test",
                "credentials": IAM_USER_CREDENTIALS,
                "streams": [],
                "endpoint": "https://test.com",
            },
            True,
            None,
            id="config-created-with-endpoint-and-aws-info",
        ),
        pytest.param({"streams": []}, False, ValidationError, id="missing-bucket"),
        pytest.param({"bucket": "test", "streams": []}, False, ValidationError, id="missing-credentials"),
    ],
)
def test_config(mocker, kwargs, is_cloud, expected_error):
    mocker.patch("source_s3.v4.config.is_cloud_environment", lambda: is_cloud)

    if expected_error:
        with pytest.raises(expected_error):
            Config(**kwargs)
    else:
        Config(**kwargs)


@pytest.mark.parametrize(
    "config, expected",
    [
        pytest.param(
            {"aws_access_key_id": "access_key", "aws_secret_access_key": "secret_access_key"},
            {"credentials": IAM_USER_CREDENTIALS},
            id="iam-user",
        ),
        pytest.param(
            {"role_arn": "arn:aws:iam::123456789012:role/my-role"},
            {"credentials": {"auth_type": "iam_role", "role_arn": "arn:aws:iam::123456789012:role/my-role"}},
            id="iam-role",
        ),
        pytest.param(
            {
                "role_arn": "arn:aws:iam::123456789012:role/my-role",
                "aws_access_key_id": "access_key",
                "aws_secret_access_key": "secret_access_key",
            },
            {"credentials": {"auth_type": "iam_role", "role_arn": "arn:aws:iam::123456789012:role/my-role"}},
            id="role-takes-precedence",
        ),
        pytest.param({}, {"credentials": DEFAULT_CREDENTIALS}, id="no-credentials"),
        pytest.param(
            {"aws_access_key_id": "access_key"},
            {"credentials": {"auth_type": "iam_user", "aws_access_key_id": "access_key"}},
            id="partial-iam-user",
        ),
    ],
)
def test_migrate_legacy_credentials(config, expected):
    original_config = config.copy()

    migrated = Config.migrate_legacy_credentials(config)

    assert migrated == expected
    assert config == original_config


def test_migrate_legacy_credentials_returns_none_for_already_migrated_config():
    config = {"credentials": DEFAULT_CREDENTIALS}

    assert Config.migrate_legacy_credentials(config) is None
    assert config == {"credentials": DEFAULT_CREDENTIALS}


def test_config_schema_orders_bucket_auth_streams_and_stream_fields():
    schema = Config.schema()
    properties = schema["properties"]
    stream_properties = properties["streams"]["items"]["properties"]

    assert "credentials" in schema["required"]
    assert properties["bucket"]["order"] == 0
    assert properties["credentials"]["order"] == 1
    assert properties["endpoint"]["order"] == 2
    assert properties["region_name"]["order"] == 3
    assert properties["delivery_method"]["order"] == 4
    assert properties["streams"]["title"] == "Streams"
    assert properties["streams"]["order"] == 5
    assert properties["start_date"]["order"] == 6
    assert stream_properties["name"]["order"] == 0
    assert stream_properties["format"]["order"] == 1
    assert not {"aws_access_key_id", "aws_secret_access_key", "role_arn"} & properties.keys()
    credential_options = properties["credentials"]["oneOf"]
    assert {option["properties"]["auth_type"]["const"] for option in credential_options} == {
        "iam_user",
        "iam_role",
        "default_credentials",
    }
    assert all(option["required"].count("auth_type") == 1 for option in credential_options)


def test_config_schema_declares_groups_and_sections():
    schema = Config.schema()
    properties = schema["properties"]

    assert [group["id"] for group in schema["groups"]] == ["bucket", "endpoint", "files", "start_date"]
    assert schema["sections"] == SECTIONS
    assert [section["id"] for section in schema["sections"]] == ["bucket", "files", "review"]
    assert [section["order"] for section in schema["sections"]] == [0, 1, 2]
    # The bucket and files sections are checked when completed; the review section is covered by the full check.
    assert [section.get("check") for section in schema["sections"]] == [True, True, None]
    # Every section group is declared, and every visible property belongs to a group of some section.
    declared_groups = {group["id"] for group in schema["groups"]}
    section_groups = {group for section in schema["sections"] for group in section["groups"]}
    assert section_groups <= declared_groups
    assert {name: prop["group"] for name, prop in properties.items()} == {
        "bucket": "bucket",
        "credentials": "bucket",
        "endpoint": "endpoint",
        "region_name": "endpoint",
        "delivery_method": "files",
        "streams": "files",
        "start_date": "start_date",
    }
    assert all(group in section_groups for group in {prop["group"] for prop in properties.values()})
