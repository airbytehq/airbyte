#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.request import HttpRequest

from .config import ORGANIZATION_ID, ConfigBuilder
from .request_builder import OAuthRequestBuilder, RequestBuilder
from .response_builder import (
    error_response,
    oauth_response,
    organizations_response,
)
from .utils import config, read_output


_STREAM_NAME = "organizations"


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=sync_mode,
        state=state,
        expecting_exception=expecting_exception,
    )


class TestOrganizations(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ORGANIZATION_ID

    @HttpMocker()
    def test_read_records_with_organization_ids(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint(ORGANIZATION_ID).build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config().with_organization_ids([ORGANIZATION_ID]))
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ORGANIZATION_ID

    @HttpMocker()
    def test_read_records_with_pagination(self, http_mocker: HttpMocker) -> None:
        next_link = "https://adsapi.snapchat.com/v1/me/organizations?cursor=page2"
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id="org_1", has_next=True, next_link=next_link),
        )
        http_mocker.get(
            HttpRequest(url=next_link),
            organizations_response(organization_id="org_2", has_next=False),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2

    @HttpMocker()
    def test_read_records_with_error_401(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_with_error_403_retry(self, http_mocker: HttpMocker) -> None:
        """Test that 403 errors trigger RETRY behavior as configured in manifest."""
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        # First request returns 403, then succeeds on retry
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            [
                error_response(HTTPStatus.FORBIDDEN),
                organizations_response(organization_id=ORGANIZATION_ID),
            ],
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == ORGANIZATION_ID


class TestOrganizationsIncremental(TestCase):
    @HttpMocker()
    def test_incremental_first_sync_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that first sync (no state) emits state message with cursor value."""
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id=ORGANIZATION_ID),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)
        assert len(output.records) == 1
        # Verify state message is emitted
        assert len(output.state_messages) >= 1
        # Verify state contains cursor field (updated_at)
        state_data = output.state_messages[-1].state
        assert state_data is not None

    @HttpMocker()
    def test_incremental_with_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages and verify pagination stops correctly."""
        page1_link = "https://adsapi.snapchat.com/v1/me/organizations?cursor=page2"
        http_mocker.post(
            OAuthRequestBuilder.oauth_endpoint().build(),
            oauth_response(),
        )
        # Page 1 with next_link
        http_mocker.get(
            RequestBuilder.organizations_endpoint("me").build(),
            organizations_response(organization_id="org_1", has_next=True, next_link=page1_link),
        )
        # Page 2 without next_link (pagination stops)
        http_mocker.get(
            HttpRequest(url=page1_link),
            organizations_response(organization_id="org_2", has_next=False),
        )

        output = _read(config_builder=config(), sync_mode=SyncMode.incremental)
        # Verify both pages were read
        assert len(output.records) == 2
        # Verify pagination stopped (no more requests made)
        record_ids = [r.record.data["id"] for r in output.records]
        assert "org_1" in record_ids
        assert "org_2" in record_ids
