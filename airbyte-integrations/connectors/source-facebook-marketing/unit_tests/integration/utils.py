#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from airbyte_cdk.test.catalog_builder import ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from facebook_business.api import _top_level_param_json_encode
from source_facebook_marketing import SourceFacebookMarketing

from .config import ConfigBuilder


def config() -> ConfigBuilder:
    return ConfigBuilder()


def catalog(stream_name: str, sync_mode: SyncMode, json_schema: Optional[Dict[str, any]]) -> ConfiguredAirbyteCatalog:
    streams = [ConfiguredAirbyteStreamBuilder().with_name(stream_name).with_sync_mode(sync_mode).with_json_schema(json_schema or {})]
    return ConfiguredAirbyteCatalog(streams=list(map(lambda builder: builder.build(), streams)))


def source() -> SourceFacebookMarketing:
    return SourceFacebookMarketing()


def read_output(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: Optional[bool] = False,
    json_schema: Optional[Dict[str, any]] = None
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode, json_schema)
    _config = config_builder.build()
    return read(source(), _config, _catalog, state, expecting_exception)


def encode_request_body(body: Dict[str, Any]) -> str:
    body = body.copy()
    return urlencode(_top_level_param_json_encode(body))
