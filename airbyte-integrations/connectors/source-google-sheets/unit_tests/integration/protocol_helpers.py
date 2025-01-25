# Copyright (c) 2025 Airbyte, Inc., all rights reserved.


from typing import Any, Dict, Optional, Tuple

from source_google_sheets import SourceGoogleSheets

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read

from .entrypoint_wrapper_helper import check


def catalog_helper(sync_mode: SyncMode, stream_name: str) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[Dict[str, Any]]) -> SourceGoogleSheets:
    return SourceGoogleSheets(catalog=catalog, config=config, state=state)


def check_helper(config: Dict[str, Any], stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    sync_mode = SyncMode.full_refresh
    catalog = catalog_helper(sync_mode, stream_name)
    source = _source(catalog=catalog, config=config, state={})
    return check(source, config, expecting_exception)


def discover_helper(config: Dict[str, Any], stream_name: str, expecting_exception: bool = False) -> EntrypointOutput:
    sync_mode = SyncMode.full_refresh
    catalog = catalog_helper(sync_mode, stream_name)
    source = _source(catalog=catalog, config=config, state={})
    return discover(source, config, expecting_exception)


def read_helper(
    config: Dict[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    source = _source(catalog=catalog, config=config, state={})
    return read(source, config, catalog, state, expecting_exception)
