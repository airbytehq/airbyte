#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional


from dagger import Container, Directory
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore

# TODO: pass secret in dagger?
API_KEY = "API_KEY"

# TODO: pass secret in dagger
DBDOCS_TOKEN = "TOKEN"


def _get_erd_folder(code_directory: Path) -> Path:
    path = code_directory / "erd"
    if not path.exists():
        path.mkdir()
    return path

def _get_dbml_file(code_directory: Path) -> Path:
    return _get_erd_folder(code_directory) / "source.dbml"


class GenerateDbml(Step):
    context: ConnectorContext

    title = "Generate DBML file"

    def __init__(self, context: PipelineContext, skip_relationship_generation: bool) -> None:
        super().__init__(context)
        self._skip_relationship_generation = skip_relationship_generation

    async def _run(self, connector_to_discover: Container) -> StepResult:
        connector = self.context.connector
        python_path = connector.code_directory
        file_path = Path(os.path.abspath(os.path.join(python_path)))

        # TODO extract that in a method
        source_config_path_in_container = "/data/config.json"
        config_secret = open(file_path / "secrets" / "config.json").read()
        discover_output = (
            await connector_to_discover.with_new_file(source_config_path_in_container, contents=config_secret)
            .with_exec(["discover", "--config", source_config_path_in_container])
            .stdout()
        )
        discovered_catalog = self._get_schema_from_discover_output(discover_output)

        connector_directory = await self.context.get_connector_dir()
        command = ["poetry", "run", "erd", "--source-path", "/source"]
        if self._skip_relationship_generation:
            command.append("--skip-llm-relationships")

        await (self._build_erd_container(connector_directory, discovered_catalog)
           .with_exec(command)
           .directory("/source/erd")
           .export(str(_get_erd_folder(python_path)))
       )

        return StepResult(step=self, status=StepStatus.SUCCESS)

    @staticmethod
    def _get_schema_from_discover_output(discover_output: str):
        """
        :param discover_output:
        :return:
        """
        for line in discover_output.split("\n"):
            json_line = json.loads(line)
            if json_line.get("type") == "CATALOG":
                return json.loads(line).get("catalog")
        raise ValueError("No catalog was found in output")

    def _build_erd_container(self, connector_directory: Directory, discovered_catalog) -> Container:
        """Create a container to run ERD generation."""
        container = (
            with_poetry(self.context)
            .with_env_variable("GENAI_API_KEY", API_KEY)  # FIXME pass using context
            .with_mounted_directory("/source", connector_directory)
            .with_new_file("/source/erd/discovered_catalog.json", contents=json.dumps(discovered_catalog))
            .with_mounted_directory("/app", self.context.erd_dir)
            .with_workdir("/app")
        )

        return container.with_exec(["poetry", "lock", "--no-update"]).with_exec(["poetry", "install"])


class UploadDbmlSchema(Step):
    context: ConnectorContext

    title = "Upload DBML file to dbdocs.io"

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    async def _run(self, connector_to_discover: Container = None) -> StepResult:
        connector = self.context.connector
        source_dbml_content = open(_get_dbml_file(connector.code_directory)).read()

        dbdocs_container = await (
            self.dagger_client.container()
            .from_("node:lts-bullseye-slim")
            .with_exec(["npm", "install", "-g", "dbdocs"])
            .with_env_variable("DBDOCS_TOKEN", DBDOCS_TOKEN)
            .with_workdir("/airbyte_dbdocs")
            .with_new_file("/airbyte_dbdocs/dbdocs.dbml", contents=source_dbml_content)
        )

        db_docs_build = ["dbdocs", "build", "dbdocs.dbml", f"--project={connector.technical_name}"]
        output = await dbdocs_container.with_exec(db_docs_build).stdout()
        # TODO: produce link to dbdocs in output logs

        return StepResult(step=self, status=StepStatus.SUCCESS)


async def run_connector_generate_erd_pipeline(context: ConnectorContext, semaphore: "Semaphore", skip_steps: Optional[List[str]] = None) -> Report:
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]
    steps_to_run: STEP_TREE = []
    if not skip_steps:
        skip_steps = []

    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.LLM_RELATIONSHIPS,
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
                    depends_on=[CONNECTOR_TEST_STEP_ID.DBML_FILE],
                ),
            ]
        )

    return await run_connector_steps(context, semaphore, steps_to_run)
