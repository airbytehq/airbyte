# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from pathlib import Path as FilePath
from typing import List, Optional

from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_protocol.models import AirbyteStateMessage, ConfiguredAirbyteCatalog, SyncMode
from source_woocommerce import SourceWoocommerce

from .config import ConfigBuilder


def catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def config() -> ConfigBuilder:
    return ConfigBuilder()


def source() -> SourceWoocommerce:
    return SourceWoocommerce()


def read_output(
        config_builder: ConfigBuilder,
        stream_name: str,
        sync_mode: SyncMode,
        state: Optional[List[AirbyteStateMessage]] = None,
        expecting_exception: Optional[bool] = False,
) -> EntrypointOutput:
    _catalog = catalog(stream_name, sync_mode)
    _config = config_builder.build()
    return read(source(), _config, _catalog, state, expecting_exception)


def _get_unit_test_folder(execution_folder: str) -> FilePath:
    path = FilePath(execution_folder)
    while path.name != "unit_tests":
        if path.name == path.root or path.name == path.drive:
            raise ValueError(f"Could not find `unit_tests` folder as a parent of {execution_folder}")
        path = path.parent
    return path


def get_json_http_response(resource: str, status_code: int) -> HttpResponse:
    json_path = str(_get_unit_test_folder(__file__) / "resource" / "http" / "response" / f"{resource}")
    with open(json_path) as f:
        response = f.read()
    return HttpResponse(response, status_code)
