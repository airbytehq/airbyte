import pytest
from pytest_mock.plugin import MockerFixture
import unittest
from unittest.mock import call, Mock, PropertyMock

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from updater.catalog import CatalogMerger
from updater.config import Config
from updater.handler import SourceUpdaterHandler
from updater.source import SourceRepository


A_SOURCE_NAME = "a source name"


class SourceUpdaterHandlerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._source_repository = Mock(spec=SourceRepository)
        self._catalog_merger = Mock(spec=CatalogMerger)
        self._handler = SourceUpdaterHandler(self._source_repository, self._catalog_merger)

        self._catalog = Mock(spec=ConfiguredAirbyteCatalog, spec_set=[field for field in ConfiguredAirbyteCatalog.__fields__.keys()])
        self._main_config = Mock(spec=Config)
        self._another_config = Mock(spec=Config)
        self._source = Mock(spec=ManifestDeclarativeSource)
        self._subprocess = self.mocker.patch("updater.handler.subprocess")

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker: MockerFixture) -> None:
        self.mocker = mocker

    def test_handle(self) -> None:
        self._source_repository.fetch_catalog.return_value = self._catalog
        self._catalog_merger.merge_into_catalog.return_value = True

        self._handler.handle(A_SOURCE_NAME, self._source, self._main_config, {self._another_config})

        self._source_repository.update_catalog.assert_called_once_with(A_SOURCE_NAME, self._catalog)
        self._source_repository.delete_schemas_folder.assert_called_once_with(A_SOURCE_NAME)
        self._source_repository.write_manifest.assert_called_once_with(A_SOURCE_NAME, self._source)
        self._source_repository.upsert_secrets.assert_called_once_with(A_SOURCE_NAME, {self._main_config, self._another_config})
        branch_name = f"source-updater/updating-{A_SOURCE_NAME}"
        self._subprocess.run.assert_has_calls([
            call(["git", "checkout", "-b", branch_name]),
            call(["git", "add", "."]),
            call(["git", "commit", "-m", f"Updating {A_SOURCE_NAME}"]),
            call(["git", "push", "--set-upstream", "origin", branch_name]),
        ])

    def test_given_catalog_is_the_same_when_handle_then_do_not_update(self) -> None:
        self._source_repository.fetch_catalog.return_value = self._catalog
        self._catalog_merger.merge_into_catalog.return_value = False

        self._handler.handle(A_SOURCE_NAME, self._source, self._main_config, {self._another_config})

        assert self._source_repository.update_catalog.call_count == 0

    def test_given_branch_name_already_exists_when_handle_then_raise_error(self) -> None:
        self._subprocess.run.return_value = PropertyMock(returncode=0)
        with pytest.raises(ValueError):
            self._handler.handle(A_SOURCE_NAME, self._source, self._main_config, {self._another_config})

    def test_given_source_does_not_exist_when_handle_then_raise_error(self) -> None:
        self._source_repository.exists.return_value = False
        with pytest.raises(ValueError):
            self._handler.handle(A_SOURCE_NAME, self._source, self._main_config, {self._another_config})
