#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from typing import Any, Dict, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteLogMessage, AirbyteMessage, ConfiguredAirbyteCatalog, Level, Status, Type
from destination_heap_analytics.client import HeapClient
from destination_heap_analytics.utils import flatten_json, parse_aap_json, parse_aup_json, parse_event_json
from requests import HTTPError

logger = logging.getLogger("airbyte")


class DestinationHeapAnalytics(Destination):
    def parse_and_validate_json(self, data: Dict[str, any], api: Mapping[str, str]):
        flatten = flatten_json(data)
        api_type = api.get("api_type")
        if api_type == "track":
            return parse_event_json(data=flatten, **api)
        elif api_type == "add_user_properties":
            return parse_aup_json(data=flatten, **api)
        elif api_type == "add_account_properties":
            return parse_aap_json(data=flatten, **api)
        else:
            return None

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        messages_count = 0
        records_count = 0
        loaded_count = 0
        api = config.get("api")
        api["property_columns"] = api.get("property_columns").split(",")
        client = HeapClient(**config)
        for message in input_messages:
            messages_count = messages_count + 1
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                data = record.data
                records_count = records_count + 1
                validated = self.parse_and_validate_json(data=data, api=api)
                if validated:
                    try:
                        client.write(validated)
                        loaded_count = loaded_count + 1
                    except HTTPError as ex:
                        logger.warn(f"experienced an error at the {records_count}th row, error: {ex}")
                else:
                    logger.warn(f"data is invalid, skip writing the {records_count}th row")
            else:
                yield message
        resultMessage = AirbyteMessage(
            type=Type.LOG,
            log=AirbyteLogMessage(
                level=Level.INFO, message=f"Total Messages: {messages_count}. Total Records: {records_count}. Total loaded: {loaded_count}."
            ),
        )
        yield resultMessage

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            client = HeapClient(**config)
            logger.info(f"Checking connection for app_id: {client.app_id}, api_endpoint: {client.api_endpoint}")
            client.check()
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
        else:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
