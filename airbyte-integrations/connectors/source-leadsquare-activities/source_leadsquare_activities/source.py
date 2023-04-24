#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import requests
from datetime import datetime
from typing import Dict, Generator

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source


class SourceLeadsquareActivities(Source):
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
            request_host = config['leadsquare-host']
            access_key = config['leadsquare-access-key']
            secret_key = config['leadsquare-secret-key']

            current_datetime = datetime.now()

            current_start_hour_timestamp = current_datetime.replace(minute=0, second=0, microsecond=0)
            current_end_hour_timestamp = current_datetime.replace(minute=59, second=59, microsecond=999)

            leadsquare_response = requests.post(
                url=f'{request_host}/v2/ProspectActivity.svc/RetrieveRecentlyModified',
                params={
                    "accessKey": access_key,
                    "secretKey": secret_key,
                },
                json={
                    "Parameter": {
                        "FromDate": current_start_hour_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "ToDate": current_end_hour_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "IncludeCustomFields": 1
                    },
                    "Paging": {
                        "PageIndex": 1,
                        "PageSize": 1
                    },
                    "Sorting": {
                        "ColumnName": "CreatedOn",
                        "Direction": 1
                    }
                }
            )

            if 200 <= leadsquare_response.status_code < 300:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)

            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Threw {leadsquare_response.status_code} Status code, with {leadsquare_response.json()} response.")
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
        activity_fields = {
            "activityId": {
                "type": "string"
            },
            "eventCode": {
                "type": "number",
            },
            "eventName": {
                "type": "string"
            },
            "activityScore": {
                "type": "number"
            },
            "activityType": {
                "type": "number"
            },
            "type": {
                "type": "string"
            },
            "relatedProspectId": {
                "type": "string"
            },
            "activityData": {
                "type": "object",
                "default": {}
            },
            "sessionId": {
                "type": "string"
            },
            "activityCustomFields": {
                "type": "object",
                "default": {}
            },

        }

        stream_name = "LeadSquareActivity"
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": activity_fields,
        }

        streams = [
            {
                "name": stream_name,
                "supported_sync_modes": [
                    "full_refresh"
                ],
                "source_defined_cursor": False,
                "json_schema": json_schema
            }
        ]

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
        stream_name = "LeadSquareActivity"
        request_host = config['leadsquare-host']
        access_key = config['leadsquare-access-key']
        secret_key = config['leadsquare-secret-key']

        current_datetime = datetime.now()

        current_start_hour_timestamp = current_datetime.replace(minute=0, second=0, microsecond=0)
        current_end_hour_timestamp = current_datetime.replace(minute=59, second=59, microsecond=999)

        try:
            leadsquare_response = requests.post(
                url=f'{request_host}/v2/ProspectActivity.svc/RetrieveRecentlyModified',
                params={
                    "accessKey": access_key,
                    "secretKey": secret_key,
                },
                json={
                    "Parameter": {
                        "FromDate": current_start_hour_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "ToDate": current_end_hour_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        "IncludeCustomFields": 1
                    },
                    "Sorting": {
                        "ColumnName": "CreatedOn",
                        "Direction": 1
                    }
                }
            )

            if 200 <= leadsquare_response.status_code < 300:
                for leadsquare_activities in leadsquare_response.json()['ProspectActivities']:
                    lead_activity_data = {
                        "activityId": leadsquare_activities['Id'],
                        "eventCode": leadsquare_activities['EventCode'],
                        "eventName": leadsquare_activities['EventName'],
                        "activityScore": leadsquare_activities['ActivityScore'],
                        "activityType": leadsquare_activities['ActivityType'],
                        "type": leadsquare_activities['Type'],
                        "relatedProspectId": leadsquare_activities['RelatedProspectId'],
                        "activityData": leadsquare_activities['Data'],
                        "sessionId": leadsquare_activities['SessionId'],
                        "activityCustomFields": leadsquare_activities['Fields'],
                    }

                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=stream_name, data=lead_activity_data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
            else:
                logger.error(f'LeadSquare Response Threw {leadsquare_response.status_code} with {leadsquare_response.status_code}')
        except Exception as e:
            logger.error(f'Error while running activity query: {str(e)}')
