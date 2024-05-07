# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_protocol.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode

from . import HubspotContactsTestCase
from .request_builders.streams import ContactsStreamRequestBuilder


@freezegun.freeze_time("2024-05-04T00:00:00Z")
class TestContactsListMembershipsStream(HubspotContactsTestCase):
    SCOPES = ["crm.objects.contacts.read"]
    STREAM_NAME = "contacts_list_memberships"

    @HttpMocker()
    def test_read_multiple_contact_pages(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(http_mocker)

        self.mock_response(http_mocker, ContactsStreamRequestBuilder().with_filter("showListMemberships", True).build(), self.response(stream_name=self.STREAM_NAME, with_pagination=True).build())
        self.mock_response(http_mocker, ContactsStreamRequestBuilder().with_filter("showListMemberships", True).with_vid_offset("5331889818").build(), self.response(stream_name=self.STREAM_NAME).build())

        output = self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh)

        assert len(output.records) == 12
        assert output.state_messages[0].state.stream.stream_state.dict() == {"vidOffset": "5331889818"}
        assert output.state_messages[0].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[0].state.sourceStats.recordCount == 6
        assert output.state_messages[1].state.stream.stream_state.dict() == {}
        assert output.state_messages[1].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[1].state.sourceStats.recordCount == 6

    @HttpMocker()
    def test_read_from_incoming_state(self, http_mocker: HttpMocker):
        state = [
            AirbyteStateMessage(
                type=AirbyteStateType.STREAM,
                stream=AirbyteStreamState(
                    stream_descriptor=StreamDescriptor(name=self.STREAM_NAME),
                    stream_state=AirbyteStateBlob(**{"vidOffset": "5331889818"})
                )
            )
        ]

        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(http_mocker)

        # Even though we only care about the request with a vidOffset parameter, we mock this in order to pass the availability check
        self.mock_response(http_mocker, ContactsStreamRequestBuilder().with_filter("showListMemberships", True).build(), self.response(stream_name=self.STREAM_NAME, with_pagination=True).build())
        self.mock_response(http_mocker, ContactsStreamRequestBuilder().with_filter("showListMemberships", True).with_vid_offset("5331889818").build(), self.response(stream_name=self.STREAM_NAME).build())

        output = self.read_from_stream(cfg=self.oauth_config(), stream=self.STREAM_NAME, sync_mode=SyncMode.full_refresh, state=state)

        assert len(output.records) == 6
        assert output.state_messages[0].state.stream.stream_state.dict() == {}
        assert output.state_messages[0].state.stream.stream_descriptor.name == self.STREAM_NAME
        assert output.state_messages[0].state.sourceStats.recordCount == 6
