import unittest
from mockito import unstub, mock, when, verifyZeroInteractions, verify
from destination_palantir_foundry.foundry_api import compass, stream_catalog, stream_proxy
from destination_palantir_foundry.writer.foundry_streams.unbuffered_foundry_stream_writer import UnbufferedFoundryStreamWriter
from unit_tests.fixtures import PROJECT_RID, NAMESPACE, STREAM_NAME, DATASET_RID, CREATE_STREAM_OR_VIEW_RESPONSE
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name
from destination_palantir_foundry.writer import dataset_registry
from unittest.mock import MagicMock


class TestUnbufferedFoundryStreamWriter(unittest.TestCase):

    def setUp(self):
        self.compass = mock(compass.Compass)
        self.stream_catalog = mock(stream_catalog.StreamCatalog, strict=False)
        self.stream_proxy = mock(stream_proxy.StreamProxy, strict=False)
        self.dataset_registry = mock(
            dataset_registry.DatasetRegistry, strict=False)

        self.unbuffered_foundry_stream_writer = UnbufferedFoundryStreamWriter(
            self.compass, self.stream_catalog, self.stream_proxy, self.dataset_registry, PROJECT_RID)

    def tearDown(self) -> None:
        unstub()

    def test_ensureRegistered_cannotFindParentPath_raises(self):
        when(self.compass).get_paths([PROJECT_RID]).thenReturn({})

        with self.assertRaises(ValueError):
            self.unbuffered_foundry_stream_writer.ensure_registered(
                NAMESPACE, STREAM_NAME)

    def test_ensureRegistered_existingFoundryStream_doesNotCreateNew(self):
        project_path = "/some/path"
        get_paths_response = {}
        get_paths_response[PROJECT_RID] = project_path
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(NAMESPACE, STREAM_NAME)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(compass.DecoratedResource(rid=DATASET_RID, name=resource_name))

        self.unbuffered_foundry_stream_writer.ensure_registered(
            NAMESPACE, STREAM_NAME)

        verifyZeroInteractions(self.stream_catalog)
        verify(self.dataset_registry).add(NAMESPACE, STREAM_NAME, DATASET_RID)

    def test_ensureRegistered_noExistingFoundryStream_createsNew(self):
        project_path = "/some/path"
        get_paths_response = {}
        get_paths_response[PROJECT_RID] = project_path
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(NAMESPACE, STREAM_NAME)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(None)

        when(self.stream_catalog).create_stream(PROJECT_RID,
                                                resource_name).thenReturn(CREATE_STREAM_OR_VIEW_RESPONSE)

        self.unbuffered_foundry_stream_writer.ensure_registered(
            NAMESPACE, STREAM_NAME)

        verify(self.dataset_registry, times=1).add(
            NAMESPACE, STREAM_NAME, DATASET_RID)

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
