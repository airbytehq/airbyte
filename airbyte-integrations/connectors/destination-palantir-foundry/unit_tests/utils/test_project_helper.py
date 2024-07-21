import unittest

from mockito import mock, when

from destination_palantir_foundry.foundry_api import compass
from destination_palantir_foundry.foundry_api.compass import GetPathsResponse, MaybeDecoratedResource
from destination_palantir_foundry.utils.project_helper import ProjectHelper
from unit_tests.fixtures import PROJECT_RID


class TestProjectHelper(unittest.TestCase):
    def setUp(self):
        self.compass = mock(compass.Compass)

        self.project_helper = ProjectHelper(self.compass)

    def test_maybeGetResourceByName_cannotFindParentPath_raises(self):
        resource_name = "resource_name"

        when(self.compass).get_paths([PROJECT_RID]).thenReturn(GetPathsResponse({}))

        with self.assertRaises(ValueError):
            self.project_helper.maybe_get_resource_by_name(PROJECT_RID, resource_name)

    def test_maybeGetResourceByName_parentPathExists_getsResourceFromCompass(self):
        resource_name = "resource_name"

        paths = {
            PROJECT_RID: "path"
        }
        when(self.compass).get_paths([PROJECT_RID]).thenReturn(GetPathsResponse(paths))
        when(self.compass).get_resource_by_path(f"{paths[PROJECT_RID]}/{resource_name}").thenReturn(MaybeDecoratedResource(None))

        result = self.project_helper.maybe_get_resource_by_name(PROJECT_RID, resource_name)

        self.assertEqual(result, None)
