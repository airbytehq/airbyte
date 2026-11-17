# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any
from unittest import TestCase
from urllib.parse import quote

import pytest

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import START_CURSOR
from .request_builder import PardotRequestBuilder, login_request
from .response_builder import login_response, page_response
from .utils import read_stream, record_ids, sent_queries, stream_state


_STREAM = "emails"
_PATH = "v5/objects/emails"
_FIELDS = (
    "id,name,type,sentAt,subject,clientType,isOperational,campaignId,prospectId,folderId,listId,listEmailId,"
    "emailTemplateId,trackerDomainId,senderOptions.type,senderOptions.address,senderOptions.name,senderOptions.userId,"
    "senderOptions.prospectCustomFieldId,senderOptions.accountCustomFieldId,replyToOptions.type,replyToOptions.address,"
    "replyToOptions.userId,replyToOptions.prospectCustomFieldId,replyToOptions.accountCustomFieldId,createdById"
)


def _request(sent_at_from: str = START_CURSOR) -> PardotRequestBuilder:
    return (
        PardotRequestBuilder.endpoint(_PATH)
        .with_query_param("limit", 1000)
        .with_query_param("fields", _FIELDS)
        .with_query_param("orderBy", "sentAt ASC")
        .with_query_param("sentAtAfterOrEqualTo", sent_at_from)
    )


def _next_page_request() -> PardotRequestBuilder:
    return PardotRequestBuilder.endpoint(_PATH).with_query_param("fields", _FIELDS).with_query_param("nextPageToken", "page-2")


def _email(email_id: int, sent_at: str = "2026-03-01T09:00:00-08:00") -> dict[str, Any]:
    return {
        "id": email_id,
        "name": f"Email {email_id}",
        "type": "html",
        "sentAt": sent_at,
        "subject": "Welcome",
        "clientType": "Builder",
        "isOperational": False,
        "campaignId": 5,
        "prospectId": 301,
        "folderId": 7,
        "listEmailId": 21,
        "emailTemplateId": 31,
        "trackerDomainId": 71,
        "senderOptions": [{"type": "general_user", "address": "sender@example.com", "name": "Example Sender"}],
        "replyToOptions": [{"type": "general_address", "address": "reply@example.com"}],
        "createdById": 11,
    }


class TestEmailsStream(TestCase):
    @HttpMocker()
    def test_first_sync_reads_two_pages_and_saves_the_start_date(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request().build(),
            page_response([_email(number) for number in range(1, 1001)], next_page_url=_next_page_request().url()),
        )
        http_mocker.get(
            _next_page_request().build(),
            page_response([_email(1001), _email(1002, sent_at="2026-03-01T09:00:05-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1003))
        assert output.records[0].record.data == _email(1)
        # A page that follows `nextPageUrl` sends `fields` and the page token, and no filter.
        assert sent_queries(http_mocker)[1] == f"fields={_FIELDS}&nextPageToken=page-2"
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"sentAt": START_CURSOR}

    @HttpMocker()
    def test_restarts_after_a_full_page_without_a_next_page_url(self, http_mocker: HttpMocker) -> None:
        last_of_page = _email(1000, sent_at="2026-03-01T09:16:40-08:00")
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_email(number) for number in range(1, 1000)] + [last_of_page]))
        http_mocker.get(
            _request(sent_at_from="2026-03-01T09:16:40-08:00").build(),
            page_response([_email(1001, sent_at="2026-03-01T09:16:41-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1002))
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_second_sync_sends_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        state = StateBuilder().with_stream_state(_STREAM, {"sentAt": "2026-03-01T09:00:05-12:00"}).build()
        http_mocker.post(login_request(), login_response())
        http_mocker.get(
            _request(sent_at_from="2026-03-01T09:00:05-12:00").build(),
            page_response([_email(1003, sent_at="2026-03-02T10:30:00-08:00")]),
        )

        output = read_stream(_STREAM, SyncMode.incremental, state=state)

        assert record_ids(output) == [1003]
        assert output.get_stream_statuses(_STREAM)[-1] == AirbyteStreamStatus.COMPLETE
        assert stream_state(output) == {"sentAt": "2026-03-02T10:30:00-12:00"}


@pytest.mark.parametrize("offset", ["+01:00", "-08:00"])
def test_restart_sends_one_inclusive_filter_with_the_value_encoded(offset: str) -> None:
    # Past 100,000 records the API returns a full page with no page token, and the connector starts a new query from the
    # last record's cursor value.
    boundary = f"2026-03-01T09:16:40{offset}"
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_email(number) for number in range(1, 1000)] + [_email(1000, sent_at=boundary)]))
        http_mocker.get(_request(sent_at_from=boundary).build(), page_response([_email(1001, sent_at=boundary)]))

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1002))
        assert sent_queries(http_mocker)[-1] == (
            f"sentAtAfterOrEqualTo={quote(boundary)}&limit=1000&fields={quote(_FIELDS)}&orderBy=sentAt+ASC"
        )


def test_restart_reads_every_record_of_the_boundary_second() -> None:
    # The new query starts at the second of the page's last record: it reads that record again and every other record of that second.
    boundary = "2026-03-01T09:16:40-08:00"
    with HttpMocker() as http_mocker:
        http_mocker.post(login_request(), login_response())
        http_mocker.get(_request().build(), page_response([_email(number) for number in range(1, 1000)] + [_email(1000, sent_at=boundary)]))
        http_mocker.get(
            _request(sent_at_from=boundary).build(),
            page_response([_email(1000, sent_at=boundary), _email(1001, sent_at=boundary)]),
        )

        output = read_stream(_STREAM, SyncMode.incremental)

        assert record_ids(output) == list(range(1, 1001)) + [1000, 1001]
