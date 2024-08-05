#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, List

from dagger import Container

from connector_ops.utils import ConnectorLanguage  # type: ignore
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext
from pipelines.consts import LOCAL_BUILD_PLATFORM
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.connectors.format import format_prettier
from pipelines.helpers.connectors.yaml import read_yaml, write_yaml
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.models.steps import Step, StepResult, StepStatus
from pipelines.models.secrets import Secret

if TYPE_CHECKING:
    from anyio import Semaphore

import google.generativeai as genai
import dpath


# TODO: how to pass secret in dagger?
API_KEY = "API_KEY"
genai.configure(api_key=API_KEY)


class GenerateErdSchema(Step):
    context: ConnectorContext

    title = "Generate ERD schema using Gemini LLM"

    def __init__(self, context: PipelineContext) -> None:
        super().__init__(context)
        self._model = genai.GenerativeModel('gemini-1.5-flash')

    async def _run(self, connector_to_discover: Container) -> StepResult:
        connector = self.context.connector
        python_path = connector.code_directory
        file_path = Path(os.path.abspath(os.path.join(python_path)))
        discover_output = await connector_to_discover.with_exec(["spec"]).stdout()
        print(discover_output)
        configured_catalog = self._get_schema_from_discover_output(discover_output)
        normalized_catalog = self._normalize_schema_catalog(configured_catalog)
        erd_relations_schema = self._get_relations_from_gemini(source_name=connector.name, catalog=normalized_catalog)
        clean_schema = self._remove_non_existing_relations(normalized_catalog, erd_relations_schema)
        # save erp to source directory
        json.dump(clean_schema, open(file_path / 'erd.json', 'w'), indent=4)

        return StepResult(step=self, status=StepStatus.SUCCESS)

    @staticmethod
    def _get_schema_from_discover_output(discover_output):
        """
        TODO:
        :param discover_output:
        :return:
        """

        schema = {}
        return schema

    @staticmethod
    def _normalize_schema_catalog(schema: dict) -> dict:
        """
        Foreign key cannot be of type object or array, therefore, we can remove these properties.
        :param schema: json_schema in draft7
        :return: json_schema in draft7 with TOP level properties only.
        """
        streams = schema['streams']
        for stream in streams:
            to_rem = dpath.search(stream['json_schema']['properties'], ['**'], afilter=lambda x: isinstance(x, dict) and (
                    'array' in str(x.get('type', '')) or "object" in str(x.get('type', ''))))
            for key in to_rem:
                stream['json_schema']['properties'].pop(key)
        return streams

    def _get_relations_from_gemini(self, source_name: str, catalog: dict) -> dict:
        """

        :param source_name:
        :param gemini_model:
        :param catalog:
        :return: {"streams":[{'name': 'ads', 'relations': {'account_id': 'ad_account.id', 'campaign_id': 'campaigns.id', 'adset_id': 'ad_sets.id'}}, ...]}
        """
        system = "You are an Database developer in charge of communicating well to your users."

        source_desc = """
        You are working on the {source_name} API service. 
    
        The current JSON Schema format is as follows:
        {current_schema}, where "streams" has a list of streams, which represents database tables, and list of properties in each, which in turn, represent DB columns. Streams presented in list are the only available ones.
        Generate and add a `foreign_key` with reference for each field in top level of properties that is helpful in understanding what the data represents and how are streams related to each other. Pay attention to fields ends with '_id'.
        """.format(source_name=source_name, current_schema=catalog)
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
        response_json = json.loads(response.text[8:-3])
        return response_json

    @staticmethod
    def _remove_non_existing_relations(discovered_catalog_schema: dict, relation_dict: dict) -> dict:
        """LLM can sometimes add non-existing relations, so we need check and remove them"""
        all_streams_names = [x.get('name') for x in discovered_catalog_schema.get('streams')]
        for stream in relation_dict['streams']:
            ref_tables = [x.split('.')[0] for x in stream['relations'].values()]
            if non_existing_streams := set(ref_tables) - set(all_streams_names):
                print(f'non_existing_stream was found in {stream["name"]=}: {non_existing_streams}. Removing ...')
                for non_existing_stream in non_existing_streams:
                    keys = dpath.search(stream['relations'], ['**'], afilter=lambda x: x.startswith(non_existing_stream))
                    for key in keys:
                        stream['relations'].pop(key)

        return relation_dict


async def run_connector_generate_erd_schema_pipeline(context: ConnectorTestContext, semaphore: "Semaphore") -> Report:
    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    steps_to_run: STEP_TREE = []

    steps_to_run.append([StepToRun(id=CONNECTOR_TEST_STEP_ID.BUILD, step=BuildConnectorImages(context))])

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.AIRBYTE_ERD_GENERATE,
                step=GenerateErdSchema(context),
                # secrets=context.get_secrets_for_step_id(CONNECTOR_TEST_STEP_ID.AIRBYTE_ERD_GENERATE),
                args=lambda results: {"connector_to_discover": results[CONNECTOR_TEST_STEP_ID.BUILD].output[LOCAL_BUILD_PLATFORM]},
                depends_on=[CONNECTOR_TEST_STEP_ID.BUILD]
            ),
        ]
    )

    return await run_connector_steps(context, semaphore, steps_to_run)
