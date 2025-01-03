# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, Optional

from config_builder import ConfigBuilder
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from source_salesforce import SourceSalesforce

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_API_VERSION = "v57.0"


def _catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceSalesforce:
    return SourceSalesforce(catalog, config, state)


def create_base_url(instance_url: str) -> str:
    return f"{instance_url}/services/data/{_API_VERSION}"


def read(
    stream_name: str,
    sync_mode: SyncMode,
    config_builder: Optional[ConfigBuilder] = None,
    state_builder: Optional[StateBuilder] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = _catalog(stream_name, sync_mode)
    config = config_builder.build() if config_builder else ConfigBuilder().build()
    state = state_builder.build() if state_builder else StateBuilder().build()
    return entrypoint_read(_source(catalog, config, state), config, catalog, state, expecting_exception)


def given_authentication(
    http_mocker: HttpMocker,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    instance_url: str,
    access_token: str = "any_access_token",
) -> None:
    http_mocker.post(
        HttpRequest(
            "https://login.salesforce.com/services/oauth2/token",
            query_params=ANY_QUERY_PARAMS,
            body=f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}",
        ),
        HttpResponse(json.dumps({"access_token": access_token, "instance_url": instance_url})),
    )


def given_stream(http_mocker: HttpMocker, base_url: str, stream_name: str, schema_builder: SalesforceDescribeResponseBuilder) -> None:
    http_mocker.get(
        HttpRequest(f"{base_url}/sobjects"),
        HttpResponse(json.dumps({"sobjects": [{"name": stream_name, "queryable": True}]})),
    )
    http_mocker.get(
        HttpRequest(f"{base_url}/sobjects/{stream_name}/describe"),
        schema_builder.build(),
    )
