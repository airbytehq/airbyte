#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from unittest.mock import Mock

import pytest
from pydantic.v1.error_wrappers import ValidationError
from source_s3.v4 import Config, SourceS3, SourceS3StreamReader

from airbyte_cdk import AirbyteTracedException, FailureType
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError


logger = logging.Logger("")


@pytest.mark.parametrize(
    "kwargs, is_cloud, expected_error",
    [
        pytest.param({"bucket": "test", "streams": []}, False, None, id="required-fields"),
        pytest.param(
            {"bucket": "test", "streams": [], "aws_access_key_id": "access_key", "aws_secret_access_key": "secret_access_key"},
            True,
            None,
            id="config-created-with-aws-info",
        ),
        pytest.param({"bucket": "test", "streams": [], "endpoint": "https://test.com"}, False, None, id="config-created-with-endpoint"),
        pytest.param(
            {"bucket": "test", "streams": [], "endpoint": "HTTPS://test.com"},
            True,
            None,
            id="uppercase-https-cloud-endpoint",
        ),
        pytest.param(
            {"bucket": "test", "streams": [], "endpoint": "HtTpS://test.com"},
            True,
            None,
            id="mixed-case-https-cloud-endpoint",
        ),
        pytest.param(
            {"bucket": "test", "streams": [], "endpoint": "http://test.com"},
            True,
            ConfigValidationError,
            id="http-endpoint-error",
        ),
        pytest.param(
            {"bucket": "test", "streams": [], "endpoint": "HTTP://test.com"},
            True,
            ConfigValidationError,
            id="uppercase-http-endpoint-error",
        ),
        pytest.param({"bucket": "test", "streams": [], "endpoint": "http://test.com"}, False, None, id="http-endpoint-error"),
        pytest.param(
            {"bucket": "test", "streams": [], "endpoint": "test.com"},
            True,
            ConfigValidationError,
            id="scheme-less-cloud-endpoint-error",
        ),
        pytest.param(
            {"bucket": "test", "streams": [], "endpoint": "test.com"},
            False,
            ConfigValidationError,
            id="scheme-less-oss-endpoint-error",
        ),
        pytest.param(
            {
                "bucket": "test",
                "streams": [],
                "aws_access_key_id": "access_key",
                "aws_secret_access_key": "secret_access_key",
                "endpoint": "https://test.com",
            },
            True,
            None,
            id="config-created-with-endpoint-and-aws-info",
        ),
        pytest.param({"streams": []}, False, ValidationError, id="missing-bucket"),
    ],
)
def test_config(mocker, kwargs, is_cloud, expected_error):
    mocker.patch("source_s3.v4.config.is_cloud_environment", lambda: is_cloud)

    if expected_error:
        with pytest.raises(expected_error):
            Config(**kwargs)
    else:
        Config(**kwargs)


def test_scheme_less_cloud_endpoint_has_classified_error(mocker):
    mocker.patch("source_s3.v4.config.is_cloud_environment", lambda: True)

    with pytest.raises(ConfigValidationError) as exc_info:
        Config(bucket="test", streams=[], endpoint="test.com")

    assert str(exc_info.value).startswith('Field "Endpoint" must be a full URL starting with "https://".')


def test_scheme_less_endpoint_has_user_visible_config_error(mocker):
    mocker.patch("source_s3.v4.config.is_cloud_environment", lambda: False)
    source = SourceS3(Mock(spec=SourceS3StreamReader), Config, None, None, None)

    with pytest.raises(AirbyteTracedException) as exc_info:
        source.check_connection(logger, {"bucket": "test", "streams": [], "endpoint": "test.com"})

    assert 'Field "Endpoint" must be a full URL starting with "http://" or "https://".' in exc_info.value.message
    assert exc_info.value.failure_type == FailureType.config_error
