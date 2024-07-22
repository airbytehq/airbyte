import unittest

from mockito import unstub, mock, when, verifyZeroInteractions, verify

from destination_palantir_foundry.foundry_api import compass, stream_catalog, stream_proxy, foundry_metadata
from destination_palantir_foundry.foundry_api.stream_catalog import MaybeGetStreamResponse
from destination_palantir_foundry.foundry_schema.providers import stream_schema_provider
from destination_palantir_foundry.utils import project_helper
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer.foundry_streams import foundry_stream_buffer_registry
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_buffer_registry import BufferRegistryEntry
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_writer import FoundryStreamWriter
from unit_tests.fixtures import PROJECT_RID, NAMESPACE, STREAM_NAME, MINIMAL_CONFIGURED_AIRBYTE_STREAM, DATASET_RID, \
    CREATE_STREAM_OR_VIEW_RESPONSE, MINIMAL_AIRBYTE_STREAM, \
    MINIMAL_AIRBYTE_RECORD_MESSAGE, VIEW_RID, GET_STREAM_RESPONSE, FOUNDRY_SCHEMA


class TestUnbufferedFoundryStreamWriter(unittest.TestCase):

    def setUp(self):
        self.project_helper = mock(project_helper.ProjectHelper, strict=False)
        self.stream_catalog = mock(stream_catalog.StreamCatalog, strict=False)
        self.stream_proxy = mock(stream_proxy.StreamProxy, strict=False)
        self.foundry_metadata = mock(
            foundry_metadata.FoundryMetadata, strict=False)
        self.buffer_registry = mock(
            foundry_stream_buffer_registry.FoundryStreamBufferRegistry, strict=False)
        self.stream_schema_provider = mock(
            stream_schema_provider.StreamSchemaProvider, strict=False)

        self.foundry_stream_writer = FoundryStreamWriter(
            self.project_helper,
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
        resource_name = get_foundry_resource_name(
            MINIMAL_CONFIGURED_AIRBYTE_STREAM.stream.namespace, MINIMAL_CONFIGURED_AIRBYTE_STREAM.stream.name)

        when(self.project_helper).maybe_get_resource_by_name(PROJECT_RID, resource_name).thenRaise(ValueError())

        with self.assertRaises(ValueError):
            self.foundry_stream_writer.ensure_registered(
                MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verifyZeroInteractions(self.buffer_registry)
        verifyZeroInteractions(self.stream_catalog)
        verifyZeroInteractions(self.stream_proxy)
        verifyZeroInteractions(self.foundry_metadata)
        verifyZeroInteractions(self.buffer_registry)
        verifyZeroInteractions(self.stream_schema_provider)

    def test_ensureRegistered_existingResourceNotStream_raises(self):
        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.project_helper).maybe_get_resource_by_name(PROJECT_RID, resource_name).thenReturn(
            compass.DecoratedResource(rid=DATASET_RID, name=resource_name)
        )
        when(self.stream_catalog).get_stream(DATASET_RID).thenReturn(MaybeGetStreamResponse(None))

        with self.assertRaises(ValueError):
            self.foundry_stream_writer.ensure_registered(
                MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verifyZeroInteractions(self.foundry_metadata)

    def test_ensureRegistered_existingFoundryStream_doesNotCreateNew(self):
        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.project_helper).maybe_get_resource_by_name(PROJECT_RID, resource_name).thenReturn(
            compass.DecoratedResource(rid=DATASET_RID, name=resource_name)
        )
        when(self.stream_catalog).get_stream(DATASET_RID).thenReturn(GET_STREAM_RESPONSE)

        when(self.stream_schema_provider).get_foundry_stream_schema(MINIMAL_CONFIGURED_AIRBYTE_STREAM.stream).thenReturn(FOUNDRY_SCHEMA)

        self.foundry_stream_writer.ensure_registered(
            MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verify(self.buffer_registry).register_foundry_stream(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name, DATASET_RID, VIEW_RID, FOUNDRY_SCHEMA,
            MINIMAL_CONFIGURED_AIRBYTE_STREAM)
        verifyZeroInteractions(self.foundry_metadata)
        verifyZeroInteractions(self.stream_proxy)

    def test_ensureRegistered_noExistingFoundryStream_createsNewAndAddsSchema(self):
        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.project_helper).maybe_get_resource_by_name(PROJECT_RID, resource_name).thenReturn(None)

        when(self.stream_catalog).create_stream(PROJECT_RID,
                                                resource_name).thenReturn(CREATE_STREAM_OR_VIEW_RESPONSE)

        when(self.stream_schema_provider).get_foundry_stream_schema(MINIMAL_CONFIGURED_AIRBYTE_STREAM.stream).thenReturn(FOUNDRY_SCHEMA)

        self.foundry_stream_writer.ensure_registered(
            MINIMAL_CONFIGURED_AIRBYTE_STREAM)

        verify(self.buffer_registry, times=1).register_foundry_stream(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name, DATASET_RID, VIEW_RID, FOUNDRY_SCHEMA,
            MINIMAL_CONFIGURED_AIRBYTE_STREAM)
        verify(self.stream_catalog, times=1)
        verify(self.foundry_metadata, times=1).put_schema(
            DATASET_RID, FOUNDRY_SCHEMA)

    def test_addRecord_noRegisteredDataset_raises(self):
        when(self.buffer_registry).get(
            NAMESPACE, STREAM_NAME).thenReturn(None)

        with self.assertRaises(ValueError):
            self.foundry_stream_writer.add_record(
                MINIMAL_AIRBYTE_RECORD_MESSAGE)

        verifyZeroInteractions(self.stream_proxy)

    def test_addRecord_registeredDataset_addsToBuffer(self):
        when(self.buffer_registry).get(
            NAMESPACE, STREAM_NAME).thenReturn(
            BufferRegistryEntry(DATASET_RID, VIEW_RID, [], FOUNDRY_SCHEMA, MINIMAL_CONFIGURED_AIRBYTE_STREAM))

        record = {"test": 1}

        self.foundry_stream_writer.add_record(
            MINIMAL_AIRBYTE_RECORD_MESSAGE)

        verify(self.buffer_registry, times=1).add_record_to_buffer(MINIMAL_AIRBYTE_RECORD_MESSAGE)

    def test_ensureFlushed_noBufferedRecords_doesNothing(self):
        when(self.buffer_registry).flush_buffer(
            NAMESPACE, STREAM_NAME).thenReturn(
            BufferRegistryEntry(DATASET_RID, VIEW_RID, [], FOUNDRY_SCHEMA, MINIMAL_CONFIGURED_AIRBYTE_STREAM))

        self.foundry_stream_writer.ensure_flushed(
            NAMESPACE, STREAM_NAME)

        verifyZeroInteractions(self.stream_proxy)

    def test_ensureFlushed_bufferedRecords_pushesToStreamProxy(self):
        entry = BufferRegistryEntry(DATASET_RID, VIEW_RID, [MINIMAL_AIRBYTE_RECORD_MESSAGE], FOUNDRY_SCHEMA,
                                    MINIMAL_CONFIGURED_AIRBYTE_STREAM)
        when(self.buffer_registry).flush_buffer(
            NAMESPACE, STREAM_NAME).thenReturn(entry)

        when(self.stream_schema_provider).get_converted_record(
            MINIMAL_AIRBYTE_RECORD_MESSAGE,
            FOUNDRY_SCHEMA,
            MINIMAL_CONFIGURED_AIRBYTE_STREAM.generation_id
        ).thenReturn({"test": "test"})

        self.foundry_stream_writer.ensure_flushed(
            NAMESPACE, STREAM_NAME)

        verify(self.stream_proxy, times=1).put_json_records(DATASET_RID, VIEW_RID, [{"test": "test"}])
