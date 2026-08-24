# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from unit_tests.conftest import get_source

from .config import ConfigBuilder
from .request_builder import LinkedInAdsRequestBuilder
from .response_builder import LinkedInAdsOffsetPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "organizations"
_PAGE_SIZE = 500

# Exact wording LinkedInAdsErrorHandler._is_data_volume_rate_limit looks for: both
# "data request limit has been exceeded" and "45 million metric values" must be present.
_DATA_VOLUME_RATE_LIMIT_BODY = json.dumps(
    {
        "message": (
            "Your data request limit has been exceeded. You have requested more than 45 million metric values in the last 24 hours."
        ),
        "status": 429,
    }
)


def _create_organization_acl_record(
    organization_id: int,
    role: str = "ADMINISTRATOR",
    role_assignee: str = "urn:li:person:abc",
    state: str = "APPROVED",
) -> dict:
    return {
        "role": role,
        "organization": f"urn:li:organization:{organization_id}",
        "roleAssignee": role_assignee,
        "state": state,
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestOrganizationsStream(TestCase):
    """
    Tests for the LinkedIn Ads 'organizations' stream.

    It reads the Rest.li /organizationAcls finder and uses:
    - request_parameters q=roleAssignee and count=500
    - OffsetIncrement pagination injected as the `start` request parameter
    - CustomRecordExtractor (LinkedInAdsRecordExtractor)
    - CustomErrorHandler (LinkedInAdsErrorHandler)
    - AddFields normalizing `organizationTarget` into `organization`
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of organization ACLs.

        Given: A configured LinkedIn Ads connector
        When: Running a full refresh sync for the organizations stream
        Then: The connector should request q=roleAssignee with count=500 and return all records
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.organizations_endpoint().with_q("roleAssignee").with_count(_PAGE_SIZE).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                [_create_organization_acl_record(123, role="ADMINISTRATOR", role_assignee="urn:li:person:abc")],
                total=1,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["organization"] == "urn:li:organization:123"
        assert record["role"] == "ADMINISTRATOR"
        assert record["roleAssignee"] == "urn:li:person:abc"
        assert record["state"] == "APPROVED"

    @HttpMocker()
    def test_pagination_start_count(self, http_mocker: HttpMocker):
        """
        Test that connector follows Rest.li start/count pagination.

        /organizationAcls does not support pageToken, so the paginator must inject `start`
        and stop once a page returns fewer than `count` elements.

        Given: A first page with exactly 500 elements and a second page with 1 element
        When: Running a full refresh sync
        Then: The connector should issue a second request with start=500 and return 501 records
        """
        config = ConfigBuilder().build()

        first_page_records = [_create_organization_acl_record(i, role_assignee=f"urn:li:person:{i}") for i in range(_PAGE_SIZE)]
        http_mocker.get(
            LinkedInAdsRequestBuilder.organizations_endpoint().with_q("roleAssignee").with_count(_PAGE_SIZE).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records(first_page_records)
            .with_paging(start=0, count=_PAGE_SIZE, total=_PAGE_SIZE + 1)
            .build(),
        )

        http_mocker.get(
            LinkedInAdsRequestBuilder.organizations_endpoint().with_q("roleAssignee").with_count(_PAGE_SIZE).with_start(_PAGE_SIZE).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder()
            .with_records([_create_organization_acl_record(999, role_assignee="urn:li:person:999")])
            .with_paging(start=_PAGE_SIZE, count=1, total=_PAGE_SIZE + 1)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == _PAGE_SIZE + 1
        organizations = {record.record.data["organization"] for record in output.records}
        assert "urn:li:organization:0" in organizations
        assert "urn:li:organization:499" in organizations
        assert "urn:li:organization:999" in organizations

    @HttpMocker()
    def test_organization_target_fallback(self, http_mocker: HttpMocker):
        """
        Test that `organizationTarget` is normalized into `organization`.

        The API returns the org URN as `organizationTarget` on some responses, which would
        otherwise leave the `organization` primary key component null.

        Given: An element carrying only `organizationTarget`
        When: Running a full refresh sync
        Then: The emitted record should have `organization` populated from `organizationTarget`
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.organizations_endpoint().with_q("roleAssignee").with_count(_PAGE_SIZE).build(),
            LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                [
                    {
                        "role": "DIRECT_SPONSORED_CONTENT_POSTER",
                        "organizationTarget": "urn:li:organization:456",
                        "roleAssignee": "urn:li:person:def",
                        "state": "APPROVED",
                    }
                ],
                total=1,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["organizationTarget"] == "urn:li:organization:456"
        assert record["organization"] == "urn:li:organization:456"

    @HttpMocker()
    def test_retries_on_data_volume_rate_limit(self, http_mocker: HttpMocker):
        """
        Test that the CustomErrorHandler retries the LinkedIn data-volume throttle.

        LinkedInAdsErrorHandler maps this response to RATE_LIMITED instead of failing, so the
        error handler has to actually be wired onto the requester.

        Given: An API that returns the data-volume rate limit error then succeeds
        When: Running a full refresh sync
        Then: The connector should retry and return the record without any stream failure
        """
        config = ConfigBuilder().build()

        http_mocker.get(
            LinkedInAdsRequestBuilder.organizations_endpoint().with_q("roleAssignee").with_count(_PAGE_SIZE).build(),
            [
                HttpResponse(body=_DATA_VOLUME_RATE_LIMIT_BODY, status_code=429),
                LinkedInAdsOffsetPaginatedResponseBuilder.single_page(
                    [_create_organization_acl_record(789, role_assignee="urn:li:person:ghi")],
                    total=1,
                ),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["organization"] == "urn:li:organization:789"
        assert not output.errors
