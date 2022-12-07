#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, DestinationSyncMode, Type

import json
import timeplus_client
from timeplus_client.rest import ApiException

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
        endpoint=config["endpoint"]
        apikey=config["apikey"]
        if endpoint[-1]=='/':
            endpoint=endpoint[0:len(endpoint)-1]
        configuration = timeplus_client.Configuration()
        configuration.api_key['X-Api-Key'] = apikey
        configuration.host=endpoint+"/api"
        stream_api = timeplus_client.StreamsV1beta1Api(timeplus_client.ApiClient(configuration))
        stream_list = stream_api.v1beta1_streams_get()
        all_streams = {s.name for s in stream_list}

        # only support "overwrite", "append"
        for configured_stream in configured_catalog.streams:
            is_overwrite = configured_stream.destination_sync_mode == DestinationSyncMode.overwrite
            stream_exists = configured_stream.stream.name in all_streams
            if is_overwrite and stream_exists:
                # delete the existing stream
                stream_api.v1beta1_streams_name_delete(configured_stream.stream.name)
            if is_overwrite or not stream_exists:
                # create a new stream
                stream_api.v1beta1_streams_post(timeplus_client.StreamDef(name=configured_stream.stream.name, columns=[timeplus_client.ColumnDef(name='raw',type='string')]))

        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                
                batch_body=timeplus_client.IngestData(columns=[timeplus_client.ColumnDef(name='raw',type='string')],data=[[json.dumps(record.data)]])
                # TODO: check the stream name, if same, then batch upload data

                stream_api.v1beta1_streams_name_ingest_post(batch_body,record.stream)

            else:
                # ignore other message types for now
                continue

        pass

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
            endpoint=config["endpoint"]
            apikey=config["apikey"]
            if not endpoint.startswith("http"):
                return AirbyteConnectionStatus(status=Status.FAILED, message="Endpoint must start with http or https")
            if len(apikey) != 60:
                return AirbyteConnectionStatus(status=Status.FAILED, message="API Key must be 60 characters")
            if endpoint[-1]=='/':
                endpoint=endpoint[0:len(endpoint)-1]
            configuration = timeplus_client.Configuration()
            configuration.api_key['X-Api-Key'] = apikey
            configuration.host=endpoint+"/api"
            timeplus_client.APIKeysV1beta1Api(timeplus_client.ApiClient(configuration)).v1beta1_auth_api_keys_get()
            logger.info("Successfully connected to "+endpoint)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Fail to connect to Timeplus endpoint with the given API key: {repr(e)}")
