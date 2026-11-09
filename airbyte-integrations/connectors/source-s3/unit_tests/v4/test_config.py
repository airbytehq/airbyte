#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

import pytest
from pydantic.v1.error_wrappers import ValidationError
from source_s3.v4.config import Config


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


def test_config_schema_orders_auth_bucket_streams_and_stream_fields():
    schema = Config.schema()
    properties = schema["properties"]
    stream_properties = properties["streams"]["items"]["properties"]

    assert "credentials" in schema["required"]
    assert properties["credentials"]["order"] == 0
    assert properties["bucket"]["order"] == 1
    assert properties["start_date"]["order"] == 3
    assert properties["streams"]["title"] == "Streams"
    assert properties["streams"]["order"] == 2
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
