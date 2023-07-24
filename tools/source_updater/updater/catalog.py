import logging

from typing import List

from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from updater.config import Config

logger = logging.getLogger("catalog")


class ConfiguredCatalogAssembler:
    @staticmethod
    def assemble(manifest_streams: List[Stream]) -> ConfiguredAirbyteCatalog:
        streams: List[ConfiguredAirbyteStream] = []
        for stream in manifest_streams:
            streams.append(
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name=stream.name,
                        json_schema={},
                        # FIXME validate if/how this field is used for CATs and update accordingly
                        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental] if stream.supports_incremental else [SyncMode.full_refresh]
                    ),
                    # FIXME validate if/how this field is used for CATs and update accordingly
                    sync_mode=SyncMode.full_refresh,
                    # FIXME validate if/how this field is used for CATs and update accordingly
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            )
        return ConfiguredAirbyteCatalog(streams=streams)


class CatalogMerger:
    def __init__(self, catalog_assembler: ConfiguredCatalogAssembler):
        self._catalog_assembler = catalog_assembler

    def merge_into_catalog(self, source_name: str, catalog: ConfiguredAirbyteCatalog, new_source: AbstractSource, config: Config) -> bool:
        """
        The merge does:
        * Fetch the streams from the source
        * Add the streams that are returned by the source but are not present in the catalog
        * Remove the streams that were part of the catalog but are not part of the stream
        * Save the new catalog if there are changes done to the streams

        Note: as of 2023-07-13, we do not update the streams that were already there. For example, if a stream was not increment and is
        being update to be incremental, the `sync_mode` field will not be updated
        """
        catalog_stream_names = {stream.stream.name for stream in catalog.streams}
        logger.debug(f"Streams identified from current {source_name}: {catalog_stream_names}")

        manifest_streams = new_source.streams(config.content)
        manifest_catalog = self._catalog_assembler.assemble(manifest_streams)
        manifest_stream_names = {stream.stream.name for stream in manifest_catalog.streams}
        logger.debug(f"Streams identified from new implementation: {manifest_stream_names}")

        streams_to_remove = catalog_stream_names - manifest_stream_names
        if streams_to_remove:
            logger.info(f"Removing {len(streams_to_remove)} stream(s): {streams_to_remove}...")
            catalog.streams = list(filter(lambda stream: stream.stream.name not in streams_to_remove, catalog.streams))

        streams_to_add = manifest_stream_names - catalog_stream_names
        if streams_to_add:
            logger.info(f"Adding streams {streams_to_add}...")
            for stream in manifest_catalog.streams:
                if stream.stream.name in streams_to_add:
                    catalog.streams.append(stream)

        return bool(streams_to_remove) or bool(streams_to_add)
