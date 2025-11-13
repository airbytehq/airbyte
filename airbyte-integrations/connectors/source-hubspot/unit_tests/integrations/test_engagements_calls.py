# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import http
import json
from typing import Dict, List, Optional

import freezegun
import mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse

from . import OBJECTS_WITH_DYNAMIC_SCHEMA, HubspotCRMSearchStream


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestEngagementCallsStream(HubspotCRMSearchStream):
    SCOPES = ["crm.objects.contacts.read"]
    CURSOR_FIELD = "updatedAt"
    STREAM_NAME = "engagements_calls"
    OBJECT_TYPE = "calls"
    ASSOCIATIONS = ["companies", "contacts", "deals", "tickets"]
    OBJECT_ID = "12345"

    @HttpMocker()
    def test_given_records_when_read_extract_desired_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_oauth=True, with_dynamic_schemas=False, entities=OBJECTS_WITH_DYNAMIC_SCHEMA)
        self.mock_response(http_mocker, self.request(), self.response(), method="post")
        self._mock_all_associations_for_ids(http_mocker, parent_entity=self.OBJECT_TYPE, record_ids=[self.OBJECT_ID])

        output = self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.incremental)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_one_page_when_read_stream_private_token_then_return_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_dynamic_schemas=False)
        self.mock_response(http_mocker, self.request(), self.response(), method="post")
        self._mock_all_associations_for_ids(http_mocker, parent_entity=self.OBJECT_TYPE, record_ids=[self.OBJECT_ID])

        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_error_response_when_read_analytics_then_get_trace_message(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_dynamic_schemas=False)
        self.mock_response(http_mocker, self.request(), HttpResponse(status_code=500, body="{}"), method="post")
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental)
        assert len(output.records) == 0
        assert len(output.trace_messages) > 0
        assert len(output.errors) > 0

    @HttpMocker()
    def test_given_500_then_200_when_read_then_return_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_dynamic_schemas=False)
        # First attempt 500, then success (both POST)
        self.mock_response(http_mocker, self.request(), [HttpResponse(status_code=500, body="{}"), self.response()], method="post")
        # Associations will be called only after the 200 response
        self._mock_all_associations_for_ids(http_mocker, parent_entity=self.OBJECT_TYPE, record_ids=[self.OBJECT_ID])

        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental)
        assert len(output.records) == 1
        assert len(output.trace_messages) > 0
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_missing_scopes_error_when_read_then_stop_sync(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_custom_objects_streams(http_mocker)
        self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh, expecting_exception=True)

    @HttpMocker()
    def test_given_unauthorized_error_when_read_then_stop_sync(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_dynamic_schemas=False)
        self.mock_response(http_mocker, self.request(), HttpResponse(status_code=http.HTTPStatus.UNAUTHORIZED, body="{}"), method="post")
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental)
        assert len(output.records) == 0
        assert len(output.trace_messages) > 0
        assert len(output.errors) > 0

    @HttpMocker()
    def test_given_one_page_when_read_then_get_records_with_flattened_properties(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_dynamic_schemas=False)
        self.mock_response(http_mocker, self.request(), self.response(), method="post")
        self._mock_all_associations_for_ids(http_mocker, parent_entity=self.OBJECT_TYPE, record_ids=[self.OBJECT_ID])

        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental)
        record = output.records[0].record.data
        assert "properties" in record  # legacy struct remains
        prop_fields = len([f for f in record if f.startswith("properties_")])
        assert prop_fields > 0

    @HttpMocker()
    def test_given_incremental_sync_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_dynamic_schemas=False)
        self.mock_response(http_mocker, self.request(), self.response(), method="post")
        self._mock_all_associations_for_ids(http_mocker, parent_entity=self.OBJECT_TYPE, record_ids=[self.OBJECT_ID])

        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental)
        assert len(output.state_messages) == 2
