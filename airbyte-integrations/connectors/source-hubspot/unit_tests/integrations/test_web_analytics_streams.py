import copy
import http
from typing import Any, List, Dict, Optional, Tuple

import mock
import pytz
import pytest
import freezegun
from datetime import datetime, timedelta
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
    PaginationStrategy
)
from .config_builder import ConfigBuilder
from .response_builder.helpers import RootHttpResponseBuilder
from .response_builder.other import ScopesAbstractResponseBuilder
from .response_builder.web_analytics import WebAnalyticsResponseBuilder, GenericAbstractResponseBuilder
from .request_builders.web_analytics import WebAnalyticsRequestBuilder, IncrementalCRMStreamRequestBuilder, CRMStreamRequestBuilder
from .request_builders.other import OAuthRequestBuilder, CustomObjectsRequestBuilder, ScopesRequestBuilder, PropertiesRequestBuilder
from airbyte_protocol.models import AirbyteStateMessage, FailureType, SyncMode
from source_hubspot import SourceHubspot


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


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class WebAnalytics:
    DT_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    @classmethod
    def now(cls):
        return datetime.now(pytz.utc)

    @classmethod
    def start_date(cls):
        return cls.now() - timedelta(days=30)

    @classmethod
    def updated_at(cls):
        return cls.now() - timedelta(days=1)

    @classmethod
    def dt_str(cls, dt: datetime.date) -> str:
        return dt.strftime(cls.DT_FORMAT)

    @classmethod
    def oauth_config(cls, start_date: Optional[str] = None) -> Dict[str, Any]:
        start_date = start_date or cls.dt_str(cls.start_date())
        return ConfigBuilder().with_start_date(start_date).with_auth(
            {
                "credentials_title": "OAuth Credentials",
                "redirect_uri": "https://airbyte.io",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "refresh_token": "refresh_token",
            }
        ).build()

    @classmethod
    def private_token_config(cls, token: str, start_date: Optional[str] = None) -> Dict[str, Any]:
        start_date = start_date or cls.dt_str(cls.start_date())
        return ConfigBuilder().with_start_date(start_date).with_auth(
            {
                "credentials_title": "Private App Credentials",
                "access_token": token,
            }
        ).build()

    @classmethod
    def mock_oauth(cls, http_mocker: HttpMocker, token: str):
        creds = cls.oauth_config()["credentials"]
        req = OAuthRequestBuilder().with_client_id(
            creds["client_id"]
        ).with_client_secret(
            creds["client_secret"]
        ).with_refresh_token(
            creds["refresh_token"]
        ).build()
        response = GenericAbstractResponseBuilder().with_value("access_token", token).with_value("expires_in", 7200).build()
        http_mocker.post(req, response)

    @classmethod
    def mock_scopes(cls, http_mocker: HttpMocker, token: str, scopes: List[str]):
        http_mocker.get(ScopesRequestBuilder().with_access_token(token).build(), ScopesAbstractResponseBuilder(scopes).build())

    @classmethod
    def mock_custom_objects(cls, http_mocker: HttpMocker):
        http_mocker.get(
            CustomObjectsRequestBuilder().build(),
            HttpResponseBuilder({}, records_path=FieldPath("results"), pagination_strategy=None).build()
        )

    @classmethod
    def mock_properties(cls, http_mocker: HttpMocker, object_type: str, properties: Dict[str, str]):
        templates = find_template(f"properties", __file__)
        record_builder = lambda: RecordBuilder(copy.deepcopy(templates[0]), id_path=None, cursor_path=None)

        response_builder = RootHttpResponseBuilder(templates)
        for name, type in properties.items():
            record = record_builder().with_field(FieldPath("name"), name).with_field(FieldPath("type"), type)
            response_builder = response_builder.with_record(record)

        http_mocker.get(
            PropertiesRequestBuilder().for_entity(object_type).build(),
            response_builder.build()
        )

    @classmethod
    def mock_parent_object(
        cls,
        http_mocker: HttpMocker,
        object_ids: List[str],
        object_type: str,
        stream_name: str,
        associations: List[str],
        properties: List[str],
        date_range: Optional[Tuple[str,...]] = None,
    ):
        response_builder = WebAnalyticsResponseBuilder.for_stream(stream_name)
        for object_id in object_ids:
            record = cls.record_builder(stream_name, FieldPath("updatedAt")).with_field(
                FieldPath("updatedAt"), cls.dt_str(cls.updated_at())
            ).with_field(
                FieldPath("id"), object_id
            )
            response_builder = response_builder.with_record(record)

        http_mocker.get(
            CRMStreamRequestBuilder().for_entity(object_type).with_associations(associations).with_properties(properties).build(),
            response_builder.build()
        )

    @classmethod
    def mock_response(cls, http_mocker: HttpMocker, request, responses):
        if not isinstance(responses, (list, tuple)):
            responses = [responses]
        http_mocker.get(request, responses)

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
            response_builder = WebAnalyticsResponseBuilder.for_stream(stream)
            query.update(response_builder.pagination_strategy.NEXT_PAGE_TOKEN)
        return WebAnalyticsRequestBuilder().with_token(token).with_query(query).build()

    @classmethod
    def web_analytics_response(cls, stream: str, with_pagination: bool = False, updated_on: Optional[str] = None) -> HttpResponse:
        updated_on = updated_on or cls.dt_str(cls.updated_at())
        record = cls.record_builder(stream, FieldPath("occurredAt")).with_field(FieldPath("updatedAt"), updated_on)
        response_builder = WebAnalyticsResponseBuilder.for_stream(stream)
        response = response_builder.with_record(record)
        if with_pagination:
            response = response.with_pagination()
        return response.build()

    @classmethod
    def record_builder(cls, stream: str, record_cursor_path):
        return create_record_builder(
            find_template(stream, __file__), records_path=FieldPath("results"), record_id_path=None, record_cursor_path=record_cursor_path
        )

    @classmethod
    def catalog(cls, stream: str, sync_mode: SyncMode):
        return CatalogBuilder().with_stream(stream, sync_mode).build()

    @classmethod
    def read_from_stream(
        cls, cfg, stream: str, sync_mode: SyncMode, state: Optional[List[AirbyteStateMessage]] = None, expecting_exception: bool = False
    ) -> EntrypointOutput:
        return read(SourceHubspot(), cfg, cls.catalog(stream, sync_mode), state, expecting_exception)


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestCRMWebAnalyticsStreamFullRefresh(WebAnalytics):
    SCOPES = ["tickets", "crm.objects.contacts.read", "crm.objects.companies.read", "contacts", "crm.objects.deals.read", "oauth"]
    OBJECT_ID = "testID"
    ACCESS_TOKEN = "new_access_token"
    PROPERTIES = {
        "closed_date": "datetime",
        "createdate": "datetime",
    }

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
            start_to_end
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
        assert len(output.records) == 4

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


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestIncrementalCRMWebAnalyticsStreamFullRefresh(TestCRMWebAnalyticsStreamFullRefresh):
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
        date_range: Optional[Tuple[str]] = None,
    ):
        date_range = date_range or (cls.dt_str(cls.start_date()), cls.dt_str(cls.now()))
        response_builder = WebAnalyticsResponseBuilder.for_stream(stream_name)
        for object_id in object_ids:
            record = cls.record_builder(stream_name, FieldPath("updatedAt")).with_field(
                FieldPath("updatedAt"), cls.dt_str(cls.updated_at())
            ).with_field(
                FieldPath("id"), object_id
            )
            response_builder = response_builder.with_record(record)

        start, end = date_range
        http_mocker.get(
            IncrementalCRMStreamRequestBuilder().for_entity(object_type).with_associations(associations).with_dt_range(
                ("startTimestamp", cls.dt_conversion(start)),
                ("endTimestamp", cls.dt_conversion(end))
            ).with_properties(properties).build(),
            response_builder.build()
        )

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
