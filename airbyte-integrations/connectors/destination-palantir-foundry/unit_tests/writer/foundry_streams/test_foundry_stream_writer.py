import unittest

from mockito import unstub, mock, when, verifyZeroInteractions, verify

from destination_palantir_foundry.foundry_api import compass, stream_catalog, stream_proxy, foundry_metadata
from destination_palantir_foundry.foundry_api.compass import GetPathsResponse, MaybeDecoratedResource
from destination_palantir_foundry.foundry_api.stream_catalog import MaybeGetStreamResponse
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema
from destination_palantir_foundry.foundry_schema.providers import stream_schema_provider
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer.foundry_streams import foundry_stream_buffer_registry
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_buffer_registry import BufferRegistryEntry
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_writer import FoundryStreamWriter
from unit_tests.fixtures import PROJECT_RID, NAMESPACE, STREAM_NAME, MINIMAL_CONFIGURED_AIRBYTE_STREAM, DATASET_RID, \
    CREATE_STREAM_OR_VIEW_RESPONSE, MINIMAL_AIRBYTE_STREAM, \
    MINIMAL_AIRBYTE_RECORD_MESSAGE, VIEW_RID, GET_STREAM_RESPONSE


class TestUnbufferedFoundryStreamWriter(unittest.TestCase):

    def setUp(self):
        self.compass = mock(compass.Compass)
        self.stream_catalog = mock(stream_catalog.StreamCatalog, strict=False)
        self.stream_proxy = mock(stream_proxy.StreamProxy, strict=False)
        self.foundry_metadata = mock(
            foundry_metadata.FoundryMetadata, strict=False)
        self.buffer_registry = mock(
            foundry_stream_buffer_registry.FoundryStreamBufferRegistry, strict=False)
        self.stream_schema_provider = mock(
            stream_schema_provider.StreamSchemaProvider, strict=False)

        self.foundry_stream_writer = FoundryStreamWriter(
            self.compass,
            self.stream_catalog,
            self.stream_proxy,
            self.foundry_metadata,
            self.buffer_registry,
            self.stream_schema_provider,
            PROJECT_RID
        )

    def tearDown(self) -> None:
        unstub()

    def test_ensureRegistered_cannotFindParentPath_raises(self):
        when(self.compass).get_paths([PROJECT_RID]).thenReturn(GetPathsResponse({}))

        with self.assertRaises(ValueError):
            self.foundry_stream_writer.ensure_registered(
                MINIMAL_AIRBYTE_STREAM)

        verifyZeroInteractions(self.buffer_registry)
        verifyZeroInteractions(self.stream_catalog)
        verifyZeroInteractions(self.stream_proxy)
        verifyZeroInteractions(self.foundry_metadata)
        verifyZeroInteractions(self.buffer_registry)
        verifyZeroInteractions(self.stream_schema_provider)

    def test_ensureRegistered_existingResourceNotStream_raises(self):
        project_path = "/some/path"
        get_paths_response = GetPathsResponse({PROJECT_RID: project_path})
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(
            MaybeDecoratedResource(compass.DecoratedResource(rid=DATASET_RID, name=resource_name)))
        when(self.stream_catalog).get_stream(DATASET_RID).thenReturn(MaybeGetStreamResponse(None))

        with self.assertRaises(ValueError):
            self.foundry_stream_writer.ensure_registered(
                MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verifyZeroInteractions(self.foundry_metadata)

    def test_ensureRegistered_existingFoundryStream_doesNotCreateNew(self):
        project_path = "/some/path"
        get_paths_response = GetPathsResponse({PROJECT_RID: project_path})
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(
            MaybeDecoratedResource(compass.DecoratedResource(rid=DATASET_RID, name=resource_name)))
        when(self.stream_catalog).get_stream(DATASET_RID).thenReturn(GET_STREAM_RESPONSE)

        self.foundry_stream_writer.ensure_registered(
            MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verify(self.buffer_registry).register_foundry_stream(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name, DATASET_RID, VIEW_RID)
        verifyZeroInteractions(self.foundry_metadata)
        verifyZeroInteractions(self.stream_proxy)

    def test_ensureRegistered_noExistingFoundryStream_createsNewAndAddsSchema(self):
        project_path = "/some/path"
        get_paths_response = GetPathsResponse({PROJECT_RID: project_path})
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(MaybeDecoratedResource(None))

        when(self.stream_catalog).create_stream(PROJECT_RID,
                                                resource_name).thenReturn(CREATE_STREAM_OR_VIEW_RESPONSE)

        mock_schema = FoundrySchema(
            fieldSchemaList=[], dataFrameReaderClass="", customMetadata={})

        when(self.stream_schema_provider).get_foundry_stream_schema(
            MINIMAL_AIRBYTE_STREAM).thenReturn(mock_schema)

        a = MINIMAL_CONFIGURED_AIRBYTE_STREAM

        self.foundry_stream_writer.ensure_registered(
            MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verify(self.buffer_registry, times=1).register_foundry_stream(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name, DATASET_RID, VIEW_RID)
        verify(self.stream_catalog, times=1)
        verify(self.foundry_metadata, times=1).put_schema(
            DATASET_RID, mock_schema)

    def test_addRecord_noRegisteredDataset_raises(self):
        when(self.buffer_registry).get(
            NAMESPACE, STREAM_NAME).thenReturn(None)

        with self.assertRaises(ValueError):
            self.foundry_stream_writer.add_record(
                MINIMAL_AIRBYTE_RECORD_MESSAGE)

        verifyZeroInteractions(self.stream_proxy)

    def test_addRecord_registeredDataset_addsToBuffer(self):
        when(self.buffer_registry).get(
            NAMESPACE, STREAM_NAME).thenReturn(DATASET_RID)

        record = {"test": 1}

        when(self.stream_schema_provider).get_converted_record(
            MINIMAL_AIRBYTE_RECORD_MESSAGE).thenReturn(record)

        self.foundry_stream_writer.add_record(
            MINIMAL_AIRBYTE_RECORD_MESSAGE)

        verify(self.buffer_registry, times=1).add_record_to_buffer(MINIMAL_AIRBYTE_RECORD_MESSAGE.namespace,
                                                                   MINIMAL_AIRBYTE_RECORD_MESSAGE.stream,
                                                                   record)

    def test_ensureFlushed_noBufferedRecords_doesNothing(self):
        when(self.buffer_registry).flush_buffer(
            NAMESPACE, STREAM_NAME).thenReturn(BufferRegistryEntry(DATASET_RID, VIEW_RID, []))

        self.foundry_stream_writer.ensure_flushed(
            NAMESPACE, STREAM_NAME)

        verifyZeroInteractions(self.stream_proxy)

    def test_ensureFlushed_bufferedRecords_pushesToStreamProxy(self):
        entry = BufferRegistryEntry(DATASET_RID, VIEW_RID, [{"test": 1}, {"test2": 2}])
        when(self.buffer_registry).flush_buffer(
            NAMESPACE, STREAM_NAME).thenReturn(entry)

        self.foundry_stream_writer.ensure_flushed(
            NAMESPACE, STREAM_NAME)

        verify(self.stream_proxy, times=1).put_json_records(DATASET_RID, VIEW_RID, entry.records)
