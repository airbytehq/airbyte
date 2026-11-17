# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus
from airbyte_cdk.test.mock_http import HttpMocker

from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids


_STREAM = "tracker_domains"
_PATH = "v5/objects/tracker-domains"
_FIELDS = (
    "id,domain,isPrimary,isDeleted,defaultCampaignId,httpsStatus,sslStatus,sslStatusDetails,sslRequestedById,"
    "validationStatus,validatedAt,vanityUrlStatus,trackingCode,createdAt,updatedAt,createdById,updatedById"
)


def _request() -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("deleted", "all")
        .with_query_param("orderBy", "id ASC")
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _tracker_domain(domain_id: int) -> dict[str, Any]:
    return {
        "id": domain_id,
        "domain": f"go{domain_id}.example.com",
        "isPrimary": False,
        "isDeleted": False,
        "defaultCampaignId": 5,
        "httpsStatus": "https",
        "sslStatus": "enabled",
        "validationStatus": "validated",
        "validatedAt": "2026-02-02T08:00:00-08:00",
        "vanityUrlStatus": "enabled",
        "createdAt": "2026-02-01T08:00:00-08:00",
        "updatedAt": "2026-03-01T09:00:00-08:00",
        "createdById": 11,
        "updatedById": 11,
    }


class TestTrackerDomainsStream(TestCase):
    @HttpMocker()
    def test_reads_two_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_tracker_domain(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(_next_page_request().build(), page_response([_tracker_domain(1001), _tracker_domain(1002)]))

        output = read_stream(_STREAM)

        assert record_ids(output) == list(range(1, 1003))
        assert output.records[0].record.data == _tracker_domain(1)
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_tracker_domain(number) for number in range(1, 1001)]))
        http_mocker.get(_request().with_query_param("idGreaterThan", 1000).build(), page_response([_tracker_domain(1001)]))

        output = read_stream(_STREAM)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
