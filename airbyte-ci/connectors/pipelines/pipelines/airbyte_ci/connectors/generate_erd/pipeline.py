#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

import dpath
import google.generativeai as genai

from airbyte_protocol.models import AirbyteCatalog
from dagger import Container
from markdown_it import MarkdownIt
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.generate_erd.dbml_assembler import Source, DbmlAssembler
from pipelines.airbyte_ci.connectors.generate_erd.relationships import RelationshipsMerger, Relationships
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus
from pydbml.renderer.dbml.default import DefaultDBMLRenderer

if TYPE_CHECKING:
    from anyio import Semaphore

# TODO: pass secret in dagger?
API_KEY = "API_KEY"
genai.configure(api_key=API_KEY)

# TODO: pass secret in dagger
DBDOCS_TOKEN = "TOKEN"


def _get_erd_folder(code_directory: Path) -> Path:
    path = code_directory / "erd"
    if not path.exists():
        path.mkdir()
    return path

def _get_discovered_catalog_file(code_directory: Path) -> Path:
    return _get_erd_folder(code_directory) / "discovered_catalog.json"

def _get_estimated_relationships_file(code_directory: Path) -> Path:
    return _get_erd_folder(code_directory) / "estimated_relationships.json"

def _get_confirmed_relationships_file(code_directory: Path) -> Path:
    return _get_erd_folder(code_directory) / "confirmed_relationships.json"

def _get_dbml_file(code_directory: Path) -> Path:
    return _get_erd_folder(code_directory) / "source.dbml"


class GenerateErdSchema(Step):
    context: ConnectorContext

    title = "Generate ERD schema using Gemini LLM"

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    async def _run(self, connector_to_discover: Container) -> StepResult:
        connector = self.context.connector
        python_path = connector.code_directory
        file_path = Path(os.path.abspath(os.path.join(python_path)))
        source_config_path_in_container = "/data/config.json"
        config_secret = open(file_path / "secrets" / "config.json").read()
        discover_output = (
            await connector_to_discover.with_new_file(source_config_path_in_container, contents=config_secret)
            .with_exec(["discover", "--config", source_config_path_in_container])
            .stdout()
        )
        discovered_catalog = self._get_schema_from_discover_output(discover_output)

        json.dump(discovered_catalog, open(_get_discovered_catalog_file(connector.code_directory), "w"), indent=4)

        normalized_catalog = self._normalize_schema_catalog(discovered_catalog)
        estimated_relationships = self._get_relations_from_gemini(source_name=connector.name, catalog=normalized_catalog)

        json.dump(estimated_relationships, open(_get_estimated_relationships_file(connector.code_directory), "w"), indent=4)

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

    @staticmethod
    def _normalize_schema_catalog(schema: dict) -> dict:
        """
        Foreign key cannot be of type object or array, therefore, we can remove these properties.
        :param schema: json_schema in draft7
        :return: json_schema in draft7 with TOP level properties only.
        """
        streams = schema["streams"]
        for stream in streams:
            to_rem = dpath.search(
                stream["json_schema"]["properties"],
                ["**"],
                afilter=lambda x: isinstance(x, dict) and ("array" in str(x.get("type", "")) or "object" in str(x.get("type", ""))),
            )
            for key in to_rem:
                stream["json_schema"]["properties"].pop(key)
        return streams

    def _get_relations_from_gemini(self, source_name: str, catalog: dict) -> dict:
        """

        :param source_name:
        :param catalog:
        :return: {"streams":[{'name': 'ads', 'relations': {'account_id': 'ad_account.id', 'campaign_id': 'campaigns.id', 'adset_id': 'ad_sets.id'}}, ...]}
        """
        system = "You are an Database developer in charge of communicating well to your users."

        source_desc = """
You are working on the {source_name} API service.

The current JSON Schema format is as follows:
{current_schema}, where "streams" has a list of streams, which represents database tables, and list of properties in each, which in turn, represent DB columns. Streams presented in list are the only available ones.
Generate and add a `foreign_key` with reference for each field in top level of properties that is helpful in understanding what the data represents and how are streams related to each other. Pay attention to fields ends with '_id'.
        """.format(
            source_name=source_name, current_schema=catalog
        )
        task = """
Please provide answer in the following format:
{streams: [{"name": "<stream_name>", "relations": {"<foreign_key>": "<ref_table.column_name>"} }]}
Pay extra attention that in <ref_table.column_name>" "ref_table" should be one of the list of streams, and "column_name" should be one of the property in respective reference stream.
Limitations:
- Not all tables should have relations
- Reference should point to 1 table only.
- table cannot reference on itself, on other words, e.g. `ad_account` cannot have relations with "ad_account" as a "ref_table"
        """
        response = self._model.generate_content(f"{system} {source_desc} {task}")
        md = MarkdownIt("commonmark")
        tokens = md.parse(response.text)
        response_json = json.loads(tokens[0].content)
        return response_json


class GenerateDbmlSchema(Step):
    context: ConnectorContext

    title = "Generate DBML file from discovered catalog and erd_relation"

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)

    def _get_catalog(self, catalog_path: Path) -> AirbyteCatalog:
        with open(catalog_path, "r") as file:
            try:
                return AirbyteCatalog.parse_obj(json.loads(file.read()))
            except json.JSONDecodeError as error:
                raise ValueError(f"Could not read json file {catalog_path}: {error}. Please ensure that it is a valid JSON.")

    def _get_relationships(self, path: Path) -> Relationships:
        if not path.exists():
            return {"streams": []}

        with open(path, "r") as file:
            return json.load(file)  # type: ignore  # we assume the content of the file matches Relationships

    async def _run(self, connector_to_discover: Container = None) -> StepResult:
        connector = self.context.connector
        python_path = connector.code_directory

        catalog = self._get_catalog(_get_discovered_catalog_file(connector.code_directory))
        source = Source(python_path)
        confirmed_relationships = self._get_relationships(_get_confirmed_relationships_file(connector.code_directory))
        estimated_relationships = self._get_relationships(_get_estimated_relationships_file(connector.code_directory))
        database = DbmlAssembler().assemble(
            source,
            catalog,
            RelationshipsMerger().merge(estimated_relationships, confirmed_relationships)
        )

        with open(_get_dbml_file(connector.code_directory), "w") as f:
            f.write(DefaultDBMLRenderer.render_db(database))

        return StepResult(step=self, status=StepStatus.SUCCESS)


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

    if CONNECTOR_TEST_STEP_ID.LLM_RELATIONSHIPS not in skip_steps:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.LLM_RELATIONSHIPS,
                    step=GenerateErdSchema(context),
                    args=lambda results: {"connector_to_discover": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                    depends_on=[CONNECTOR_TEST_STEP_ID.BUILD],
                ),
            ]
        )

    if CONNECTOR_TEST_STEP_ID.DBML_FILE not in skip_steps:
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.DBML_FILE,
                    step=GenerateDbmlSchema(context),
                    depends_on=[CONNECTOR_TEST_STEP_ID.LLM_RELATIONSHIPS],
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
