import json
import os
import shutil
import yaml
from pydantic.error_wrappers import ValidationError
from typing import Set

from airbyte_cdk.connector import BaseConnector
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from updater.config import Config

# This is needed as when interpreting SecretsManager, the path used is determined by the VERSION environment variable
os.environ["VERSION"] = "dev"
from ci_credentials import SecretsManager  # noqa: E402


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
        shutil.rmtree(schemas_folder_path, ignore_errors=True)

    def write_manifest(self, source_name: str, source: ManifestDeclarativeSource) -> None:
        # FIXME This seems very intrusive because it modifies the internal attribute of ManifestDeclarativeSource. We should probably have a
        #  method to explicit this behavior
        if "metadata" in source.resolved_manifest:
            del source.resolved_manifest["metadata"]

        with open(self._manifest_path(source_name), 'w') as outfile:
            yaml.dump(source.resolved_manifest, outfile, sort_keys=False, Dumper=_PrettyDumper)

    def upsert_secrets(self, source_name: str, configs: Set[Config]) -> None:
        """
        If config_path points to a directory, all json files from this repository will be uploaded. Else, only the file will be uploaded.
        Note that this method will overwrite the content of <source-name>/secrets/updated_configurations since this is how ci_credentials
        works.
        """
        gsm_credentials = json.loads(os.environ['GCP_GSM_CREDENTIALS'])
        if not gsm_credentials:
            raise ValueError("GSM credentials should be set as described in https://github.com/airbytehq/airbyte/blob/master/tools/ci_credentials/README.md")

        self._set_up_config_files(source_name, configs)

        secret_manager = SecretsManager(
            connector_name=source_name,
            gsm_credentials=gsm_credentials,
        )
        secrets = secret_manager.read_from_gsm()
        secret_manager.update_secrets(secrets)

    def _set_up_config_files(self, source_name: str, configs: Set[Config]):
        """
        In order of the current version of SecretManager to update secrets, updated secrets needs to be part of secrets/updated_configurations/*.json
        """
        secrets_folder_path = os.path.join(self._path_from_name(source_name), "secrets")
        updated_config_path = os.path.join(secrets_folder_path, "updated_configurations")
        if not os.path.exists(secrets_folder_path):
            os.mkdir(secrets_folder_path)
        if not os.path.exists(updated_config_path):
            os.mkdir(updated_config_path)

        for config in configs:
            with open(os.path.join(updated_config_path, f"{config.name}.json"), 'w') as destination_file:
                json.dump(config.content, destination_file)

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


import yaml.emitter
import yaml.serializer
import yaml.representer
import yaml.resolver


class _IndentingEmitter(yaml.emitter.Emitter):
    def increase_indent(self, flow=False, indentless=False):
        """Ensure that lists items are always indented."""
        return super().increase_indent(
            flow=False,
            indentless=False,
        )


class _PrettyDumper(
    _IndentingEmitter,
    yaml.serializer.Serializer,
    yaml.representer.Representer,
    yaml.resolver.Resolver,
):
    def __init__(
        self,
        stream,
        default_style=None,
        default_flow_style=False,
        canonical=None,
        indent=None,
        width=None,
        allow_unicode=None,
        line_break=None,
        encoding=None,
        explicit_start=None,
        explicit_end=None,
        version=None,
        tags=None,
        sort_keys=True,
    ):
        _IndentingEmitter.__init__(
            self,
            stream,
            canonical=canonical,
            indent=indent,
            width=width,
            allow_unicode=allow_unicode,
            line_break=line_break,
        )
        yaml.serializer.Serializer.__init__(
            self,
            encoding=encoding,
            explicit_start=explicit_start,
            explicit_end=explicit_end,
            version=version,
            tags=tags,
        )
        yaml.representer.Representer.__init__(
            self,
            default_style=default_style,
            default_flow_style=default_flow_style,
            sort_keys=sort_keys,
        )
        yaml.resolver.Resolver.__init__(self)
