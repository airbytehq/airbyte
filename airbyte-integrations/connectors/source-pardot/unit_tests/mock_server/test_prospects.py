# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import START_CURSOR
from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids, stream_state


_STREAM = "prospects"
_PATH = "v5/objects/prospects"
_FIELDS = (
    "id,email,optedOut,isDeleted,isDoNotCall,isDoNotEmail,isEmailHardBounced,isReviewed,isStarred,doNotSell,"
    "prospectAccountId,campaignId,profileId,lifecycleStageId,userId,lastActivityAt,recentInteraction,firstName,lastName,"
    "salutation,jobTitle,emailBouncedAt,emailBouncedReason,source,sourceParameter,campaignParameter,mediumParameter,"
    "contentParameter,termParameter,firstActivityAt,firstAssignedAt,firstReferrerQuery,firstReferrerType,firstReferrerUrl,"
    "salesforceId,salesforceContactId,salesforceLeadId,salesforceAccountId,salesforceCampaignId,salesforceOwnerId,"
    "salesforceUrl,salesforceLastSync,assignedToId,convertedAt,convertedFromObjectName,convertedFromObjectType,grade,phone,"
    "fax,addressOne,addressTwo,city,state,zip,country,company,annualRevenue,website,industry,department,yearsInBusiness,"
    "employees,score,territory,comments,notes,createdAt,updatedAt,createdById,updatedById"
)


def _request(updated_at_after: str = START_CURSOR) -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("deleted", "all")
        .with_query_param("orderBy", "updatedAt ASC")
        .with_query_param("updatedAtAfter", updated_at_after)
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _prospect(prospect_id: int, updated_at: str = "2026-03-01T09:00:00-08:00") -> dict[str, Any]:
    return {
        "id": prospect_id,
        "email": f"prospect{prospect_id}@example.com",
        "optedOut": False,
        "isDeleted": False,
        "isDoNotEmail": False,
        "prospectAccountId": 41,
        "campaignId": 5,
        "firstName": "Ada",
        "lastName": "Example",
        "company": "Example Inc",
        "assignedToId": 12,
        "grade": "B+",
        "score": 150,
        "lastActivityAt": "2026-02-28T16:45:00-08:00",
        "createdAt": "2026-02-01T08:00:00-08:00",
        "updatedAt": updated_at,
        "createdById": 11,
        "updatedById": 11,
    }


class TestProspectsStream(TestCase):
    @HttpMocker()
    def test_first_sync_reads_two_pages_and_saves_the_start_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_prospect(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(
            _next_page_request().build(),
            page_response([_prospect(1001), _prospect(1002, updated_at="2026-03-01T09:00:05-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1003))
        # The vendor documents both as integers. The schema declares strings, so they come out as strings.
        assert output.records[0].record.data == {**_prospect(1), "assignedToId": "12", "score": "150"}
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"updatedAt": START_CURSOR}

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        last_of_page = _prospect(1000, updated_at="2026-03-01T09:16:40-08:00")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_prospect(number) for number in range(1, 1000)] + [last_of_page]))
        http_mocker.get(
            _request(updated_at_after="2026-03-01T09:16:40-08:00").build(),
            page_response([_prospect(1001, updated_at="2026-03-01T09:16:41-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_second_sync_sends_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"updatedAt": "2026-03-01T09:00:05-12:00"}).build()
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request(updated_at_after="2026-03-01T09:00:05-12:00").build(),
            page_response([_prospect(1003, updated_at="2026-03-02T10:30:00-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert record_ids(output) == [1003]
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"updatedAt": "2026-03-02T10:30:00-12:00"}
