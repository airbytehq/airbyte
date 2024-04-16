# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import http
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import freezegun
import mock
import pytest
import pytz
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_protocol.models import AirbyteStateBlob, AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor, SyncMode

from . import HubspotTestCase
from .request_builders.streams import CRMStreamRequestBuilder, IncrementalCRMStreamRequestBuilder, WebAnalyticsRequestBuilder
from .response_builder.streams import HubspotStreamResponseBuilder

CRM_STREAMS = (
    ("tickets_web_analytics", "tickets", "ticket", ["contacts", "deals", "companies"]),
    ("deals_web_analytics", "deals", "deal", ["contacts", "companies", "line_items"]),
    ("companies_web_analytics", "companies", "company", ["contacts"]),
    ("contacts_web_analytics", "contacts", "contact", ["contacts", "companies"]),
    ("engagements_calls_web_analytics", "engagements_calls", "calls", ["contacts", "deal", "company", "tickets"]),
    ("engagements_emails_web_analytics", "engagements_emails", "emails", ["contacts", "deal", "company", "tickets"]),
    ("engagements_meetings_web_analytics", "engagements_meetings", "meetings", ["contacts", "deal", "company", "tickets"]),
    ("engagements_notes_web_analytics", "engagements_notes", "notes", ["contacts", "deal", "company", "tickets"]),
    ("engagements_tasks_web_analytics", "engagements_tasks", "tasks", ["contacts", "deal", "company", "tickets"]),
)

CRM_INCREMENTAL_STREAMS = (
    ("goals_web_analytics", "goals", "goal_targets", []),
    ("line_items_web_analytics", "line_items", "line_item", []),
    ("products_web_analytics", "products", "product", []),
)


class WebAnalyticsTestCase(HubspotTestCase):
    PARENT_CURSOR_FIELD = "updatedAt"

    @classmethod
    def response_builder(cls, stream):
        return HubspotStreamResponseBuilder.for_stream(stream)

    @classmethod
    def web_analytics_request(
        cls,
        stream: str,
        token: str,
        object_id: str,
        object_type: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        first_page: bool = True
    ):
        start_date = start_date or cls.dt_str(cls.start_date())
        end_date = end_date or cls.dt_str(cls.now())
        query = {
            "limit": 100,
            "occurredAfter": start_date,
            "occurredBefore": end_date,
            "objectId": object_id,
            "objectType": object_type
        }

        if not first_page:
            query.update(cls.response_builder(stream).pagination_strategy.NEXT_PAGE_TOKEN)
        return WebAnalyticsRequestBuilder().with_token(token).with_query(query).build()

    @classmethod
    def web_analytics_response(
        cls, stream: str, with_pagination: bool = False, updated_on: Optional[str] = None, id: Optional[str] = None
    ) -> HttpResponse:
        updated_on = updated_on or cls.dt_str(cls.updated_at())
        record = cls.record_builder(stream, FieldPath(cls.CURSOR_FIELD)).with_field(FieldPath(cls.CURSOR_FIELD), updated_on)
        if id:
            record = record.with_field(FieldPath("objectId"), id)
        response = cls.response_builder(stream).with_record(record)
        if with_pagination:
            response = response.with_pagination()
        return response.build()

    @classmethod
    def mock_parent_object(
        cls,
        http_mocker: HttpMocker,
        object_ids: List[str],
        object_type: str,
        stream_name: str,
        associations: List[str],
        properties: List[str],
        first_page: bool = True,
        with_pagination: bool = False,
        date_range: Optional[Tuple[str, ...]] = None,
    ):
        response_builder = cls.response_builder(stream_name)
        for object_id in object_ids:
            record = cls.record_builder(stream_name, FieldPath(cls.PARENT_CURSOR_FIELD)).with_field(
                FieldPath(cls.PARENT_CURSOR_FIELD), cls.dt_str(cls.updated_at())
            ).with_field(
                FieldPath("id"), object_id
            )
            response_builder = response_builder.with_record(record)
        if with_pagination:
            response_builder = response_builder.with_pagination()

        request_builder = CRMStreamRequestBuilder().for_entity(object_type).with_associations(associations).with_properties(properties)
        if not first_page:
            request_builder = request_builder.with_page_token(response_builder.pagination_strategy.NEXT_PAGE_TOKEN)
        http_mocker.get(request_builder.build(), response_builder.build())


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestCRMWebAnalyticsStream(WebAnalyticsTestCase):
    SCOPES = ["tickets", "crm.objects.contacts.read", "crm.objects.companies.read", "contacts", "crm.objects.deals.read", "oauth"]

    @classmethod
    def extended_dt_ranges(cls) -> Tuple[Tuple[str, ...], ...]:
        return (
            (cls.dt_str(cls.now() - timedelta(days=60)), cls.dt_str(cls.now() - timedelta(days=30))),
            (cls.dt_str(cls.now() - timedelta(days=30)), cls.dt_str(cls.now())),
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_one_page_when_read_stream_oauth_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, self.SCOPES)
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name)
        )
        output = self.read_from_stream(self.oauth_config(), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 1

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_one_page_when_read_stream_private_token_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name)
        )
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 1

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_two_pages_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name, with_pagination=True)
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type, first_page=False),
            self.web_analytics_response(stream_name)
        )
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 2

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_two_parent_pages_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker,
            [self.OBJECT_ID],
            object_type,
            parent_stream_name,
            parent_stream_associations,
            with_pagination=True,
            properties=list(self.PROPERTIES.keys())
        )
        self.mock_parent_object(
            http_mocker,
            ["another_object_id"],
            object_type,
            parent_stream_name,
            parent_stream_associations,
            first_page=False,
            properties=list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name)
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, "another_object_id", object_type),
            self.web_analytics_response(stream_name)
        )
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 2

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_wide_date_range_and_multiple_parent_records_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        date_ranges = self.extended_dt_ranges()
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        start_to_end = (date_ranges[0][0], date_ranges[-1][-1])
        self.mock_parent_object(
            http_mocker,
            [self.OBJECT_ID, "another_object_id"],
            object_type,
            parent_stream_name,
            parent_stream_associations,
            list(self.PROPERTIES.keys()),
            date_range=start_to_end
        )
        for dt_range in date_ranges:
            for _id in (self.OBJECT_ID, "another_object_id"):
                start, end = dt_range
                web_analytics_response = self.web_analytics_response(stream_name)
                self.mock_response(
                    http_mocker,
                    self.web_analytics_request(stream_name, self.ACCESS_TOKEN, _id, object_type, start, end),
                    web_analytics_response
                )
        config_start_dt = date_ranges[0][0]
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN, config_start_dt), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 4  # 2 parent objects * 2 datetime slices

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_error_response_when_read_analytics_then_get_trace_message(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            HttpResponse(status_code=500, body="{}")
        )
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 0
        assert len(output.trace_messages) > 0
        assert len(output.errors) > 0

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_500_then_200_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            [
                HttpResponse(status_code=500, body="{}"),
                self.web_analytics_response(stream_name)
            ]
        )
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 1
        assert len(output.trace_messages) > 0
        assert len(output.errors) == 0

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_missing_scopes_error_when_read_then_hault(
        self,
        stream_name,
        parent_stream_name,
        object_type,
        parent_stream_associations,
        http_mocker: HttpMocker
    ):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_scopes(http_mocker, self.ACCESS_TOKEN, [])
        self.read_from_stream(self.oauth_config(), stream_name, SyncMode.full_refresh, expecting_exception=True)

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_unauthorized_error_when_read_then_hault(
        self,
        stream_name,
        parent_stream_name,
        object_type,
        parent_stream_associations,
        http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            HttpResponse(status_code=http.HTTPStatus.UNAUTHORIZED, body="{}")
        )
        with mock.patch("time.sleep"):
            output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 0
        assert len(output.trace_messages) > 0
        assert len(output.errors) > 0

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_one_page_when_read_then_get_transformed_records(
        self,
        stream_name,
        parent_stream_name,
        object_type,
        parent_stream_associations,
        http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name)
        )
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        record = output.records[0].record.data
        assert "properties" not in record
        prop_fields = len([f for f in record if f.startswith("properties_")])
        assert prop_fields > 0

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_one_page_when_read_then_get_no_records_filtered(
        self,
        stream_name,
        parent_stream_name,
        object_type,
        parent_stream_associations,
        http_mocker: HttpMocker
    ):
        # validate that no filter is applied on the record set received from the API response
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name, updated_on=self.dt_str(self.now() - timedelta(days=365)))
        )
        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.full_refresh)
        assert len(output.records) == 1

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_incremental_sync_when_read_then_state_message_produced_and_state_match_latest_record(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name, id=self.OBJECT_ID)
        )
        output = self.read_from_stream(
            self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.incremental
        )
        assert len(output.state_messages) == 1

        cursor_value_from_state_message = output.most_recent_state.stream_state.dict().get(self.OBJECT_ID, {}).get(self.CURSOR_FIELD)
        cursor_value_from_latest_record = output.records[-1].record.data.get(self.CURSOR_FIELD)
        assert cursor_value_from_state_message == cursor_value_from_latest_record

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_state_with_no_current_slice_when_read_then_current_slice_in_state(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name, id=self.OBJECT_ID)
        )
        another_object_id = "another_object_id"
        current_state = AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name),
                stream_state=AirbyteStateBlob(**{another_object_id: {self.CURSOR_FIELD: self.dt_str(self.now())}})
            )
        )
        output = self.read_from_stream(
            self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.incremental, state=[current_state]
        )
        assert len(output.state_messages) == 1
        assert output.most_recent_state.stream_state.dict().get(self.OBJECT_ID, {}).get(self.CURSOR_FIELD)
        assert output.most_recent_state.stream_state.dict().get(another_object_id, {}).get(self.CURSOR_FIELD)

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_STREAMS)
    @HttpMocker()
    def test_given_state_with_current_slice_when_read_then_state_is_updated(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations, http_mocker: HttpMocker
    ):
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, object_type, self.PROPERTIES)
        self.mock_parent_object(
            http_mocker, [self.OBJECT_ID], object_type, parent_stream_name, parent_stream_associations, list(self.PROPERTIES.keys())
        )
        self.mock_response(
            http_mocker,
            self.web_analytics_request(stream_name, self.ACCESS_TOKEN, self.OBJECT_ID, object_type),
            self.web_analytics_response(stream_name, id=self.OBJECT_ID)
        )
        current_state = AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name=stream_name),
                stream_state=AirbyteStateBlob(**{self.OBJECT_ID: {self.CURSOR_FIELD: self.dt_str(self.start_date() - timedelta(days=30))}})
            )
        )
        output = self.read_from_stream(
            self.private_token_config(self.ACCESS_TOKEN), stream_name, SyncMode.incremental, state=[current_state]
        )
        assert len(output.state_messages) == 1
        assert output.most_recent_state.stream_state.dict().get(self.OBJECT_ID, {}).get(self.CURSOR_FIELD) == self.dt_str(self.updated_at())


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestIncrementalCRMWebAnalyticsStreamFullRefresh(TestCRMWebAnalyticsStream):
    SCOPES = ["e-commerce", "oauth", "crm.objects.feedback_submissions.read", "crm.objects.goals.read"]

    @classmethod
    def dt_conversion(cls, dt: str) -> str:
        return str(int(datetime.strptime(dt, cls.DT_FORMAT).replace(tzinfo=pytz.utc).timestamp()) * 1000)

    @classmethod
    def mock_parent_object(
        cls,
        http_mocker: HttpMocker,
        object_ids: List[str],
        object_type: str,
        stream_name: str,
        associations: List[str],
        properties: List[str],
        first_page: bool = True,
        with_pagination: bool = False,
        date_range: Optional[Tuple[str]] = None,
    ):
        date_range = date_range or (cls.dt_str(cls.start_date()), cls.dt_str(cls.now()))
        response_builder = cls.response_builder(stream_name)
        for object_id in object_ids:
            record = cls.record_builder(stream_name, FieldPath(cls.PARENT_CURSOR_FIELD)).with_field(
                FieldPath(cls.PARENT_CURSOR_FIELD), cls.dt_str(cls.updated_at())
            ).with_field(
                FieldPath("id"), object_id
            )
            response_builder = response_builder.with_record(record)
        if with_pagination:
            response_builder = response_builder.with_pagination()

        start, end = date_range
        request_builder = IncrementalCRMStreamRequestBuilder().for_entity(
            object_type
        ).with_associations(
            associations
        ).with_dt_range(
            ("startTimestamp", cls.dt_conversion(start)),
            ("endTimestamp", cls.dt_conversion(end))
        ).with_properties(properties)
        if not first_page:
            request_builder = request_builder.with_page_token(response_builder.pagination_strategy.NEXT_PAGE_TOKEN)

        http_mocker.get(request_builder.build(), response_builder.build())

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_one_page_when_read_stream_oauth_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_one_page_when_read_stream_oauth_then_return_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_one_page_when_read_stream_private_token_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_one_page_when_read_stream_private_token_then_return_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_two_pages_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_two_pages_when_read_then_return_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_wide_date_range_and_multiple_parent_records_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_wide_date_range_and_multiple_parent_records_when_read_then_return_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_error_response_when_read_analytics_then_get_trace_message(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_error_response_when_read_analytics_then_get_trace_message(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_500_then_200_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_500_then_200_when_read_then_return_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_missing_scopes_error_when_read_then_hault(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_missing_scopes_error_when_read_then_hault(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_unauthorized_error_when_read_then_hault(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_unauthorized_error_when_read_then_hault(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_one_page_when_read_then_get_transformed_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_one_page_when_read_then_get_transformed_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_one_page_when_read_then_get_no_records_filtered(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_one_page_when_read_then_get_no_records_filtered(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_incremental_sync_when_read_then_state_message_produced_and_state_match_latest_record(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_incremental_sync_when_read_then_state_message_produced_and_state_match_latest_record(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_state_with_no_current_slice_when_read_then_current_slice_in_state(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_state_with_no_current_slice_when_read_then_current_slice_in_state(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_state_with_current_slice_when_read_then_state_is_updated(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_state_with_current_slice_when_read_then_state_is_updated(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )

    @pytest.mark.parametrize(("stream_name", "parent_stream_name", "object_type", "parent_stream_associations"), CRM_INCREMENTAL_STREAMS)
    def test_given_two_parent_pages_when_read_then_return_records(
        self, stream_name, parent_stream_name, object_type, parent_stream_associations
    ):
        super().test_given_two_parent_pages_when_read_then_return_records(
            stream_name, parent_stream_name, object_type, parent_stream_associations
        )
