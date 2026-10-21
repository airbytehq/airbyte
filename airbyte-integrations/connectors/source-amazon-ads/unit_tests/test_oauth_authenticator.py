# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from importlib.metadata import version

import pytest

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.integrations.ad_requests import OAuthRequestBuilder
from unit_tests.integrations.config import ConfigBuilder
from unit_tests.integrations.utils import read_stream


# The connector runs on CDK 7.x (the source-declarative-manifest base image), but unit_tests/poetry.lock
# still pins CDK 6.x, which ignores refresh_token_error_* on OAuthAuthenticator. Remove this guard once
# the test dependencies are on CDK 7.
pytestmark = pytest.mark.skipif(
    int(version("airbyte-cdk").split(".")[0]) < 7,
    reason="refresh_token_error_* on OAuthAuthenticator needs the CDK 7 runtime",
)


@pytest.mark.parametrize(
    "status_code, error",
    [
        pytest.param(400, "invalid_grant", id="400_invalid_grant"),
        pytest.param(401, "invalid_grant", id="401_invalid_grant"),
        pytest.param(400, "invalid_permissions", id="400_invalid_permissions"),
    ],
)
def test_rejected_refresh_token_is_config_error(status_code: int, error: str) -> None:
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint(
                client_id=config["client_id"], client_secred=config["client_secret"], refresh_token=config["refresh_token"]
            ).build(),
            HttpResponse(body=json.dumps({"error": error, "error_description": "refresh token rejected"}), status_code=status_code),
        )

        output = read_stream("profiles", SyncMode.full_refresh, config, expecting_exception=True)

    assert output.errors
    assert all(message.trace.error.failure_type == FailureType.config_error for message in output.errors)
