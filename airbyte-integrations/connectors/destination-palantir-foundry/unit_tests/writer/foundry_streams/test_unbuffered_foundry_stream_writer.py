import unittest
from mockito import unstub, mock, when
from destination_palantir_foundry.foundry_api import compass, stream_catalog
from destination_palantir_foundry.writer.foundry_streams.unbuffered_foundry_stream_writer import UnbufferedFoundryStreamWriter
from unit_tests.fixtures import PROJECT_RID, NAMESPACE, STREAM_NAME


class TestUnbufferedFoundryStreamWriter(unittest.TestCase):

    def setUp(self):
        self.compass = mock(compass.Compass)
        self.stream_catalog = mock(stream_catalog.StreamCatalog)

        self.unbuffered_foundry_stream_writer = UnbufferedFoundryStreamWriter(
            self.compass, self.stream_catalog, PROJECT_RID)

    def test_ensureRegistered_cannotFindParentPath_raises(self):
        when(self.compass).get_paths([PROJECT_RID]).thenReturn({})

        with self.assertRaises(ValueError):
            self.unbuffered_foundry_stream_writer.ensure_registered(
                NAMESPACE, STREAM_NAME)

    def test_ensureRegistered_existingFoundryStream_doesNotCreateNew(self):
        pass

    def test_ensureRegistered_noExistingFoundryStream_createsNew(self):
        pass
