# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from datetime import datetime, timedelta, timezone
from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker
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
            ContactsStreamRequestBuilder().with_filter("showListMemberships", True).build(),
            AllContactsResponseBuilder().with_pagination(vid_offset=_VID_OFFSET).with_contacts([
                ContactBuilder().with_list_memberships([
                    ContactsListMembershipBuilder(),
                    ContactsListMembershipBuilder(),
                ]),
            ]).build(),
        )
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("showListMemberships", True).with_vid_offset(str(_VID_OFFSET)).build(),
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_list_memberships([
                    ContactsListMembershipBuilder(),
                ]),
                ContactBuilder().with_list_memberships([
                    ContactsListMembershipBuilder(),
                    ContactsListMembershipBuilder(),
                ]),
            ]).build(),
        )

        output = self.read_from_stream(self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD), self.STREAM_NAME, SyncMode.full_refresh)

        assert len(output.records) == 5

    def test_given_timestamp_before_start_date_when_read_then_filter_out(self) -> None:
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("showListMemberships", True).build(),
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_list_memberships([
                    ContactsListMembershipBuilder().with_timestamp(start_date + timedelta(days=10)),
                    ContactsListMembershipBuilder().with_timestamp(start_date - timedelta(days=10)),
                ]),
            ]).build(),
        )
        output = self.read_from_stream(self.oauth_config(start_date=start_date.isoformat().replace("+00:00", "Z")), self.STREAM_NAME, SyncMode.full_refresh)

        assert len(output.records) == 1

    def test_given_state_when_read_then_filter_out(self) -> None:
        state_value = datetime(2024, 1, 1, tzinfo=timezone.utc)
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("showListMemberships", True).build(),
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_list_memberships([
                    ContactsListMembershipBuilder().with_timestamp(state_value + timedelta(days=10)),
                    ContactsListMembershipBuilder().with_timestamp(state_value - timedelta(days=10)),
                ]),
            ]).build(),
        )
        output = self.read_from_stream(
            self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD),
            self.STREAM_NAME,
            SyncMode.incremental,
            StateBuilder().with_stream_state(self.STREAM_NAME, {"timestamp": int(state_value.timestamp() * 1000)}).build(),
        )

        assert len(output.records) == 1
