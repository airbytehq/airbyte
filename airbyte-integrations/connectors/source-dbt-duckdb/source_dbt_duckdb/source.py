#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, Generator

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source

from .utils.dbt import AirbyteDbtRunner
from dbt.cli.main import RunExecutionResult

class SourceDbtDuckDB(Source):
    """This source will run dbt build operations using the dbt-duckdb adapter."""

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        env_vars = self._get_env_vars(config)
        dbt_runner = AirbyteDbtRunner(
            project_dir=config["dbt_project_path"],
            logger=logger,
            env_vars=env_vars,
        )
        try:
            dbt_runner.invoke("compile")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        For example, given valid credentials to a Postgres database,
        returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """
        streams = []

        # dbt Project Manifest
        streams.append(
            AirbyteStream(
                name="dbt_manifest",
                supported_sync_modes=["full_refresh"],
                source_defined_cursor=True,
                json_schema={  # Example
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "unique_id": {"type": "string"},
                        "name": {
                            "type": "string",
                            "examples": [
                                "model.duckdb_sample_project.my_first_dbt_model",
                                "test.duckdb_sample_project.unique_my_first_dbt_model_id.16e066b321",
                            ],
                        },
                        "resource_type": {
                            "type": "string",
                            "examples": ["model", "test"],
                        },
                        "language": {
                            "type": "string",
                            "examples": ["sql", "python"],
                        },
                    },
                },
            )
        )

        # dbt Build Results
        streams.append(
            AirbyteStream(
                name="dbt_run_results",
                supported_sync_modes=["full_refresh"],
                source_defined_cursor=True,
                json_schema={  # Example
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "result": {"type": "string"},
                    },
                },
            )
        )

        # dbt Test Results
        streams.append(
            AirbyteStream(
                name="dbt_test_results",
                supported_sync_modes=["full_refresh"],
                source_defined_cursor=True,
                json_schema={  # Example
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "result": {"type": "string"},
                    },
                },
            )
        )

        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: AirbyteLogger,
        config: json,
        catalog: ConfiguredAirbyteCatalog,
        state: Dict[str, any],
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
        catalog, and state.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
            the properties of the spec.yaml file
        :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
            returned by discover(), but
        in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
        with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
        :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
            replication in the future from that saved checkpoint.
            This is the object that is provided with state from previous runs and avoid replicating the entire set of
            data every time.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        env_vars = self._get_env_vars(config)
        dbt_runner = AirbyteDbtRunner(
            project_dir=config["dbt_project_path"],
            logger=logger,
            env_vars=env_vars,
        )
        results_list: list[RunExecutionResult] = []

        # Get dbt manifest
        manifest = dbt_runner.generate_manifest()
        for node in manifest.nodes.values():
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream="dbt_manifest",
                    data={
                        "unique_id": node.unique_id,
                        "name": node.name,
                        "resource_type": node.resource_type,
                        "language": node.language,
                    },
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
        if config.get("enabled_steps", {}).get("deps", True):
            dbt_runner.invoke("deps")

        if config.get("enabled_steps", {}).get("seed", False):
            for result in dbt_runner.run_with_results("seed"):
                yield self._airbyte_record_message_from_result(
                    stream="dbt_run_results",
                    result=result,
                )
                results_list.append(result)

        if config.get("enabled_steps", {}).get("source_freshness", False):
            for result in dbt_runner.run_with_results("source freshness"):
                yield self._airbyte_record_message_from_result(
                    stream="dbt_run_results",
                    result=result,
                )
                results_list.append(result)

        if config.get("enabled_steps", {}).get("docs_generate", False):
            dbt_runner.generate_docs()

        if config.get("enabled_steps", {}).get("snapshot", False):
            for result in dbt_runner.run_with_results("snapshot"):
                yield self._airbyte_record_message_from_result(
                    stream="dbt_run_results",
                    result=result,
                )
                results_list.append(result)

        if config.get("enabled_steps", {}).get("run", True):
            for result in dbt_runner.run_with_results("run"):
                yield self._airbyte_record_message_from_result(
                    stream="dbt_run_results",
                    result=result,
                )
                results_list.append(result)

        if config.get("enabled_steps", {}).get("test", True):
            for result in dbt_runner.run_with_results("test"):
                yield self._airbyte_record_message_from_result(
                    stream="dbt_test_results",
                    result=result,
                )
                results_list.append(result)
        
        yield self._airbyte_state_message_from_results(
            stream="dbt_run_results",
            results=results_list,
        )

    def _get_env_vars(self, config: json) -> dict[str, str]:
        env_var_settings = config.get("env_var_settings", [])
        env_var_secrets = config.get("env_var_secrets", [])
        env_vars = {
            **os.environ,
            **{setting["name"]: setting["value"] for setting in env_var_settings},
            **{secret["name"]: secret["value"] for secret in env_var_secrets},
        }
        return env_vars

    def _airbyte_record_message_from_result(
        self,
        stream: str,
        result: RunExecutionResult,
    ) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                stream=stream,
                data={
                    "name": result.node.name,
                    "result": result.status.value,
                },
                emitted_at=int(datetime.now().timestamp()) * 1000,
            ),
    )

    def _airbyte_state_message_from_results(
        self,
        stream: str,
        results: list[RunExecutionResult],
    ) -> AirbyteMessage:
        return AirbyteMessage(
            type=Type.STATE,
            record=AirbyteRecordMessage(
                stream=stream,
                data={"results": [result.to_dict() for result in results]},
                emitted_at=int(datetime.now().timestamp()) * 1000,
            ),
        )
