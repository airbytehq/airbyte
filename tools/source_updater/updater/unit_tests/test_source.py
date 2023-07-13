import json
import os
import pytest
from pyfakefs.fake_filesystem_unittest import TestCase
from unittest.mock import Mock

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from updater.config import Config
from updater.source import SourceRepository


A_CONFIG_NAME = "a-config-name"
A_CONFIG_FILE_PATH = "a-config-file.json"
SOURCE_NAME = "source-toto"
SOURCE_DIRECTORY_PATH = f"airbyte-integrations/connectors/{SOURCE_NAME}"
CATALOG_PATH = f"{SOURCE_DIRECTORY_PATH}/integration_tests/configured_catalog.json"
SCHEMAS_PATH = f"{SOURCE_DIRECTORY_PATH}/source_toto/schemas"
MANIFEST_PATH = f"{SOURCE_DIRECTORY_PATH}/source_toto/manifest.yaml"
VALID_CATALOG_JSON = '{"streams":[{"stream":{"name":"customers","json_schema":{},"supported_sync_modes":["full_refresh"]},"sync_mode":"full_refresh","destination_sync_mode":"overwrite"}]}'


class SourceRepositoryTestCase(TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self._repo = SourceRepository()
        self._secret_manager = self.mocker.patch("updater.source.SecretsManager")

    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_given_source_exists_when_exists_then_return_true(self):
        self.fs.create_dir(f"airbyte-integrations/connectors/{SOURCE_NAME}")
        assert self._repo.exists(SOURCE_NAME)

    def test_given_source_does_not_exist_when_exists_then_return_false(self):
        assert not self._repo.exists(SOURCE_NAME)

    def test_given_catalog_when_fetch_catalog_then_return_configured_catalog(self):
        self.fs.create_file(CATALOG_PATH, contents=VALID_CATALOG_JSON)
        catalog = self._repo.fetch_catalog(SOURCE_NAME)
        assert len(catalog.streams) == 1

    def test_given_catalog_is_not_valid_catalog_when_fetch_catalog_then_raise_error(self):
        self.fs.create_file(CATALOG_PATH, contents='{"not a valid catalog": 1}',)
        with pytest.raises(ValueError):
            self._repo.fetch_catalog(SOURCE_NAME)

    def test_given_catalog_file_does_not_exist_when_fetch_catalog_then_raise_error(self):
        with pytest.raises(FileNotFoundError):
            self._repo.fetch_catalog(SOURCE_NAME)

    def test_given_folder_exists_when_update_catalog_then_create_catalog_file(self):
        self.fs.create_dir(os.path.dirname(CATALOG_PATH))
        self._repo.update_catalog(SOURCE_NAME, ConfiguredAirbyteCatalog.parse_raw(VALID_CATALOG_JSON))
        with open(CATALOG_PATH, "r") as saved_catalog:
            assert json.load(saved_catalog) == json.loads(VALID_CATALOG_JSON)

    def test_given_folder_does_not_exist_when_update_catalog_then_create_catalog_file(self):
        self.fs.create_dir(os.path.dirname(CATALOG_PATH))
        self._repo.update_catalog(SOURCE_NAME, ConfiguredAirbyteCatalog.parse_raw(VALID_CATALOG_JSON))
        with open(CATALOG_PATH, "r") as saved_catalog:
            assert json.load(saved_catalog) == json.loads(VALID_CATALOG_JSON)

    def test_given_schemas_folder_with_files_when_delete_schemas_then_delete(self):
        self.fs.create_file(os.path.join(SCHEMAS_PATH, "a-file.json"), contents='{"any_schema": 1}')
        self.fs.create_file(os.path.join(SCHEMAS_PATH, "another-file.json"), contents='{"any_schema": 1}')
        self._repo.delete_schemas_folder(SOURCE_NAME)
        assert not os.path.exists(SCHEMAS_PATH)

    def test_given_schemas_folder_with_folders_when_delete_schemas_then_delete(self):
        self.fs.create_file(os.path.join(SCHEMAS_PATH, "a-folder", "a-file.json"))
        self._repo.delete_schemas_folder(SOURCE_NAME)
        assert not os.path.exists(SCHEMAS_PATH)

    def test_given_no_schemas_folder_when_delete_schemas_then_do_nothing(self):
        self._repo.delete_schemas_folder(SOURCE_NAME)
        # if it does raise an exception here, we're happy

    def test_given_manifest_folder_does_not_exist_when_write_manifest_then_raise_error(self):
        source = Mock(spec=ManifestDeclarativeSource)
        source.resolved_manifest = {"streams": ["a stream", "another stream"]}

        with pytest.raises(FileNotFoundError):
            self._repo.write_manifest(SOURCE_NAME, source)

    def test_when_write_manifest_then_delete_metadata_and_save_manifest(self):
        self.fs.create_dir(os.path.dirname(MANIFEST_PATH))
        source = Mock(spec=ManifestDeclarativeSource)
        source.resolved_manifest = {
            "streams": ["a stream", "another stream"],
            "metadata": {"some metadata": "metadata value"}
        }

        self._repo.write_manifest(SOURCE_NAME, source)

        with open(MANIFEST_PATH, "r") as manifest_file:
            assert "metadata" not in manifest_file.read()

    def test_given_config_is_file_when_upsert_secrets_then_create_files_and_call_secret_manager(self):
        os.environ["GCP_GSM_CREDENTIALS"] = '{"gsm_credentials": "actual credentials"}'
        self.fs.create_dir(SOURCE_DIRECTORY_PATH)
        content = '{"any_config": 1}'

        self._repo.upsert_secrets(SOURCE_NAME, {Config(A_CONFIG_NAME, json.loads(content))})

        with open(os.path.join(SOURCE_DIRECTORY_PATH, "secrets", "updated_configurations", A_CONFIG_NAME + ".json")) as secret_file:
            assert secret_file.read() == content
        self._secret_manager.return_value.update_secrets.assert_called_once_with(self._secret_manager.return_value.read_from_gsm.return_value)

    def test_given_gsm_credentials_not_present_when_upsert_secrets_then_raise_error(self):
        del os.environ["GCP_GSM_CREDENTIALS"]
        self.fs.create_file(A_CONFIG_FILE_PATH, contents='{"any_config": "config value"}')

        with pytest.raises(KeyError):
            self._repo.upsert_secrets(SOURCE_NAME, {Config(A_CONFIG_NAME, {})})
