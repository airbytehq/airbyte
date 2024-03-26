import unittest
from typing import List
from unittest.mock import Mock

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode

from updater.catalog import ConfiguredCatalogAssembler, CatalogMerger
from updater.config import Config


A_SOURCE_NAME = "a source name"
A_STREAM_NAME = "a stream name"
A_CONFIG = Config("a config", {})
NO_STREAMS = []


class ConfiguredCatalogAssemblerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._assembler = ConfiguredCatalogAssembler()

    def test_when_assemble_then_return_catalog(self):
        catalog = self._assembler.assemble([
            self._given_stream(name="non incremental stream", supports_incremental=False),
            self._given_stream(name="incremental stream", supports_incremental=True),
        ])

        assert len(catalog.streams) == 2
        assert catalog.streams[0].stream.name == "non incremental stream"
        assert catalog.streams[0].stream.json_schema == {}
        assert catalog.streams[0].stream.supported_sync_modes == [SyncMode.full_refresh]
        assert catalog.streams[0].sync_mode == SyncMode.full_refresh
        assert catalog.streams[0].destination_sync_mode == DestinationSyncMode.overwrite

        assert catalog.streams[1].stream.name == "incremental stream"
        assert catalog.streams[1].stream.json_schema == {}
        assert catalog.streams[1].stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]
        assert catalog.streams[1].sync_mode == SyncMode.full_refresh
        assert catalog.streams[1].destination_sync_mode == DestinationSyncMode.overwrite

    def test_given_no_streams_when_assemble_then_catalog_is_empty(self):
        catalog = self._assembler.assemble([])
        assert len(catalog.streams) == 0

    @staticmethod
    def _given_stream(name: str = "any stream name", supports_incremental: bool = False) -> Stream:
        stream = Mock(spec=Stream)
        stream.name = name
        stream.supports_incremental = supports_incremental
        return stream


class CalatogMergerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._assembler = Mock(spec=ConfiguredCatalogAssembler)
        self._merger = CatalogMerger(self._assembler)

    def test_given_stream_added_when_merge_and_save_then_stream_is_added_to_catalog(self):
        catalog = self._given_catalog_with_streams(NO_STREAMS)
        source = self._given_source_with_stream(["newly added source"])

        is_updated = self._merger.merge_into_catalog(A_SOURCE_NAME, catalog, source, A_CONFIG)

        assert catalog.streams == self._assembler.assemble.return_value.streams
        assert is_updated

    def test_given_stream_removed_when_merge_and_save_then_stream_is_removed_from_catalog(self):
        catalog = self._given_catalog_with_streams(["stream to be removed"])
        source = self._given_source_with_stream(NO_STREAMS)

        is_updated = self._merger.merge_into_catalog(A_SOURCE_NAME, catalog, source, A_CONFIG)

        assert catalog.streams == []
        assert is_updated

    def test_given_no_addition_or_removal_when_merge_and_save_then_do_nothing(self):
        catalog = self._given_catalog_with_streams([A_STREAM_NAME])
        source = self._given_source_with_stream([A_STREAM_NAME])

        is_updated = self._merger.merge_into_catalog(A_SOURCE_NAME, catalog, source, A_CONFIG)

        assert not is_updated

    def _given_catalog_with_streams(self, stream_names: List[str]) -> ConfiguredAirbyteCatalog:
        catalog = Mock(spec=ConfiguredAirbyteCatalog, spec_set=[field for field in ConfiguredAirbyteCatalog.__fields__.keys()])
        catalog.streams = [self._given_catalog_stream(name) for name in stream_names]
        return catalog

    def _given_source_with_stream(self, stream_names: List[str]) -> AbstractSource:
        source = Mock(spec=AbstractSource)
        source.streams.return_value = [self._given_source_stream(name) for name in stream_names]

        catalog = Mock(spec=ConfiguredAirbyteCatalog, spec_set=[field for field in ConfiguredAirbyteCatalog.__fields__.keys()])
        catalog.streams = [self._given_catalog_stream(name) for name in stream_names]
        self._assembler.assemble.return_value = catalog

        return source

    @staticmethod
    def _given_source_stream(name: str) -> Stream:
        stream = Mock(spec=Stream)
        stream.name = name
        return stream

    @staticmethod
    def _given_catalog_stream(name: str) -> ConfiguredAirbyteStream:
        stream = Mock(spec=ConfiguredAirbyteStream, spec_set=[field for field in ConfiguredAirbyteStream.__fields__.keys()])
        stream.stream.name = name
        return stream
