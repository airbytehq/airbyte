#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator
from time import sleep

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

import requests


SELECT_STAR_BASE_URL = "https://api.production.selectstar.com/v1"


def request_with_backoff(url, headers, logger):
    response = None
    backoff_time = 1
    retries = 0
    logger.info(f"Perform a GET on {url}")
    while response is None:
        try:
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 429:
                sleep(backoff_time * (2 ** retries))
                retries = retries + 1
                response = None
        except requests.ConnectionError as e:
            logger.warn(e)
            sleep(3)
            continue
        except requests.Timeout as e:
            logger.warn(e)
            sleep(3)
            continue
        except requests.RequestException as e:
            logger.warn(e)
            sleep(3)
            continue
        if response is not None and response.status_code != 200:
            # should anything is unexpected, log and retry
            logger.warn(f"error when GET {url}, status code returned {response.status_code}")
            response = None

    # in the end, no matter how long, a response will be sent back
    return response


class SourceSelectStar(Source):
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
            # do a dummy get request just to handshake and verify token is valid
            token = json.loads(json.dumps(config))["token"]
            table_url = f"{SELECT_STAR_BASE_URL}/tables/"
            headers = {"AUTHORIZATION": f"Token {token}"}
            response = requests.request("GET", table_url, headers=headers)
            if response.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(response.text)}")
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

        supported_sync_modes = ["full_refresh"]
        source_defined_cursor = False

        stream_name = "table"  # Example
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "guid": {"type": "string"},
                "database_name": {"type": "string"},
                "schema_name": {"type": "string"},
                "table_name": {"type": "string"},
                "description": {"type": "string"},
                "business_owner": {"type": "string"},
                "technical_owner": {"type": "string"},
                "row_count": {"type": "integer"},
            },
        }
        streams.append(
            AirbyteStream(
                name=stream_name,
                json_schema=json_schema,
                supported_sync_modes=supported_sync_modes,
                source_defined_cursor=source_defined_cursor,
            )
        )

        stream_name = "lineage"
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"guid": {"type": "string"}, "target_guid": {"type": "string"}, "target_object_type": {"type": "string"}},
        }
        streams.append(
            AirbyteStream(
                name=stream_name,
                json_schema=json_schema,
                supported_sync_modes=supported_sync_modes,
                source_defined_cursor=source_defined_cursor,
            )
        )

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
        token = json.loads(json.dumps(config))["token"]
        table_url = f"{SELECT_STAR_BASE_URL}/tables/"
        headers = {"AUTHORIZATION": f"Token {token}"}

        while table_url is not None:
            table_response = request_with_backoff(table_url, headers, logger)
            res = table_response.json()
            for table in res["results"]:

                # create table object
                table_obj = {
                    "guid": table["guid"],
                    "database_name": table["database"]["name"],
                    "schema_name": table["schema"]["name"],
                    "table_name": table["name"],
                    "description": table["description"],
                    "business_owner": table["business_owner"],
                    "technical_owner": table["technical_owner"],
                    "row_count": table["row_count"],
                }

                # and sent it
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream="table", data=table_obj, emitted_at=int(datetime.now().timestamp()) * 1000),
                )

                # get lineage for each table
                lineage_url = f"{SELECT_STAR_BASE_URL}/lineage/{table_obj['guid']}/?max_depth=1&direction=right&mode=table"
                lineage_response = request_with_backoff(lineage_url, headers, logger)
                lineage = lineage_response.json()

                # form connections
                target_table_guid = []

                # also construct the object type for each target_guid found
                target_object_types = {}
                for lin in lineage["table_lineage"]:
                    target_table_guid.extend(lin["target_table_guids"])
                    target_object_types[lin["key"]] = lin["object_type"]

                # and for each conenction found sent it
                for target_guid in target_table_guid:
                    if table_obj["guid"] != target_guid:  # exclude self-references
                        data = {"guid": table_obj["guid"], "target_guid": target_guid, "target_object_type": target_object_types[target_guid]}
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(stream="lineage", data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                        )

            # visit next page since tables is paginated
            next_page = res["next"]

            # visit the next page
            table_url = next_page
