import copy
from typing import Any, Dict, List, Mapping, Optional

from airbyte_protocol_dataclasses.models import AirbyteStateMessage

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
    TestLimits,
)

SHOULD_NORMALIZE_KEY = "__should_normalize"
SHOULD_MIGRATE_KEY = "__should_migrate"


def build_catalog(stream_name: str) -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )


def should_migrate_manifest(manifest: Mapping[str, Any]) -> bool:
    """
    Determines whether the manifest should be migrated,
    based on the presence of the "__should_migrate" key.

    This flag is set by the UI.
    """
    return manifest.get(SHOULD_MIGRATE_KEY, False)


def should_normalize_manifest(manifest: Mapping[str, Any]) -> bool:
    """
    Determines whether the manifest should be normalized,
    based on the presence of the "__should_normalize" key.

    This flag is set by the UI.
    """
    return manifest.get(SHOULD_NORMALIZE_KEY, False)


def build_source(
    manifest: Dict[str, Any],
    catalog: Optional[ConfiguredAirbyteCatalog],
    config: Mapping[str, Any],
    state: Optional[List[AirbyteStateMessage]],
    record_limit: Optional[int] = None,
    page_limit: Optional[int] = None,
    slice_limit: Optional[int] = None,
) -> ConcurrentDeclarativeSource:
    definition = copy.deepcopy(manifest)

    should_normalize = should_normalize_manifest(manifest)
    if should_normalize:
        del definition[SHOULD_NORMALIZE_KEY]

    should_migrate = should_migrate_manifest(manifest)
    if should_migrate:
        del definition[SHOULD_MIGRATE_KEY]

    return ConcurrentDeclarativeSource(
        catalog=catalog,
        state=state,
        source_config=definition,
        config=config,
        normalize_manifest=should_normalize,
        migrate_manifest=should_migrate,
        emit_connector_builder_messages=True,
        limits=TestLimits(
            max_pages_per_slice=page_limit or TestLimits.DEFAULT_MAX_PAGES_PER_SLICE,
            max_slices=slice_limit or TestLimits.DEFAULT_MAX_SLICES,
            max_records=record_limit or TestLimits.DEFAULT_MAX_RECORDS,
        ),
    )
