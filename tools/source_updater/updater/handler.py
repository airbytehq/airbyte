import logging
import subprocess
from typing import Set

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from updater.catalog import CatalogMerger
from updater.config import Config
from updater.source import SourceRepository


logger = logging.getLogger("handler")


class SourceUpdaterHandler:
    def __init__(self, source_repository: SourceRepository, catalog_merger: CatalogMerger):
        self._source_repository = source_repository
        self._catalog_merger = catalog_merger

    def handle(self, source_name: str, new_manifest_source: ManifestDeclarativeSource, main_config: Config, other_configs: Set[Config]) -> None:
        # FIXME eventually extract git related command somewhere it makes sense
        # FIXME is there a state of the local git we would like to enforce?
        branch_name = f"source-updater/updating-{source_name}"
        validate_branch_process = subprocess.run(["git", "rev-parse", "--verify", branch_name])
        if validate_branch_process.returncode == 0:
            error_message = f"The target branch `{branch_name}` for the update operations already exist. Please make sure to push those " \
                            f"local changes before doing more changes or delete this branch "
            logger.error(error_message)
            raise ValueError(error_message)

        if not self._source_repository.exists(source_name):
            error_message = "Source does not exist. Please generate it as demonstrated by " \
                            "https://docs.airbyte.com/connector-development/config-based/tutorial/create-source "
            raise ValueError(error_message)

        catalog = self._source_repository.fetch_catalog(source_name)
        is_updated = self._catalog_merger.merge_into_catalog(source_name, catalog, new_manifest_source, main_config)
        if is_updated:
            self._source_repository.update_catalog(source_name, catalog)
        self._update_manifest(source_name, new_manifest_source)
        self._source_repository.upsert_secrets(source_name, other_configs.union({main_config}))

        # CATs
        #   Update expected records
        pass

        # GitHub PR
        subprocess.run(["git", "checkout", "-b", branch_name])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Updating {source_name}"])
        subprocess.run(["git", "push", "--set-upstream", "origin", branch_name])

        # Change management
        #   Is there a breaking change?
        #   Version bump
        #   [blocked] Changelogs using PR URL
        #       PyGithub would allow to create a PR automatically but it will require OAuth2 Token Auth. Until then, this will be manual
        pass

    def _update_manifest(self, source_name: str, source: ManifestDeclarativeSource) -> None:
        # Update manifest
        #   Delete schemas folder
        #   Remove metadata from manifest
        #   Overwrite manifest.yaml
        logger.info("Deleting schemas folder as schemas are embedded in the manifest...")
        self._source_repository.delete_schemas_folder(source_name)
        self._source_repository.write_manifest(source_name, source)
