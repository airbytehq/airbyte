#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, List

from dagger import Container, Directory
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.secrets import Secret
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


def _get_erd_folder(code_directory: Path) -> Path:
    path = code_directory / "erd"
    if not path.exists():
        path.mkdir()
    return path


class GenerateDbml(Step):
    context: ConnectorContext

    title = "Generate DBML file"

    def __init__(self, context: PipelineContext, skip_relationship_generation: bool) -> None:
        super().__init__(context)
        self._skip_relationship_generation = skip_relationship_generation

    async def _run(self, connector_to_discover: Container) -> StepResult:
        if not self._skip_relationship_generation and not self.context.genai_api_key:
            raise ValueError("GENAI_API_KEY needs to be provided if the relationship generation is not skipped")

        discovered_catalog = await self._get_discovered_catalog(connector_to_discover)

        connector_directory = await self.context.get_connector_dir()
        command = ["poetry", "run", "erd", "--source-path", "/source", "--source-technical-name", self.context.connector.technical_name]
        if self._skip_relationship_generation:
            command.append("--skip-llm-relationships")

        erd_directory = self._build_erd_container(connector_directory, discovered_catalog).with_exec(command).directory("/source/erd")
        await (erd_directory.export(str(_get_erd_folder(self.context.connector.code_directory))))

        return StepResult(step=self, status=StepStatus.SUCCESS, output=erd_directory)

    async def _get_discovered_catalog(self, connector_to_discover: Container) -> str:
        source_config_path_in_container = "/data/config.json"
        discover_output = (
            await connector_to_discover.with_new_file(source_config_path_in_container, contents=self._get_default_config().value)
            .with_exec(["discover", "--config", source_config_path_in_container])
            .stdout()
        )
        return self._get_schema_from_discover_output(discover_output)

    def _get_default_config(self) -> Secret:
        if not self.context.local_secret_store:
            raise ValueError("Expecting local secret store to be set up but couldn't find it")

        filtered_secrets = [secret for secret in self.context.local_secret_store.get_all_secrets() if secret.file_name == "config.json"]
        if not filtered_secrets:
            raise ValueError("Expecting at least one secret to match name `config.json`")
        elif len(filtered_secrets) > 1:
            self.logger.warning(
                f"Expecting only one secret with name `config.json but got {len(filtered_secrets)}. Will take the first one in the list."
            )

        return filtered_secrets[0]

    @staticmethod
    def _get_schema_from_discover_output(discover_output: str) -> str:
        for line in discover_output.split("\n"):
            json_line = json.loads(line)
            if json_line.get("type") == "CATALOG":
                return json.dumps(json.loads(line).get("catalog"))
        raise ValueError("No catalog was found in output")

    def _build_erd_container(self, connector_directory: Directory, discovered_catalog: str) -> Container:
        """Create a container to run ERD generation."""
        container = with_poetry(self.context)
        if self.context.genai_api_key:
            container = container.with_secret_variable("GENAI_API_KEY", self.context.genai_api_key.as_dagger_secret(self.dagger_client))

        container = (
            container.with_mounted_directory("/source", connector_directory)
            .with_new_file("/source/erd/discovered_catalog.json", contents=discovered_catalog)
            .with_mounted_directory("/app", self.context.erd_package_dir)
            .with_workdir("/app")
        )

        return container.with_exec(["poetry", "lock", "--no-update"]).with_exec(["poetry", "install"])


class UploadDbmlSchema(Step):
    context: ConnectorContext

    title = "Upload DBML file to dbdocs.io"

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self, erd_directory: Directory) -> StepResult:
        if not self.context.dbdocs_token:
            raise ValueError(
                "In order to publish to dbdocs, DBDOCS_TOKEN needs to be provided. Either pass the value or skip the publish step"
            )

        dbdocs_container = (
            self.dagger_client.container()
            .from_("node:lts-bullseye-slim")
            .with_exec(["npm", "install", "-g", "dbdocs"])
            .with_env_variable("DBDOCS_TOKEN", self.context.dbdocs_token.value)
            .with_workdir("/airbyte_dbdocs")
            .with_file("/airbyte_dbdocs/dbdocs.dbml", erd_directory.file("source.dbml"))
        )

        db_docs_build = ["dbdocs", "build", "dbdocs.dbml", f"--project={self.context.connector.technical_name}"]
        await dbdocs_container.with_exec(db_docs_build).stdout()
        # TODO: produce link to dbdocs in output logs

        return StepResult(step=self, status=StepStatus.SUCCESS)


async def run_connector_generate_erd_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    skip_steps: List[str],
) -> Report:
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]
    steps_to_run: STEP_TREE = []

    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.DBML_FILE,
                step=GenerateDbml(context, CONNECTOR_TEST_STEP_ID.LLM_RELATIONSHIPS in skip_steps),
                args=lambda results: {"connector_to_discover": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
            ),
        ]
    )

    if CONNECTOR_TEST_STEP_ID.PUBLISH_ERD not in skip_steps:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.PUBLISH_ERD,
                    step=UploadDbmlSchema(context),
                    args=lambda results: {"erd_directory": results[CONNECTOR_TEST_STEP_ID.DBML_FILE].output},
                    depends_on=[CONNECTOR_TEST_STEP_ID.DBML_FILE],
                ),
            ]
        )

    return await run_connector_steps(context, semaphore, steps_to_run)
