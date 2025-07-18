#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging

import pytest
from pydantic.v1.error_wrappers import ValidationError
from source_s3.v4.config import Config


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
        pytest.param({"bucket": "test", "streams": [], "endpoint": "http://test.com"}, True, ValidationError, id="http-endpoint-error"),
        pytest.param({"bucket": "test", "streams": [], "endpoint": "http://test.com"}, False, None, id="http-endpoint-error"),
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
