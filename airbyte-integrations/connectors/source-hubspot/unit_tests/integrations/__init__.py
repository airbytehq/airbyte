# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import copy
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import freezegun
import pytz
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpResponse, HttpRequest, HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, RecordBuilder, create_record_builder, find_template
from airbyte_cdk.models import AirbyteStateMessage, SyncMode

from .config_builder import ConfigBuilder
from .request_builders.api import CustomObjectsRequestBuilder, OAuthRequestBuilder, PropertiesRequestBuilder, ScopesRequestBuilder
from .request_builders.streams import CRMStreamRequestBuilder, IncrementalCRMStreamRequestBuilder, WebAnalyticsRequestBuilder
from .response_builder.helpers import RootHttpResponseBuilder
from .response_builder.api import ScopesResponseBuilder
from .response_builder.streams import GenericResponseBuilder, HubspotStreamResponseBuilder
from ..conftest import get_source

OBJECTS_WITH_DYNAMIC_SCHEMA = [
    "calls",
    "company",
    "contact",
    "deal",
    "deal_split",
    "emails",
    "form",
    "goal_targets",
    "leads",
    "line_item",
    "meetings",
    "notes",
    "tasks",
    "product",
    "ticket",
]


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class HubspotTestCase:
    DT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    OBJECT_ID = "testID"
    ACCESS_TOKEN = "new_access_token"
    CURSOR_FIELD = "occurredAt"
    MOCK_PROPERTIES_FOR_SCHEMA_LOADER = {
        # We do not need to include `closed_date` because the first property is automatically mocked
        # when we instantiate the properties in RootHttpResponseBuilder(templates).
        # "closed_date": "datetime",
        "createdate": "datetime",
    }
    PROPERTIES = {
        "closed_date": "datetime",
        "createdate": "datetime",
    }

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
        return (
            ConfigBuilder()
            .with_start_date(start_date)
            .with_auth(
                {
                    "credentials_title": "OAuth Credentials",
                    "redirect_uri": "https://airbyte.io",
                    "client_id": "client_id",
                    "client_secret": "client_secret",
                    "refresh_token": "refresh_token",
                }
            )
            .build()
        )

    @classmethod
    def private_token_config(cls, token: str, start_date: Optional[str] = None) -> Dict[str, Any]:
        start_date = start_date or cls.dt_str(cls.start_date())
        return (
            ConfigBuilder()
            .with_start_date(start_date)
            .with_auth(
                {
                    "credentials_title": "Private App Credentials",
                    "access_token": token,
                }
            )
            .build()
        )

    @classmethod
    def mock_oauth(cls, http_mocker: HttpMocker, token: str):
        creds = cls.oauth_config()["credentials"]
        req = (
            OAuthRequestBuilder()
            .with_client_id(creds["client_id"])
            .with_client_secret(creds["client_secret"])
            .with_refresh_token(creds["refresh_token"])
            .build()
        )
        response = GenericResponseBuilder().with_value("access_token", token).with_value("expires_in", 7200).build()
        http_mocker.post(req, response)

    @classmethod
    def mock_custom_objects(cls, http_mocker: HttpMocker):
        http_mocker.get(
            CustomObjectsRequestBuilder().build(),
            HttpResponseBuilder({}, records_path=FieldPath("results"), pagination_strategy=None).build(),
        )

    @classmethod
    def mock_properties(cls, http_mocker: HttpMocker, object_type: str, properties: Dict[str, str]):
        templates = find_template("properties", __file__)
        record_builder = lambda: RecordBuilder(copy.deepcopy(templates[0]), id_path=None, cursor_path=None)

        response_builder = RootHttpResponseBuilder(templates)
        for name, type in properties.items():
            record = record_builder().with_field(FieldPath("name"), name).with_field(FieldPath("type"), type)
            response_builder = response_builder.with_record(record)

        http_mocker.get(PropertiesRequestBuilder().for_entity(object_type).build(), response_builder.build())

    @classmethod
    def mock_response(cls, http_mocker: HttpMocker, request, responses, method: str = "get"):
        if not isinstance(responses, (list, tuple)):
            responses = [responses]
        getattr(http_mocker, method)(request, responses)

    @classmethod
    def mock_dynamic_schema_requests(cls, http_mocker: HttpMocker, entities: Optional[List[str]] = None):
        entities = entities or OBJECTS_WITH_DYNAMIC_SCHEMA

        # figure out which entities are already mocked
        existing = set()
        for entity in entities:
            for request_mock in http_mocker._get_matchers():
                # check if dynamic stream was already mocked
                if f"properties/v2/{entity}" in request_mock.request._parsed_url.path:
                    existing.add(entity)

        templates = [{"name": "hs__test_field", "type": "enumeration"}]
        response_builder = RootHttpResponseBuilder(templates)

        for entity in entities:
            if entity in existing:
                continue  # skip if already mocked

            http_mocker.get(PropertiesRequestBuilder().for_entity(entity).build(), response_builder.build())

    @classmethod
    def mock_custom_objects_streams(cls, http_mocker: HttpMocker):
        # Mock CustomObjects streams
        http_mocker.get(
            HttpRequest("https://api.hubapi.com/crm/v3/schemas"),
            HttpResponse("{}", 200),
        )

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
        return read(get_source(cfg, state), cfg, cls.catalog(stream, sync_mode), state, expecting_exception)
