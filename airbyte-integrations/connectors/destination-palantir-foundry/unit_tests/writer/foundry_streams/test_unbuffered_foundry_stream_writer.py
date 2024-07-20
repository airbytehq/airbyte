import unittest
from mockito import unstub, mock, when, verifyZeroInteractions, verify
from destination_palantir_foundry.foundry_api import compass, stream_catalog
from destination_palantir_foundry.writer.foundry_streams.unbuffered_foundry_stream_writer import UnbufferedFoundryStreamWriter
from unit_tests.fixtures import PROJECT_RID, NAMESPACE, STREAM_NAME, DATASET_RID
from destination_palantir_foundry.utils.resource_names import get_foundry_resource_name


class TestUnbufferedFoundryStreamWriter(unittest.TestCase):

    def setUp(self):
        self.compass = mock(compass.Compass)
        self.stream_catalog = mock(stream_catalog.StreamCatalog, strict=False)

        self.unbuffered_foundry_stream_writer = UnbufferedFoundryStreamWriter(
            self.compass, self.stream_catalog, PROJECT_RID)

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

        verifyZeroInteractions(self.stream_catalog)

    def test_ensureRegistered_noExistingFoundryStream_createsNew(self):
        project_path = "/some/path"
        get_paths_response = {}
        get_paths_response[PROJECT_RID] = project_path
        when(self.compass).get_paths(
            [PROJECT_RID]).thenReturn(get_paths_response)

        resource_name = get_foundry_resource_name(NAMESPACE, STREAM_NAME)

        when(self.compass).get_resource_by_path(
            f"{project_path}/{resource_name}").thenReturn(None)

        self.unbuffered_foundry_stream_writer.ensure_registered(
            NAMESPACE, STREAM_NAME)

        verify(self.stream_catalog, times=1).create_stream(
            PROJECT_RID, resource_name)
