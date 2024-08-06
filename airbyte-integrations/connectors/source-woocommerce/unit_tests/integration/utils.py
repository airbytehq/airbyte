# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path as FilePath
from typing import List, Optional, MutableMapping, Any

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from source_woocommerce import SourceWoocommerce

from .config import ConfigBuilder


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def config() -> MutableMapping[str, Any]:
    return {
        "api_key": "test_api_key",
        "api_secret": "test_api_secret",
        "shop": "airbyte.store",
        "start_date": "2017-01-01",
    }


def read_output(
        config_builder: ConfigBuilder,
        stream_name: str,
        sync_mode: SyncMode,
        state: Optional[List[AirbyteStateMessage]] = None,
        expecting_exception: Optional[bool] = False,
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode)
    _config = config_builder.build()
    return read(SourceWoocommerce(), _config, _catalog, state, expecting_exception)
