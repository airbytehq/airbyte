# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import copy
import json
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
from .request_builders.streams import AssociationsBatchReadRequestBuilder, CRMSearchRequestBuilder, WebAnalyticsRequestBuilder
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
        entities = entities if entities is not None else OBJECTS_WITH_DYNAMIC_SCHEMA

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


class HubspotCRMSearchStream(HubspotTestCase):
    def _ms(self, dt) -> int:
        return int(dt.timestamp() * 1000)

    def request(self, page_token: Optional[Dict[str, str]] = None):
        start = self.start_date()
        end = self.now()

        builder = (
            CRMSearchRequestBuilder()
            .for_entity(self.OBJECT_TYPE)
            .with_properties(list(self.PROPERTIES.keys()))
            .with_cursor_range_ms(
                cursor_field="hs_lastmodifieddate",
                start_ms=self._ms(start),
                end_ms=self._ms(end),
            )
        )
        if page_token:
            builder = builder.with_page_token(page_token)
        return builder.build()

    @property
    def response_builder(self):
        return HubspotStreamResponseBuilder.for_stream(self.STREAM_NAME)

    def response(self, id: Optional[str] = None, with_pagination: bool = False):
        record = (
            self.record_builder(self.STREAM_NAME, FieldPath(self.CURSOR_FIELD))
            .with_field(FieldPath(self.CURSOR_FIELD), self.dt_str(self.updated_at()))
            .with_field(FieldPath("id"), id if id else self.OBJECT_ID)
        )
        response = self.response_builder.with_record(record)
        if with_pagination:
            response = response.with_pagination()
        return response.build()

    def _set_up_oauth(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)

    def _set_up_requests(
        self, http_mocker: HttpMocker, with_oauth: bool = False, with_dynamic_schemas: bool = True, entities: Optional[List[str]] = None
    ):
        if with_oauth:
            self._set_up_oauth(http_mocker)
        self.mock_custom_objects(http_mocker)
        self.mock_properties(http_mocker, self.OBJECT_TYPE, self.MOCK_PROPERTIES_FOR_SCHEMA_LOADER)
        if with_dynamic_schemas:
            self.mock_dynamic_schema_requests(http_mocker, entities)

    def _mock_associations_with_stream_builder(
        self,
        http_mocker,
        parent_entity: str,           # e.g. "calls" / "meetings"
        association_name: str,        # e.g. "contacts"
        record_ids: List[str],        # primary ids from the page, as strings
        to_ids_per_record: Dict[str, List[int]],  # map primary id -> list of associated ids
    ):
        """
        Mocks:
          POST https://api.hubapi.com/crm/v4/associations/{parent_entity}/{association_name}/batch/read

        Response body mirrors HubSpot's shape but only includes:
          { "status": "COMPLETE", "results": [ { "from": {"id": ...}, "to": [ { "toObjectId": ..., "associationTypes": [...] }, ... ] }, ... ] }
        We intentionally skip `errors` / `numErrors`.
        """
        req = (
            AssociationsBatchReadRequestBuilder()
            .for_parent(parent_entity)
            .for_association(association_name)
            .with_ids(record_ids)
            .build()
        )

        results = []
        for rid in record_ids:
            to_list = [
                {
                    "toObjectId": int(x),
                    "associationTypes": [
                        {"category": "HUBSPOT_DEFINED", "typeId": 200, "label": None}
                    ],
                }
                for x in to_ids_per_record.get(rid, [])
            ]
            results.append({"from": {"id": str(rid)}, "to": to_list})

        body = json.dumps({"status": "COMPLETE", "results": results})
        self.mock_response(http_mocker, req, HttpResponse(status_code=200, body=body), method="post")

    def _mock_all_associations_for_ids(self, http_mocker: HttpMocker, parent_entity: str, record_ids: List[str]):
        """
        Convenience wrapper: for each association, create two deterministic associated IDs per record.
        """
        to_map = {rid: [int(rid) + 1, int(rid) + 2] for rid in record_ids if rid.isdigit()}
        for assoc in self.ASSOCIATIONS:
            self._mock_associations_with_stream_builder(
                http_mocker,
                parent_entity=parent_entity,
                association_name=assoc,
                record_ids=record_ids,
                to_ids_per_record=to_map,
            )
