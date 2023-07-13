import glob
import json
import logging
import os
import subprocess
import sys
import yaml
from pydantic.error_wrappers import ValidationError
from typing import Any, List, Mapping

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream

# This is needed as when interpreting SecretsManager, the path used is determined by the VERSION environment variable
os.environ["VERSION"] = "dev"
from ci_credentials import SecretsManager

from updater.yaml_utils import PrettyDumper

_DEFAULT_CONFIG_FILE = "config.json"

logger = logging.getLogger("main")


class SourceRepository:
    def exists(self, source_name: str) -> bool:
        return os.path.exists(self._path_from_name(source_name))

    def fetch_catalog(self, source_name: str) -> ConfiguredAirbyteCatalog:
        try:
            return ConfiguredAirbyteCatalog.parse_obj(BaseConnector.read_config(self._catalog_path(source_name)))
        except ValidationError as error:
            raise ValueError(error)

    def update_catalog(self, source_name: str, catalog: ConfiguredAirbyteCatalog) -> None:
        with open(self._catalog_path(source_name), "w") as catalog_file:
            json.dump(catalog.dict(exclude_none=True), catalog_file, indent=2, default=lambda x: x.value)

    def delete_schemas_folder(self, source_name: str) -> None:
        schemas_folder_path = os.path.join(self._path_from_name(source_name), source_name.replace("-", "_"), "schemas")
        for root, dirs, files in os.walk(schemas_folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        try:
            os.rmdir(os.path.join(schemas_folder_path))
        except FileNotFoundError:
            # Nothing to do here as the directory didn't exist
            pass

    def write_manifest(self, source_name: str, source: ManifestDeclarativeSource) -> None:
        # FIXME This seems very intrusive because it modifies the internal attribute of ManifestDeclarativeSource. We should probably have a
        #  method to explicit this behavior
        if "metadata" in source.resolved_manifest:
            del source.resolved_manifest["metadata"]

        with open(self._manifest_path(source_name), 'w') as outfile:
            yaml.dump(source.resolved_manifest, outfile, sort_keys=False, Dumper=PrettyDumper)

    def upsert_secrets(self, source_name: str, config_path: str) -> None:
        """
        If config_path points to a directory, all json files from this repository will be uploaded. Else, only the file will be uploaded.
        Note that this method will overwrite the content of <source-name>/secrets/updated_configurations since this is how ci_credentials
        works.
        """
        gsm_credentials = json.loads(os.environ['GCP_GSM_CREDENTIALS'])
        if not gsm_credentials:
            raise ValueError("GSM credentials should be set as described in https://github.com/airbytehq/airbyte/blob/master/tools/ci_credentials/README.md")

        self._set_up_config_files(source_name, config_path)

        secret_manager = SecretsManager(
            connector_name=source_name,
            gsm_credentials=gsm_credentials,
        )
        secrets = secret_manager.read_from_gsm()
        secret_manager.update_secrets(secrets)

    def _set_up_config_files(self, source_name: str, config_path: str):
        """
        In order of the current version of SecretManager to update secrets, updated secrets needs to be part of secrets/updated_configurations/*.json
        """
        secrets_folder_path = os.path.join(self._path_from_name(source_name), "secrets")
        updated_config_path = os.path.join(secrets_folder_path, "updated_configurations")
        if not os.path.exists(secrets_folder_path):
            os.mkdir(secrets_folder_path)
        if not os.path.exists(updated_config_path):
            os.mkdir(updated_config_path)

        if not os.path.abspath(config_path).startswith(os.path.abspath(updated_config_path)):
            if os.path.isfile(config_path):
                self._copy_file(config_path, os.path.join(updated_config_path, os.path.basename(config_path)))
            else:
                config_files = glob.glob(os.path.join(config_path, "*.json"))
                for file in config_files:
                    self._copy_file(file, os.path.join(updated_config_path, os.path.basename(file)))

    @staticmethod
    def _copy_file(source_file_path: str, destination_file_path: str):
        with open(source_file_path, 'rb') as source, open(destination_file_path, 'wb') as destination:
            destination.write(source.read())

    def _catalog_path(self, source_name: str) -> str:
        return os.path.join(self._path_from_name(source_name), "integration_tests", "configured_catalog.json")

    def _manifest_path(self, source_name: str) -> str:
        return os.path.join(self._path_from_name(source_name), source_name.replace("-", "_"), "manifest.yaml")

    def _path_from_name(self, source_name: str) -> str:
        return os.path.join("airbyte-integrations", "connectors", source_name)


class CatalogAssembler:
    def assemble(self, manifest_streams: List[Stream]) -> ConfiguredAirbyteCatalog:
        streams: List[ConfiguredAirbyteStream] = []
        for stream in manifest_streams:
            streams.append(
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(
                        name=stream.name,
                        json_schema={},
                        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental] if stream.supports_incremental else [SyncMode.full_refresh]
                    ),
                    # FIXME determine default value in case it is incremental
                    sync_mode=SyncMode.full_refresh,
                    # FIXME determine default value
                    destination_sync_mode=DestinationSyncMode.overwrite,
                )
            )
        return ConfiguredAirbyteCatalog(streams=streams)


def _update_catalog(source_name: str, catalog: ConfiguredAirbyteCatalog, new_manifest_source: Source, config: Mapping[str, Any]):
    # Update catalog if add/remove stream or change sync_modes
    #   Compare current catalog and new to validate add/remove stream
    #   Validate `supported_sync_modes` by checking if stream incremental
    #   default sync_mode?
    catalog_stream_names = {stream.stream.name for stream in catalog.streams}
    logger.debug(f"Streams identified from current {source_name}: {catalog_stream_names}")
    manifest_streams = new_manifest_source.streams(config)
    manifest_catalog = CatalogAssembler().assemble(manifest_streams)
    manifest_stream_names = {stream.stream.name for stream in manifest_catalog.streams}
    logger.debug(f"Streams identified from new implementation: {manifest_stream_names}")

    streams_to_remove = catalog_stream_names - manifest_stream_names
    if streams_to_remove:
        logger.info(f"Removing streams {streams_to_remove}...")
        catalog.streams = list(filter(lambda stream: stream.stream.name in streams_to_remove, catalog.streams))

    streams_to_add = manifest_stream_names - catalog_stream_names
    if streams_to_add:
        logger.info(f"Adding streams {streams_to_add}...")
        for stream in manifest_catalog.streams:
            if stream.stream.name in streams_to_add:
                catalog.streams.append(stream)

    if streams_to_remove or streams_to_add:
        logger.info("Saving new catalog...")
        repo.update_catalog(source_name, catalog)


def _update_manifest(source_name: str, source: ManifestDeclarativeSource) -> None:
    # Update manifest
    #   Delete schemas folder
    #   Remove metadata from manifest
    #   Overwrite manifest.yaml
    logger.info("Deleting schemas folder as schemas are embedded in the manifest...")
    repo.delete_schemas_folder(source_name)
    repo.write_manifest(source_name, source)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Source updated",
    )
    parser.add_argument("--source", type=str, required=True, help="Name of the source. For example, 'source-jira'")
    parser.add_argument("--manifest", type=str, required=True, help="Path to the new yaml manifest file")
    parser.add_argument("--config", type=str, required=True, help="Path to the config file or directory. We recommend using `airbyte-integrations/connectors/<source_name>/secrets/updated_configurations/*.json`")
    parser.add_argument("--debug", default=False, required=False, action='store_true', help="Enable debug logs")

    args = parser.parse_args()
    source_name = args.source
    manifest_path = args.manifest
    config_path = args.config
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, force=True)

    logger.info("Starting the update...")

    repo = SourceRepository()

    # FIXME is there a state of the local git we would like to enforce?
    branch_name = f"source-updater/updating-{source_name}"
    validate_branch_process = subprocess.run(["git", "rev-parse", "--verify", branch_name])
    if validate_branch_process.returncode == 0:
        error_message = f"The target branch `{branch_name}` for the update operations already exist. Please make sure to push those local changes before doing more changes or delete this branch"
        logger.error(error_message)
        sys.exit(error_message)

    if not repo.exists(source_name):
        error_message = "Source does not exist. Please generate it as demonstrated by https://docs.airbyte.com/connector-development/config-based/tutorial/create-source"
        logger.error(error_message)
        sys.exit(error_message)

    catalog = repo.fetch_catalog(source_name)
    new_manifest_source = YamlDeclarativeSource(manifest_path)
    config = BaseConnector.read_config(
        config_path
        if config_path.endswith(_DEFAULT_CONFIG_FILE)
        else os.path.join(config_path, _DEFAULT_CONFIG_FILE)
    )

    _update_catalog(source_name, catalog, new_manifest_source, config)
    _update_manifest(source_name, new_manifest_source)
    repo.upsert_secrets(source_name, config_path)

    # CATs
    #   Update expected records
    pass

    # GitHub PR
    subprocess.run(["git", "checkout", "-b", branch_name])
    subprocess.run(["git", "add", "."])
    # to avoid pushing secrets to GitHub
    subprocess.run(["git", "restore", "--staged", config_path])
    subprocess.run(["git", "commit", "-m", f"Updating {source_name}"])
    subprocess.run(["git", "push", "--set-upstream", "origin", branch_name])

    # Change management
    #   Is there a breaking change?
    #   Version bump
    #   [blocked] Changelogs using PR URL
    #       PyGithub would allow to create a PR automatically but it will require OAuth2 Token Auth. Until then, this will be manual
    pass

    print("Yay!!")
