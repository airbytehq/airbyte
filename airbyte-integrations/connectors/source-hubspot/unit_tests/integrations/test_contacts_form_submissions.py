# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode

from . import HubspotTestCase
from .request_builders.streams import ContactsStreamRequestBuilder
from .response_builder.contact_response_builder import AllContactsResponseBuilder, ContactBuilder, ContactsFormSubmissionsBuilder

_START_TIME_BEFORE_ANY_RECORD = "1970-01-01T00:00:00Z"

_VID_OFFSET = 5331889818


class TestContactsFormSubmissionsStream(TestCase, HubspotTestCase):
    SCOPES = ["crm.objects.contacts.read"]
    STREAM_NAME = "contacts_form_submissions"

    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        self.mock_oauth(self._http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(self._http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(self._http_mocker)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_read_multiple_contact_pages(self) -> None:
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("formSubmissionMode", "all").build(),
            AllContactsResponseBuilder().with_pagination(vid_offset=_VID_OFFSET).with_contacts([
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                ]),
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                ]),
            ]).build(),
        )
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("formSubmissionMode", "all").with_vid_offset(str(_VID_OFFSET)).build(),
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                ]),
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                ]),
            ]).build(),
        )

        output = self.read_from_stream(
            cfg=self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD),
            stream=self.STREAM_NAME,
            sync_mode=SyncMode.full_refresh
        )

        assert len(output.records) == 11
        assert output.state_messages[0].state.stream.stream_state.dict() == {"vidOffset": 5331889818}
        assert output.state_messages[0].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[0].state.sourceStats.recordCount == 6
        assert output.state_messages[1].state.stream.stream_state.dict() == {}
        assert output.state_messages[1].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[1].state.sourceStats.recordCount == 5

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
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("formSubmissionMode", "all").build(),
            AllContactsResponseBuilder().with_pagination(vid_offset=_VID_OFFSET).with_contacts([
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),

                ]),
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                ]),
            ]).build(),
        )
        self.mock_response(
            self._http_mocker,
            ContactsStreamRequestBuilder().with_filter("formSubmissionMode", "all").with_vid_offset(str(_VID_OFFSET)).build(),
            AllContactsResponseBuilder().with_contacts([
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                ]),
                ContactBuilder().with_form_submissions([
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                    ContactsFormSubmissionsBuilder(),
                ]),
            ]).build(),
        )

        output = self.read_from_stream(
            cfg=self.oauth_config(start_date=_START_TIME_BEFORE_ANY_RECORD),
            stream=self.STREAM_NAME,
            sync_mode=SyncMode.full_refresh,
            state=state
        )

        assert len(output.records) == 6
        assert output.state_messages[0].state.stream.stream_state.dict() == {}
        assert output.state_messages[0].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[0].state.sourceStats.recordCount == 6
