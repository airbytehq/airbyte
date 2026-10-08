# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
A 401 with API-token authentication must keep failing fast as a config error.

The REFRESH_TOKEN_THEN_RETRY filter only makes sense for OAuth2.0 with refresh token. With an API
token there is nothing to refresh, so a 401 means the credentials are wrong: the connector must not
retry and must not call the OAuth token endpoint.
"""

from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ZendeskSupportRequestBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_SUBDOMAIN = "d3v-airbyte"
_OAUTH_TOKEN_URL = f"https://{_SUBDOMAIN}.zendesk.com/oauth/tokens"
_UNAUTHORIZED_BODY = '{"error": "Couldn\'t authenticate you"}'


class TestUnauthorizedWithApiToken(TestCase):
    @HttpMocker()
    def test_given_401_with_api_token_when_read_then_fail_fast_without_token_refresh(self, http_mocker):
        config = (
            ConfigBuilder()
            .with_subdomain(_SUBDOMAIN)
            .with_start_date(_START_DATE)
            .with_basic_auth_credentials("user@example.com", "wrong_api_token")
            .build()
        )

        token_endpoint = http_mocker._mocker.post(_OAUTH_TOKEN_URL, text="{}", status_code=200)
        # No authenticator on the expected request: the header set is empty, so it matches whatever
        # Authorization header the connector sends.
        tags_request = ZendeskSupportRequestBuilder(_SUBDOMAIN, "tags").with_page_size(100).build()
        http_mocker.get(tags_request, HttpResponse(body=_UNAUTHORIZED_BODY, status_code=401))

        with patch("time.sleep"):
            output = read_stream("tags", SyncMode.full_refresh, config, expecting_exception=True)

        assert len(output.records) == 0
        assert token_endpoint.call_count == 0
        http_mocker.assert_number_of_calls(tags_request, 1)
        assert output.errors
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
