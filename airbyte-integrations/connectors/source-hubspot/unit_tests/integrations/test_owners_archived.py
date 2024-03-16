# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import freezegun
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_protocol.models import SyncMode

from . import HubspotTestCase
from .request_builders.streams import OwnersArchivedStreamRequestBuilder
from .response_builder.streams import HubspotStreamResponseBuilder


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestOwnersArchivedStream(HubspotTestCase):
    """
    The test case contains a single test - this is just a sanity check, as the tested
    stream is identical to the `Owners` stream (which is covered by acceptance tests), except for a single url param.
    """
    SCOPES = ["crm.objects.owners.read"]
    CURSOR_FIELD = "updatedAt"
    STREAM_NAME = "owners_archived"

    def request(self):
        return OwnersArchivedStreamRequestBuilder().build()

    def response(self, with_pagination: bool = False):
        response_builder = HubspotStreamResponseBuilder.for_stream(self.STREAM_NAME)
        record = self.record_builder(self.STREAM_NAME, FieldPath(self.CURSOR_FIELD)).with_field(
            FieldPath(self.CURSOR_FIELD), self.dt_str(self.updated_at())
        ).with_field(
            FieldPath("id"), self.OBJECT_ID
        )
        response = response_builder.with_record(record)
        if with_pagination:
            response = response.with_pagination()
        return response.build()

    @HttpMocker()
    def test_given_one_page_when_read_stream_oauth_then_return_records(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(http_mocker)
        self.mock_response(http_mocker, self.request(), self.response())
        output = self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 1
