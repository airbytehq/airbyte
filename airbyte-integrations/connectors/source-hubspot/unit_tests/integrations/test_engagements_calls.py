# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import http
from typing import Dict, Optional

import freezegun
import mock
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_protocol.models import SyncMode

from . import HubspotTestCase
from .request_builders.streams import CRMStreamRequestBuilder
from .response_builder.streams import HubspotStreamResponseBuilder


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestEngagementCallsStream(HubspotTestCase):
    SCOPES = ["crm.objects.contacts.read"]
    CURSOR_FIELD = "updatedAt"
    STREAM_NAME = "engagements_calls"
    OBJECT_TYPE = "calls"
    ASSOCIATIONS = ["contacts", "deal", "company", "tickets"]

    @property
    def response_builder(self):
        return HubspotStreamResponseBuilder.for_stream(self.STREAM_NAME)

    def request(self, page_token: Optional[Dict[str, str]] = None):
        request_builder = CRMStreamRequestBuilder().for_entity(
            self.OBJECT_TYPE
        ).with_associations(
            self.ASSOCIATIONS
        ).with_properties(
            list(self.PROPERTIES.keys())
        )
        if page_token:
            request_builder = request_builder.with_page_token(page_token)
        return request_builder.build()

    def response(self, with_pagination: bool = False):
        record = self.record_builder(self.STREAM_NAME, FieldPath(self.CURSOR_FIELD)).with_field(
            FieldPath(self.CURSOR_FIELD), self.dt_str(self.updated_at())
        ).with_field(
            FieldPath("id"), self.OBJECT_ID
        )
        response = self.response_builder.with_record(record)
        if with_pagination:
            response = response.with_pagination()
        return response.build()

    def _set_up_oauth(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, self.SCOPES)

    def _set_up_requests(self, http_mocker: HttpMocker, with_oauth: bool = False):
        if with_oauth:
            self._set_up_oauth(http_mocker)
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, self.OBJECT_TYPE, self.PROPERTIES)

    @HttpMocker()
    def test_given_oauth_authentication_when_read_then_perform_authenticated_queries(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_oauth=True)
        self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh)

    @HttpMocker()
    def test_given_records_when_read_extract_desired_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker, with_oauth=True)
        self.mock_response(http_mocker, self.request(), self.response())
        output = self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_one_page_when_read_stream_private_token_then_return_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(http_mocker, self.request(), self.response())
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_then_return_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(http_mocker, self.request(), self.response(with_pagination=True))
        self.mock_response(
            http_mocker,
            self.request(page_token=self.response_builder.pagination_strategy.NEXT_PAGE_TOKEN),
            self.response()
        )
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_error_response_when_read_analytics_then_get_trace_message(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(http_mocker, self.request(), HttpResponse(status_code=500, body="{}"))
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 0
        assert len(output.trace_messages) > 0
        assert len(output.errors) > 0

    @HttpMocker()
    def test_given_500_then_200_when_read_then_return_records(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(
            http_mocker,
            self.request(),
            [
                HttpResponse(status_code=500, body="{}"),
                self.response()
            ]
        )
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 1
        assert len(output.trace_messages) > 0
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_missing_scopes_error_when_read_then_stop_sync(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, [])
        self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh, expecting_exception=True)

    @HttpMocker()
    def test_given_unauthorized_error_when_read_then_stop_sync(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(http_mocker, self.request(), HttpResponse(status_code=http.HTTPStatus.UNAUTHORIZED, body="{}"))
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)
        assert len(output.records) == 0
        assert len(output.trace_messages) > 0
        assert len(output.errors) > 0

    @HttpMocker()
    def test_given_one_page_when_read_then_get_records_with_flattened_properties(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(http_mocker, self.request(), self.response())
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)
        record = output.records[0].record.data
        assert "properties" in record  # legacy struct remains to not introduce breaking changes
        prop_fields = len([f for f in record if f.startswith("properties_")])
        assert prop_fields > 0

    @HttpMocker()
    def test_given_incremental_sync_when_read_then_state_message_produced_and_state_match_latest_record(self, http_mocker: HttpMocker):
        self._set_up_requests(http_mocker)
        self.mock_response(http_mocker, self.request(), self.response())
        output = self.read_from_stream(
            self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.incremental
        )
        assert len(output.state_messages) == 1

