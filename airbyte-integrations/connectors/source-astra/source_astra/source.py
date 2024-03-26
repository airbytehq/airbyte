#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

import numbers
from source_astra.astra_client import AstraClient

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


class SourceAstra(Source):
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
            index = AstraClient(
                astra_endpoint=config["database_endpoint"],
                astra_application_token=config["application_token"],
                keyspace_name=config["keyspace_name"],
                collection_name=config["collection_name"],
                embedding_dim=config["embedding_dimension"],
                similarity_function=config["similarity_function"],
                )

            index.find_index()

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

        stream_name = config["keyspace_name"]+"."+config["collection_name"]

        index = AstraClient(
            astra_endpoint=config["database_endpoint"],
            astra_application_token=config["application_token"],
            keyspace_name=config["keyspace_name"],
            collection_name=config["collection_name"],
            embedding_dim=config["embedding_dimension"],
            similarity_function=config["similarity_function"],
            )
        
        def get_json_schema_type(instance):
            if isinstance(instance, dict):
                return { "type": "object" }
            if isinstance(instance, list):
                return { "type": "array", "items": get_json_schema_type(instance[0])}
            if isinstance(instance, bool):
                return { "type": "boolean" }
            if isinstance(instance, int):
                return { "type": "integer"}
            if isinstance(instance, float):
                return { "type": "number"}
            if isinstance(instance, str):
                return { "type": "string"}
            return { "type": "null"}

        document_types = []
        for doc in index.find_documents({}):
            document_types.append([{"column_name": key , "column_type": doc[key]} for key in doc.keys()])
        json_schema_properties = {}
        for column in [column for list in document_types for column in list]:
            json_schema_properties[str(column["column_name"])] = get_json_schema_type(column["column_type"])

        json_schema = { 
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": json_schema_properties
        }

        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema, supported_sync_modes = ["full_refresh"]))
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
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
            data everytime.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        stream_name = config["keyspace_name"]+"."+config["collection_name"]

        index = AstraClient(
            astra_endpoint=config["database_endpoint"],
            astra_application_token=config["application_token"],
            keyspace_name=config["keyspace_name"],
            collection_name=config["collection_name"],
            embedding_dim=config["embedding_dimension"],
            similarity_function=config["similarity_function"],
            )

        for data in index.find_documents({}):    
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
            )
