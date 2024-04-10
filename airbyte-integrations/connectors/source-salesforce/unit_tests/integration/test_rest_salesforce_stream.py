# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import ConfiguredAirbyteCatalog, SyncMode
from config_builder import ConfigBuilder
from source_salesforce import SourceSalesforce
from source_salesforce.api import UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS

_A_FIELD_NAME = "a_field"
_ACCESS_TOKEN = "an_access_token"
_API_VERSION = "v57.0"
_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_INSTANCE_URL = "https://instance.salesforce.com"
_NOW = datetime.now(timezone.utc)
_REFRESH_TOKEN = "a_refresh_token"
_STREAM_NAME = UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS[0]


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceSalesforce:
    return SourceSalesforce(catalog, config, state)


def _read(
    sync_mode: SyncMode,
    config_builder: Optional[ConfigBuilder] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = StateBuilder().build()
    return read(_source(catalog, config, state), config, catalog, state, expecting_exception)


def _given_authentication(http_mocker: HttpMocker, client_id: str, client_secret: str, refresh_token: str) -> None:
    http_mocker.post(
        HttpRequest(
            "https://login.salesforce.com/services/oauth2/token",
            query_params=ANY_QUERY_PARAMS,
            body=f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}"
        ),
        HttpResponse(json.dumps({"access_token": _ACCESS_TOKEN, "instance_url": _INSTANCE_URL})),
    )


def _given_stream(http_mocker: HttpMocker, stream_name: str, field_name: str) -> None:
    http_mocker.get(
        HttpRequest(f"{_INSTANCE_URL}/services/data/{_API_VERSION}/sobjects"),
        HttpResponse(json.dumps({"sobjects": [{"name": stream_name, "queryable": True}]})),
    )
    http_mocker.get(
        HttpRequest(f"{_INSTANCE_URL}/services/data/{_API_VERSION}/sobjects/AcceptedEventRelation/describe"),
        HttpResponse(json.dumps({"fields": [{"name": field_name, "type": "string"}]})),
    )


@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    def setUp(self) -> None:
        self._config = ConfigBuilder().client_id(_CLIENT_ID).client_secret(_CLIENT_SECRET).refresh_token(_REFRESH_TOKEN)

    @HttpMocker()
    def test_given_error_on_fetch_chunk_when_read_then_retry(self, http_mocker: HttpMocker) -> None:
        _given_authentication(http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN)
        _given_stream(http_mocker, _STREAM_NAME, _A_FIELD_NAME)
        http_mocker.get(
            HttpRequest(f"{_INSTANCE_URL}/services/data/{_API_VERSION}/queryAll?q=SELECT+{_A_FIELD_NAME}+FROM+{_STREAM_NAME}+"),
            [
                HttpResponse("", status_code=406),
                HttpResponse(json.dumps({"records": [{"a_field": "a_value"}]})),
            ]
        )

        output = _read(SyncMode.full_refresh, self._config)

        assert len(output.records) == 1
