#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import shutil
from pathlib import Path
from typing import Any

import git  # type: ignore
from anyio import Semaphore  # type: ignore
from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.migrate_to_manifest_only.manifest_component_transformer import ManifestComponentTransformer
from pipelines.airbyte_ci.connectors.migrate_to_manifest_only.manifest_resolver import ManifestReferenceResolver
from pipelines.airbyte_ci.connectors.migrate_to_manifest_only.utils import (
    get_latest_base_image,
    readme_for_connector,
    remove_parameters_from_manifest,
)
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.connectors.yaml import read_yaml, write_yaml
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus

## GLOBAL VARIABLES ##

# spec.yaml and spec.json will be removed as part of the conversion. But if they are present, it's fine to convert still.
MANIFEST_ONLY_COMPATIBLE_FILES = ["manifest.yaml", "run.py", "__init__.py", "source.py", "spec.json", "spec.yaml"]
MANIFEST_ONLY_KEEP_FILES = ["manifest.yaml", "metadata.yaml", "icon.svg", "integration_tests", "acceptance-test-config.yml", "secrets"]


## STEPS ##


class CheckIsManifestMigrationCandidate(Step):
    """
    Pipeline step to check if the connector is a candidate for migration to manifest-only.
    """

    context: ConnectorContext
    title: str = "Validate Manifest Migration Candidate"
    airbyte_repo: git.Repo = git.Repo(search_parent_directories=True)

    async def _run(self) -> StepResult:
        connector = self.context.connector
        invalid_files: list = []

        ## 1. Confirm the connector is low-code and not already manifest-only
        if connector.language != ConnectorLanguage.LOW_CODE:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is not a low-code connector.",
            )

        if connector.language == ConnectorLanguage.MANIFEST_ONLY:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stderr="The connector is already in manifest-only format.",
            )

        ## 2. Detect invalid python files in the connector's source directory
        for file in connector.python_source_dir_path.iterdir():
            if file.name not in MANIFEST_ONLY_COMPATIBLE_FILES:
                invalid_files.append(file.name)
        if invalid_files:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout=f"The connector has unrecognized source files: {', '.join(invalid_files)}",
            )

        ## 3. Detect connector class name to make sure it's inherited from source-declarative-manifest
        # and does not override the `streams` method
        connector_source_py = (connector.python_source_dir_path / "source.py").read_text()

        if "YamlDeclarativeSource" not in connector_source_py:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="The connector does not use the YamlDeclarativeSource class.",
            )

        if "def streams" in connector_source_py:
            return StepResult(
                step=self,
                status=StepStatus.SKIPPED,
                stdout="The connector overrides the streams method.",
            )

        # All checks passed, the connector is a valid candidate for migration
        return StepResult(step=self, status=StepStatus.SUCCESS, stdout=f"{connector.technical_name} is a valid candidate for migration.")


class StripConnector(Step):
    """
    Pipeline step to strip a low-code connector to manifest-only files.
    """

    context: ConnectorContext
    title = "Strip Out Unnecessary Files"

    def _delete_directory_item(self, file: Path) -> None:
        """
        Deletes the passed file or folder.
        """
        self.logger.info(f"Deleting {file.name}")
        try:
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()
        except Exception as e:
            raise ValueError(f"Failed to delete {file.name}: {e}")

    def _check_if_non_inline_spec(self, path: Path) -> Path | None:
        """
        Checks if a non-inline spec file exists and return its path.
        """
        spec_file_yaml = path / "spec.yaml"
        spec_file_json = path / "spec.json"

        if spec_file_yaml.exists():
            return spec_file_yaml
        elif spec_file_json.exists():
            return spec_file_json
        return None

    def _read_spec_from_file(self, spec_file: Path) -> dict:
        """
        Grabs the relevant data from a non-inline spec, to be added to the manifest.
        """
        try:
            if spec_file.suffix == ".json":
                with open(spec_file, "r") as file:
                    spec = json.load(file)
            else:
                spec = read_yaml(spec_file)

            documentation_url = spec.get("documentationUrl") or spec.get("documentation_url")
            connection_specification = spec.get("connection_specification") or spec.get("connectionSpecification")
            return {"documentation_url": documentation_url, "connection_specification": connection_specification}

        except Exception as e:
            raise ValueError(f"Failed to read data in spec file: {e}")

    async def _run(self) -> StepResult:
        connector = self.context.connector

        ## 1. Move manifest.yaml to the root level of the directory
        self.logger.info("Moving manifest to the root level of the directory")
        root_manifest_path = connector.code_directory / "manifest.yaml"
        connector.manifest_path.rename(root_manifest_path)

        ## 2. Update the version in manifest.yaml
        try:
            manifest = read_yaml(root_manifest_path)
            manifest["version"] = "4.3.2"
            manifest["type"] = "DeclarativeSource"

            # Resolve $parameters and types with CDK magic
            resolved_manifest = ManifestReferenceResolver().preprocess_manifest(manifest)
            propagated_manifest = ManifestComponentTransformer().propagate_types_and_parameters("", resolved_manifest, {})
            cleaned_manifest = remove_parameters_from_manifest(propagated_manifest)

            write_yaml(cleaned_manifest, root_manifest_path)
        except Exception as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stdout=f"Failed to update version in manifest.yaml: {e}")

        ## 3. Check for non-inline spec files and add the data to manifest.yaml
        spec_file = self._check_if_non_inline_spec(connector.python_source_dir_path)
        if spec_file:
            self.logger.info("Non-inline spec file found. Migrating spec to manifest")
            try:
                spec_data = self._read_spec_from_file(spec_file)
                manifest = read_yaml(root_manifest_path)

                # Confirm the connector does not have both inline and non-inline specs
                if "spec" in manifest:
                    return StepResult(step=self, status=StepStatus.FAILURE, stdout="Connector has both inline and non-inline specs.")

                manifest["spec"] = {
                    "type": "Spec",
                    "documentation_url": spec_data.get("documentation_url"),
                    "connection_specification": spec_data.get("connection_specification"),
                }
                write_yaml(manifest, root_manifest_path)
            except Exception as e:
                return StepResult(step=self, status=StepStatus.FAILURE, stdout=f"Failed to add spec data to manifest.yaml: {e}")

        ## 4. Delete all non-essential files
        try:
            for item in connector.code_directory.iterdir():
                if item.name in MANIFEST_ONLY_KEEP_FILES:
                    continue  # Preserve the allowed files
                else:
                    self._delete_directory_item(item)
        except Exception as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stdout=f"Failed to delete files: {e}")

        return StepResult(step=self, status=StepStatus.SUCCESS, stdout="The connector has been successfully stripped.")


class UpdateManifestOnlyFiles(Step):
    """
    Pipeline step to update connector's metadata, acceptance-test-config and readme to manifest-only.
    """

    context: ConnectorContext
    title = "Update Connector Metadata"

    async def _run(self) -> StepResult:
        connector = self.context.connector

        ## 1. Update the acceptance test config to point to the right spec path
        try:
            acceptance_test_config_data = read_yaml(connector.acceptance_test_config_path)
            # Handle legacy acceptance-test-config:
            if "acceptance_tests" in acceptance_test_config_data:
                acceptance_test_config_data["acceptance_tests"]["spec"]["tests"][0]["spec_path"] = "manifest.yaml"
            else:
                acceptance_test_config_data["tests"]["spec"][0]["spec_path"] = "manifest.yaml"
            write_yaml(acceptance_test_config_data, connector.acceptance_test_config_path)
        except Exception as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stdout=f"Failed to update acceptance-test-config.yml: {e}")

        ## 2. Update the connector's metadata
        self.logger.info("Updating metadata file")
        try:
            metadata = read_yaml(connector.metadata_file_path)

            # Remove any existing language tags and append the manifest-only tag
            tags = metadata.get("data", {}).get("tags", [])
            for tag in tags:
                if "language:" in tag:
                    tags.remove(tag)
            tags.append("language:manifest-only")

            pypi_package = metadata.get("data", {}).get("remoteRegistries", {}).get("pypi")
            if pypi_package:
                pypi_package["enabled"] = False

            # Update the base image
            latest_base_image = get_latest_base_image("airbyte/source-declarative-manifest")
            connector_base_image = metadata.get("data", {}).get("connectorBuildOptions")
            connector_base_image["baseImage"] = latest_base_image

            # Write the changes to metadata.yaml
            write_yaml(metadata, connector.metadata_file_path)
        except Exception as e:
            return StepResult(step=self, status=StepStatus.FAILURE, stdout=f"Failed to update metadata.yaml: {e}")

        ## 3. Update the connector's README
        self.logger.info("Updating README file")
        readme = readme_for_connector(connector.technical_name)

        with open(connector.code_directory / "README.md", "w") as file:
            file.write(readme)

        return StepResult(step=self, status=StepStatus.SUCCESS, stdout="The connector has been successfully migrated to manifest-only.")


## MAIN FUNCTION ##
async def run_connectors_manifest_only_pipeline(context: ConnectorContext, semaphore: "Semaphore", *args: Any) -> Report:

    steps_to_run: STEP_TREE = []
    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.MANIFEST_ONLY_CHECK, step=CheckIsManifestMigrationCandidate(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.MANIFEST_ONLY_STRIP,
                step=StripConnector(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.MANIFEST_ONLY_CHECK],
            )
        ]
    )

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.MANIFEST_ONLY_UPDATE,
                step=UpdateManifestOnlyFiles(context),
                depends_on=[CONNECTOR_TEST_STEP_ID.MANIFEST_ONLY_STRIP],
            )
        ]
    )

    return await run_connector_steps(context, semaphore, steps_to_run)
