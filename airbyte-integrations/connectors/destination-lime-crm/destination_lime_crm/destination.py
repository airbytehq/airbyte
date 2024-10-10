#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import datetime
import logging

import requests

import urllib.parse
from typing import Any, Iterable, Mapping
import uuid

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from collections import defaultdict

logger = logging.getLogger(__name__)


class DestinationLimeCrm(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        streams = {s.stream.name for s in configured_catalog.streams}
        logger.info(f"Starting write to Lime CRM with {len(configured_catalog.streams)} streams")

        buffer = defaultdict(list)

        for message in input_messages:

            logger.info(f"Received message: {message}")

            match message.type:
                case Type.RECORD:
                    logger.info(f"Received record: {message.record}")
                    stream = message.record.stream
                    if stream not in streams:
                        logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                        continue
                    buffer[stream].append((str(uuid.uuid4()), datetime.datetime.now().isoformat(), message))
                case Type.STATE:
                    logger.info(f"Received state: {message.state}")
                    for stream_name in buffer.keys():
                        logger.info(f"Flushing buffer for stream: {stream_name}")
                        logger.info("TODO: Persisting records to Lime CRM...")
                        for message in buffer[stream_name]:
                            yield message
                    buffer.clear()
                case _:
                    logger.info(f"Message type {message.type} not supported, skipping")

            for stream_name in buffer.keys():
                logger.info(f"Flushing remaining streams in buffer: {stream_name}")
                logger.info("TODO: Persisting records to Lime CRM...")
            buffer.clear()

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            url_root = config.get("url_root")
            url = urllib.parse.urljoin(url_root, "api/v1/")
            requests.get(url, timeout=3, headers={"x-api-key": config.get("api_key")}).raise_for_status()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
