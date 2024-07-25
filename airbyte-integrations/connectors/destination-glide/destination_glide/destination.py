#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    Status,
    DestinationSyncMode,
    Type
)
from collections import defaultdict
from collections.abc import Hashable
import datetime

from .glide import Column, GlideBigTableFactory
import json
from .log import LOG_LEVEL_DEFAULT
import logging
import requests
from typing import Any, Iterable, Mapping
import uuid

CONFIG_GLIDE_API_HOST_DEFAULT = "https://api.glideapps.com"
CONFIG_GLIDE_API_PATH_ROOT_DEFAULT = ""

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_DEFAULT)


def airbyteTypeToGlideType(json_type: str) -> str:
    jsonSchemaTypeToGlideType = {
        "string": "string",
        "number": "number",
        "integer": "number",
        "boolean": "boolean",
    }
    if isinstance(json_type, list):
        logger.debug(f"Found list type '{json_type}'. Attempting to map to a primitive type.")  # nopep8
        # find the first type that is not 'null' and supported and use that instead:
        for t in json_type:
            if t != "null" and t in jsonSchemaTypeToGlideType:
                logger.debug(f"Mapped json schema list type of '{json_type}' to '{t}'.")  # nopep8
                json_type = t
                break

    # NOTE: if json_type is still a list, it won't be Hashable and we can't use it as a key in the dict
    if isinstance(json_type, Hashable) and json_type in jsonSchemaTypeToGlideType:
        return jsonSchemaTypeToGlideType[json_type]

    logger.warning(f"Unsupported JSON schema type for glide '{json_type}'. Will use string.")  # nopep8
    return "string"


class DestinationGlide(Destination):
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
        # load user-specified config:
        api_host = config.get('api_host', CONFIG_GLIDE_API_HOST_DEFAULT)
        api_path_root = config.get('api_path_root', CONFIG_GLIDE_API_PATH_ROOT_DEFAULT)
        api_key = config.get('api_key')

        # configure the table based on the stream catalog:
        # choose a strategy based on config:

        def create_table_client_for_stream(stream_name):
            # TODO: sanitize stream_name chars and length for GBT name
            glide = GlideBigTableFactory.create()
            glide.init(api_key, stream_name, api_host, api_path_root)
            return glide

        table_clients = {}
        stream_names = {s.stream.name for s in configured_catalog.streams}
        for configured_stream in configured_catalog.streams:
            if configured_stream.destination_sync_mode != DestinationSyncMode.overwrite:
                raise Exception(f'Only destination sync mode overwrite is supported, but received "{configured_stream.destination_sync_mode}".')  # nopep8 because https://github.com/hhatto/autopep8/issues/712

            glide = create_table_client_for_stream(
                configured_stream.stream.name)
            # upsert the GBT with schema to set_schema for dumping the data into it
            columns = []
            properties = configured_stream.stream.json_schema["properties"]
            for (prop_name, prop) in properties.items():
                prop_type = prop["type"]
                logger.debug(f"Found column/property '{prop_name}' with type '{prop_type}' in stream {configured_stream.stream.name}.")  # nopep8
                columns.append(
                    Column(prop_name, airbyteTypeToGlideType(prop_type))
                )

            glide.set_schema(columns)
            table_clients[configured_stream.stream.name] = glide

        # stream the records into the GBT:
        buffers = defaultdict(list)
        logger.debug("Processing messages...")
        for message in input_messages:
            logger.debug(f"processing message {message.type}...")
            if message.type == Type.RECORD:
                logger.debug("buffering record...")
                stream_name = message.record.stream
                if stream_name not in stream_names:
                    logger.warning(
                        f"Stream {stream_name} was not present in configured streams, skipping")
                    continue

                # add to buffer
                record_data = message.record.data
                record_id = str(uuid.uuid4())
                stream_buffer = buffers[stream_name]
                stream_buffer.append(
                    (record_id, datetime.datetime.now().isoformat(), record_data))
                logger.debug("buffering record complete.")

            elif message.type == Type.STATE:
                # `Type.State` is a signal from the source that we should save the previous batch of `Type.RECORD` messages to the destination.
                #   It is a checkpoint that enables partial success.
                #   See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#state--checkpointing
                logger.info(f"Writing buffered records to Glide API from {len(buffers.keys())} streams...")  # nopep8
                for stream_name in buffers.keys():
                    stream_buffer = buffers[stream_name]
                    logger.info(f"Saving buffered records to Glide API (stream: '{stream_name}', record count: '{len(stream_buffer)}')...")  # nopep8
                    DATA_INDEX = 2
                    data_rows = [row_tuple[DATA_INDEX]
                                 for row_tuple in stream_buffer]
                    if len(data_rows) > 0:
                        if stream_name not in table_clients:
                            raise Exception(
                                f"Stream '{stream_name}' not found in table_clients")
                        glide = table_clients[stream_name]
                        glide.add_rows(data_rows)
                    stream_buffer.clear()
                    logger.info(f"Saving buffered records to Glide API complete.")  # nopep8 because https://github.com/hhatto/autopep8/issues/712

                # dump all buffers now as we just wrote them to the table:
                buffers = defaultdict(list)
                yield message
            else:
                logger.warn(f"Ignoring unknown Airbyte input message type: {message.type}")  # nopep8 because https://github.com/hhatto/autopep8/issues/712

        # commit the stash to the table
        for stream_name, glide in table_clients.items():
            glide.commit()
            logger.info(f"Committed stream '{stream_name}' to Glide.")

        pass

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
            # TODO

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
