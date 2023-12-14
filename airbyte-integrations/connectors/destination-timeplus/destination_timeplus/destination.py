#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from logging import getLogger
from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    DestinationSyncMode,
    Status,
    Type,
)
from timeplus import Environment, Stream

logger = getLogger("airbyte")


class DestinationTimeplus(Destination):
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
        endpoint = config["endpoint"]
        apikey = config["apikey"]
        if endpoint[-1] == "/":
            endpoint = endpoint[0 : len(endpoint) - 1]
        env = Environment().address(endpoint).apikey(apikey)
        stream_list = Stream(env=env).list()
        all_streams = {s.name for s in stream_list}

        # only support "overwrite", "append"
        for configured_stream in configured_catalog.streams:
            is_overwrite = configured_stream.destination_sync_mode == DestinationSyncMode.overwrite
            stream_exists = configured_stream.stream.name in all_streams
            logger.info(f"Stream {configured_stream.stream.name} {configured_stream.destination_sync_mode}")
            need_delete_stream = False
            need_create_stream = False
            if is_overwrite:
                if stream_exists:
                    # delete all data in the existing stream and recreate the stream.
                    need_delete_stream = True
                    need_create_stream = True
                else:
                    # only need to create the stream
                    need_create_stream = True
            else:
                if stream_exists:
                    # for append mode, just add more data to the existing stream. No need to do anything.
                    pass
                else:
                    # for append mode, create the stream and append data to it.
                    need_create_stream = True

            if need_delete_stream:
                # delete the existing stream
                Stream(env=env).name(configured_stream.stream.name).get().delete()
                logger.info(f"Stream {configured_stream.stream.name} deleted successfully")
            if need_create_stream:
                # create a new stream
                DestinationTimeplus.create_stream(env, configured_stream.stream)
                logger.info(f"Stream {configured_stream.stream.name} created successfully")

        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                yield message
            elif message.type == Type.RECORD:
                record = message.record

                # this code is to send data to a single-column stream
                # Stream(env=env).name(record.stream).column("raw", "string").ingest(payload=record.data)

                Stream(env=env).name(record.stream).ingest(payload=record.data, format="streaming")
            else:
                # ignore other message types for now
                continue

    @staticmethod
    def create_stream(env, stream: AirbyteStream):
        # singlel-column stream
        # Stream(env=env).name(stream.name).column('raw','string').create()

        tp_stream = Stream(env=env).name(stream.name.strip())
        for name, v in stream.json_schema["properties"].items():
            tp_stream.column(name.strip(), DestinationTimeplus.type_mapping(v))
        tp_stream.create()

    @staticmethod
    def type_mapping(v) -> str:
        airbyte_type = v["type"]
        if type(airbyte_type) is list:
            for t in list(airbyte_type):
                if t != "null":
                    type_def = {"type": t}
                    if t == "array":
                        type_def["items"] = v["items"]
                    return DestinationTimeplus.type_mapping(type_def)
        if airbyte_type == "number":
            return "float"
        elif airbyte_type == "integer":
            return "integer"
        elif airbyte_type == "boolean":
            return "bool"
        elif airbyte_type == "object":
            return "string"
        elif airbyte_type == "array":
            return f"array({DestinationTimeplus.type_mapping(v['items'])})"
        else:
            return "string"

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
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
            endpoint = config["endpoint"]
            apikey = config["apikey"]
            if not endpoint.startswith("http"):
                return AirbyteConnectionStatus(status=Status.FAILED, message="Endpoint must start with http or https")
            if len(apikey) != 60:
                return AirbyteConnectionStatus(status=Status.FAILED, message="API Key must be 60 characters")
            if endpoint[-1] == "/":
                endpoint = endpoint[0 : len(endpoint) - 1]
            env = Environment().address(endpoint).apikey(apikey)
            Stream(env=env).list()
            logger.info("Successfully connected to " + endpoint)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"Fail to connect to Timeplus endpoint with the given API key: {repr(e)}"
            )
