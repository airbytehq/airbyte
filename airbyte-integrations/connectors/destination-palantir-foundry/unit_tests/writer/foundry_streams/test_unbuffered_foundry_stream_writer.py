import unittest
from mockito import unstub, mock, when, verifyZeroInteractions, verify
from destination_palantir_foundry.foundry_api import compass, stream_catalog, stream_proxy, foundry_metadata
from destination_palantir_foundry.foundry_schema.providers import stream_schema_provider
from destination_palantir_foundry.writer.foundry_streams.unbuffered_foundry_stream_writer import UnbufferedFoundryStreamWriter
from unit_tests.fixtures import PROJECT_RID, NAMESPACE, STREAM_NAME, DATASET_RID, CREATE_STREAM_OR_VIEW_RESPONSE, MINIMAL_AIRBYTE_STREAM
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer import dataset_registry
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema


class TestUnbufferedFoundryStreamWriter(unittest.TestCase):

    def setUp(self):
        self.compass = mock(compass.Compass)
        self.stream_catalog = mock(stream_catalog.StreamCatalog, strict=False)
        self.stream_proxy = mock(stream_proxy.StreamProxy, strict=False)
        self.foundry_metadata = mock(
            foundry_metadata.FoundryMetadata, strict=False)
        self.dataset_registry = mock(
            dataset_registry.DatasetRegistry, strict=False)
        self.stream_schema_provider = mock(
            stream_schema_provider.StreamSchemaProvider, strict=False)

        self.unbuffered_foundry_stream_writer = UnbufferedFoundryStreamWriter(
            self.compass,
            self.stream_catalog,
            self.stream_proxy,
            self.foundry_metadata,
            self.dataset_registry,
            self.stream_schema_provider,
            PROJECT_RID
        )

    def tearDown(self) -> None:
        unstub()

    def test_ensureRegistered_cannotFindParentPath_raises(self):
        when(self.compass).get_paths([PROJECT_RID]).thenReturn({})

        with self.assertRaises(ValueError):
            self.unbuffered_foundry_stream_writer.ensure_registered(
                MINIMAL_AIRBYTE_STREAM)

        verifyZeroInteractions(self.dataset_registry)
        verifyZeroInteractions(self.stream_catalog)
        verifyZeroInteractions(self.stream_proxy)
        verifyZeroInteractions(self.foundry_metadata)
        verifyZeroInteractions(self.dataset_registry)
        verifyZeroInteractions(self.stream_schema_provider)

    def test_ensureRegistered_existingFoundryStream_doesNotCreateNew(self):
        project_path = "/some/path"
        get_paths_response = {}
        get_paths_response[PROJECT_RID] = project_path
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(compass.DecoratedResource(rid=DATASET_RID, name=resource_name))

        self.unbuffered_foundry_stream_writer.ensure_registered(
            MINIMAL_AIRBYTE_STREAM)

        verify(self.dataset_registry).add(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name, DATASET_RID)
        verifyZeroInteractions(self.stream_catalog)
        verifyZeroInteractions(self.foundry_metadata)
        verifyZeroInteractions(self.stream_proxy)

    def test_ensureRegistered_noExistingFoundryStream_createsNewAndAddsSchema(self):
        project_path = "/some/path"
        get_paths_response = {}
        get_paths_response[PROJECT_RID] = project_path
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(None)

        when(self.stream_catalog).create_stream(PROJECT_RID,
                                                resource_name).thenReturn(CREATE_STREAM_OR_VIEW_RESPONSE)

        mock_schema = FoundrySchema(
            fieldSchemaList=[], dataFrameReaderClass="", customMetadata={})

        when(self.stream_schema_provider).get_foundry_stream_schema(
            MINIMAL_AIRBYTE_STREAM).thenReturn(mock_schema)

        self.unbuffered_foundry_stream_writer.ensure_registered(
            MINIMAL_AIRBYTE_STREAM)

        verify(self.dataset_registry, times=1).add(
            MINIMAL_AIRBYTE_STREAM.namespace, MINIMAL_AIRBYTE_STREAM.name, DATASET_RID)
        verify(self.stream_catalog, times=1)
        verify(self.foundry_metadata, times=1).put_schema(
            DATASET_RID, mock_schema)

    def test_addRecord_noRegisteredDataset_raises(self):
        when(self.dataset_registry).get(
            NAMESPACE, STREAM_NAME).thenReturn(None)

        with self.assertRaises(ValueError):
            self.unbuffered_foundry_stream_writer.add_record(
                NAMESPACE, STREAM_NAME, {})

        verifyZeroInteractions(self.stream_proxy)

    def test_addRecord_registeredDataset_writes(self):
        when(self.dataset_registry).get(
            NAMESPACE, STREAM_NAME).thenReturn(DATASET_RID)

        record = {"test": 1}

        self.unbuffered_foundry_stream_writer.add_record(
            NAMESPACE, STREAM_NAME, record)

        verify(self.stream_proxy, times=1).put_json_record(DATASET_RID, record)

    def test_ensureFlushed_doesNothing(self):
        self.unbuffered_foundry_stream_writer.ensure_flushed(
            NAMESPACE, STREAM_NAME)

        verifyZeroInteractions(self.stream_proxy)
