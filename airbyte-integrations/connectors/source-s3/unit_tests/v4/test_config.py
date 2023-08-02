
import logging

import pytest
from pydantic import ValidationError
from source_s3.v4.config import Config

logger = logging.Logger("")


@pytest.mark.parametrize(
    "kwargs,expected_error",
    [
        pytest.param({"bucket": "test", "streams": []}, None, id="required-fields"),
        pytest.param({"bucket": "test", "streams": [], "aws_access_key_id": "access_key", "aws_secret_access_key": "secret_access_key"}, None, id="config-created-with-aws-info"),
        pytest.param({"bucket": "test", "streams": [], "endpoint": "http://test.com"}, None, id="config-created-with-endpoint"),
        pytest.param({"bucket": "test", "streams": [], "aws_access_key_id": "access_key", "aws_secret_access_key": "secret_access_key", "endpoint": "http://test.com"}, ValidationError, id="cannot-have-endpoint-and-aws-info"),
        pytest.param({"streams": []}, ValidationError, id="missing-bucket"),
    ]
)
def test_config(kwargs, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            Config(**kwargs)
    else:
        Config(**kwargs)
