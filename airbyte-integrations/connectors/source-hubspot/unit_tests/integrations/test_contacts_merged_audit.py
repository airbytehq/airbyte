# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode

from . import HubspotTestCase
from .request_builders.streams import ContactsStreamRequestBuilder
from .response_builder.contact_response_builder import AllContactsResponseBuilder, ContactBuilder, ContactsMergeAuditsBuilder

_START_TIME_BEFORE_ANY_RECORD = "1970-01-01T00:00:00Z"

_VID_OFFSET = 5331889818


class TestContactsMergedAuditStream(TestCase, HubspotTestCase):
    SCOPES = ["crm.objects.contacts.read"]
    STREAM_NAME = "contacts_merged_audit"

    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        self.mock_oauth(self._http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(self._http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(self._http_mocker)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_read_multiple_contact_pages(self) -> None:
        first_page_request = ContactsStreamRequestBuilder().build()
        second_page_request = ContactsStreamRequestBuilder().with_vid_offset(str(_VID_OFFSET)).build()
        self.mock_response(
            self._http_mocker,
            first_page_request,
            AllContactsResponseBuilder().with_pagination(vid_offset=_VID_OFFSET).with_contacts([
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                ]),
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                ]),
            ]).build(),
        )
        self.mock_response(
            self._http_mocker,
            second_page_request,
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                ]),
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                ]),
            ]).build(),
        )

        output = self.read_from_stream(self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD), self.STREAM_NAME, SyncMode.full_refresh)

        self._http_mocker.assert_number_of_calls(first_page_request, 2)
        self._http_mocker.assert_number_of_calls(second_page_request, 1)

        assert len(output.records) == 10
        assert output.state_messages[0].state.stream.stream_state.dict() == {"vidOffset": 5331889818}
        assert output.state_messages[0].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[0].state.sourceStats.recordCount == 7
        assert output.state_messages[1].state.stream.stream_state.dict() == {"__ab_full_refresh_sync_complete": True}
        assert output.state_messages[1].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[1].state.sourceStats.recordCount == 3

    def test_read_from_incoming_state(self) -> None:
        state = [
            AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name=self.STREAM_NAME),
                    stream_state=AirbyteStateBlob(**{"vidOffset": "5331889818"})
                )
            )
        ]

        # Even though we only care about the request with a vidOffset parameter, we mock this in order to pass the availability check
        first_page_request = ContactsStreamRequestBuilder().build()
        second_page_request = ContactsStreamRequestBuilder().with_vid_offset(str(_VID_OFFSET)).build()
        self.mock_response(
            self._http_mocker,
            first_page_request,
            AllContactsResponseBuilder().with_pagination(vid_offset=_VID_OFFSET).with_contacts([
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                ]),
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                ]),
            ]).build(),
        )
        self.mock_response(
            self._http_mocker,
            second_page_request,
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                ]),
                ContactBuilder().with_merge_audits([
                    ContactsMergeAuditsBuilder(),
                    ContactsMergeAuditsBuilder(),
                ]),
            ]).build(),
        )

        output = self.read_from_stream(
            cfg=self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD),
            stream=self.STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            state=state
        )

        # We call the first page during check availability. And the sync actually starts with a request to the second page
        self._http_mocker.assert_number_of_calls(first_page_request, 1)
        self._http_mocker.assert_number_of_calls(second_page_request, 1)

        assert len(output.records) == 3
        assert output.state_messages[0].state.stream.stream_state.dict() == {"__ab_full_refresh_sync_complete": True}
        assert output.state_messages[0].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[0].state.sourceStats.recordCount == 3
