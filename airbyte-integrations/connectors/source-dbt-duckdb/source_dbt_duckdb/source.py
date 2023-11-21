#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
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

from .utils.dbt import invoke_dbt, get_dbt_manifest


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
        try:
            # Not Implemented
            invoke_dbt("debug", project_dir=config["dbt_project_path"], logger=logger)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"An exception occurred: {str(e)}"
            )

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
                        "model_name": {"type": "string"},
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
                        "test_name": {"type": "string"},
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
        dbt_project_dir = config["dbt_project_path"]

        # Get dbt manifest
        manifest = get_dbt_manifest(project_dir=dbt_project_dir, logger=logger)
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

        # Run dbt models
        results_list: list[dict] = []
        dbt_runner_result = invoke_dbt(
            "run",
            project_dir=dbt_project_dir,
            manifest=manifest,
            logger=logger,
        )
        for result_item in dbt_runner_result.result:
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    stream="dbt_run_results",
                    data={
                        "model_name": result_item.node.name,
                        "status": result_item.status,
                    },
                    emitted_at=int(datetime.now().timestamp()) * 1000,
                ),
            )
            results_list.append(result_item.to_dict())
        yield AirbyteMessage(
            type=Type.STATE,
            state={"results": results_list},
        )

        # Optionally run dbt tests
        if config.get("run_tests"):
            dbt_runner_result = invoke_dbt(
                "test",
                project_dir=dbt_project_dir,
                logger=logger,
            )
            for result_item in dbt_runner_result.result:
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream="dbt_test_results",
                        data={
                            "model_name": result_item.node.name,
                            "status": result_item.status,
                        },
                        emitted_at=int(datetime.now().timestamp()) * 1000,
                    ),
                )
