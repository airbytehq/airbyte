# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
import json
from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import SyncMode

from . import HubspotTestCase
from .request_builders.streams import ContactsStreamRequestBuilder
from .response_builder.contact_response_builder import AllContactsResponseBuilder, ContactBuilder, ContactsListMembershipBuilder


_START_TIME_BEFORE_ANY_RECORD = "1970-01-01T00:00:00Z"

_NOW = datetime.now(timezone.utc)
_VID_OFFSET = 5331889818


class ContactsListMembershipsStreamTest(TestCase, HubspotTestCase):
    SCOPES = ["crm.objects.contacts.read"]
    STREAM_NAME = "contacts_list_memberships"

    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        self.mock_oauth(self._http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(self._http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(self._http_mocker)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_given_pagination_when_read_then_extract_records_from_both_pages(self) -> None:
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().build(),
            AllContactsResponseBuilder()
            .with_pagination(vid_offset=_VID_OFFSET)
            .with_contacts(
                [
                    ContactBuilder().with_list_memberships(
                        [
                            ContactsListMembershipBuilder(),
                            ContactsListMembershipBuilder(),
                        ]
                    ),
                ]
            )
            .build(),
        )
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_vid_offset(str(_VID_OFFSET)).build(),
            AllContactsResponseBuilder()
            .with_contacts(
                [
                    ContactBuilder().with_list_memberships(
                        [
                            ContactsListMembershipBuilder(),
                        ]
                    ),
                    ContactBuilder().with_list_memberships(
                        [
                            ContactsListMembershipBuilder(),
                            ContactsListMembershipBuilder(),
                        ]
                    ),
                ]
            )
            .build(),
        )

        memberships = {
            "results": [
                {
                    "canonical-vid": 5331889818,
                    "listId": 166,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-03-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2025-03-31T10:43:34.442Z"
                },
                {
                    "canonical-vid": 5331889818,
                    "listId": 167,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-03-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2025-03-31T10:43:34.442Z"
                },
                {
                    "canonical-vid": 5331889818,
                    "listId": 167,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-03-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2025-03-31T10:43:34.442Z"
                }
            ]
        }
        self.mock_response(
            self._http_mocker,
            HttpRequest("https://api.hubapi.com/crm/v3/lists/records/0-1/5331889818/memberships"),
            HttpResponse(json.dumps(memberships), 200)
        )
        output = self.read_from_stream(self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD), self.STREAM_NAME, SyncMode.full_refresh)

        assert len(output.records) == 9

    def test_given_timestamp_before_start_date_when_read_then_filter_out(self) -> None:
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().build(),
            AllContactsResponseBuilder()
            .with_contacts(
                [
                    ContactBuilder().with_list_memberships(
                        [
                            ContactsListMembershipBuilder().with_timestamp(start_date + timedelta(days=10)),
                            ContactsListMembershipBuilder().with_timestamp(start_date - timedelta(days=10)),
                        ]
                    ),
                ]
            )
            .build(),
        )
        memberships = {
            "results": [
                {
                    "canonical-vid": 5331889818,
                    "listId": 166,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-03-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2025-03-31T10:43:34.442Z"
                },
                {
                    "canonical-vid": 5331889818,
                    "listId": 167,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-03-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2025-03-31T10:43:34.442Z"
                },
                {
                    "canonical-vid": 5331889818,
                    "listId": 167,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2023-03-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2025-03-31T10:43:34.442Z"
                }
            ]
        }
        self.mock_response(
            self._http_mocker,
            HttpRequest("https://api.hubapi.com/crm/v3/lists/records/0-1/5331889818/memberships"),
            HttpResponse(json.dumps(memberships), 200)
        )
        output = self.read_from_stream(
            self.oauth_config(start_date=start_date.isoformat().replace("+00:00", "Z")), self.STREAM_NAME, SyncMode.full_refresh
        )

        assert len(output.records) == 2

    def test_given_state_when_read_then_filter_out(self) -> None:
        state_value = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().build(),
            AllContactsResponseBuilder()
            .with_contacts(
                [
                    ContactBuilder().with_list_memberships(
                        [
                            ContactsListMembershipBuilder().with_timestamp(state_value + timedelta(days=10)),
                            ContactsListMembershipBuilder().with_timestamp(state_value - timedelta(days=10)),
                        ]
                    ),
                ]
            )
            .build(),
        )
        memberships = {
            "results": [
                {
                    "canonical-vid": 5331889818,
                    "listId": 166,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-01-31T10:43:34.442Z",
                    "firstAddedTimestamp": "2024-03-31T10:43:34.442Z"
                },
                {
                    "canonical-vid": 5331889818,
                    "listId": 167,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-02-01T10:43:34.442Z",
                    "firstAddedTimestamp": "2024-03-31T10:43:34.442Z"
                },
                {
                    "canonical-vid": 5331889818,
                    "listId": 167,
                    "listVersion": 0,
                    "lastAddedTimestamp": "2025-02-05T10:43:34.442Z",
                    "firstAddedTimestamp": "2024-03-31T10:43:34.442Z"
                }
            ]
        }
        self.mock_response(
            self._http_mocker,
            HttpRequest("https://api.hubapi.com/crm/v3/lists/records/0-1/5331889818/memberships"),
            HttpResponse(json.dumps(memberships), 200)
        )
        output = self.read_from_stream(
            self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD),
            self.STREAM_NAME,
            SyncMode.incremental,
            StateBuilder().with_stream_state(self.STREAM_NAME, {"lastAddedTimestamp": "2025-02-05T10:43:34.442Z"}).build(),
        )

        assert len(output.records) == 1
