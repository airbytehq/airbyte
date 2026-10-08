# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Tests for a 401 on a stream request while using OAuth2.0 with refresh token.

Zendesk enforces the access-token lifetime the connector requests (48h). A request that is
already in flight when the token expires is answered with 401 `invalid_token`, even though the
connector's stored `token_expiry_date` still says the token is valid. With the 401 response
filter mapped to `REFRESH_TOKEN_THEN_RETRY`, the CDK refreshes the token once and retries that
request with the new token instead of failing the whole sync.
"""

from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import OAuthBearerAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import TagsRecordBuilder, TagsResponseBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_SUBDOMAIN = "d3v-airbyte"
_OAUTH_TOKEN_URL = f"https://{_SUBDOMAIN}.zendesk.com/oauth/tokens"

_CLIENT_ID = "test_client_id"
_CLIENT_SECRET = "test_client_secret"
_INITIAL_REFRESH_TOKEN = "initial_refresh_token_rt1"
_ROTATED_REFRESH_TOKEN = "rotated_refresh_token_rt2"
# Valid according to the stored expiry date, but already rejected by Zendesk.
_STALE_ACCESS_TOKEN = "access_token_valid_locally_but_rejected_by_zendesk"
_NEW_ACCESS_TOKEN = "new_access_token_after_forced_refresh"

_UNAUTHORIZED_BODY = (
    '{"error": "invalid_token", "error_description": '
    '"The access token provided is expired, revoked, malformed or invalid for other reasons."}'
)


def _config_with_locally_valid_token() -> dict:
    return (
        ConfigBuilder()
        .with_subdomain(_SUBDOMAIN)
        .with_start_date(_START_DATE)
        .with_oauth_refresh_credentials(
            client_id=_CLIENT_ID,
            client_secret=_CLIENT_SECRET,
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_STALE_ACCESS_TOKEN,
            token_expiry_date=(_NOW + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        .build()
    )


def _token_response(access_token: str, refresh_token: str, expires_in: int = 172800) -> str:
    return (
        f'{{"access_token": "{access_token}", "refresh_token": "{refresh_token}", '
        f'"token_type": "bearer", "expires_in": {expires_in}}}'
    )


def _tags_request(access_token: str):
    return ZendeskSupportRequestBuilder.tags_endpoint(OAuthBearerAuthenticator(access_token)).with_page_size(100).build()


class TestUnauthorizedRefreshesTokenThenRetries(TestCase):
    @HttpMocker()
    def test_given_401_on_locally_valid_token_when_read_then_refresh_once_and_retry_with_new_token(self, http_mocker):
        """
        The stored expiry date is in the future, so no proactive refresh happens. The first request is
        rejected with 401. The connector must refresh the token exactly once, retry the same request with
        the new token, and sync the data.
        """
        config = _config_with_locally_valid_token()

        # Registered on requests_mock directly: the CDK posts the refresh as form data, which the
        # HttpMocker body matcher can't match (same approach as test_oauth_refresh_flow.py).
        token_endpoint = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_token_response(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )
        http_mocker.get(_tags_request(_STALE_ACCESS_TOKEN), HttpResponse(body=_UNAUTHORIZED_BODY, status_code=401))
        http_mocker.get(
            _tags_request(_NEW_ACCESS_TOKEN),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        with patch("time.sleep"):
            output = read_stream("tags", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        assert token_endpoint.call_count == 1
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_401_again_after_refresh_when_read_then_fail_without_second_refresh(self, http_mocker):
        """
        If the freshly refreshed token is rejected too, the credentials are broken. The connector must
        fail with a config error and must not refresh again (no retry loop against the token endpoint).
        """
        config = _config_with_locally_valid_token()

        token_endpoint = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_token_response(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )
        http_mocker.get(_tags_request(_STALE_ACCESS_TOKEN), HttpResponse(body=_UNAUTHORIZED_BODY, status_code=401))
        http_mocker.get(_tags_request(_NEW_ACCESS_TOKEN), HttpResponse(body=_UNAUTHORIZED_BODY, status_code=401))

        with patch("time.sleep"):
            output = read_stream("tags", SyncMode.full_refresh, config, expecting_exception=True)

        assert len(output.records) == 0
        assert token_endpoint.call_count == 1
        assert output.errors
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
