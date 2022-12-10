#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, DestinationSyncMode, Type, AirbyteStream

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
        api_client=timeplus_client.ApiClient(configuration)
        stream_api = timeplus_client.StreamsV1beta1Api(api_client)
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
                DestinationTimeplus.create_stream(stream_api, configured_stream.stream)
                
        for message in input_messages:
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the destination. So we flush
                # the queue to ensure writes happen, then output the state message to indicate it's safe to checkpoint state
                yield message
            elif message.type == Type.RECORD:
                record = message.record
                
                # this code is to send data to a single-column stream
                # batch_body=timeplus_client.IngestData(columns=['raw'],data=[[json.dumps(record.data)]])
                # stream_api.v1beta1_streams_name_ingest_post(batch_body,record.stream)

                # using a hacking way to send JSON objects directly to Timeplus, without using the default compact mode.
                api_client.call_api(
                    f"/v1beta1/streams/{record.stream}/ingest",
                    "POST",
                    {},
                    {"format":"streaming"},
                    {},
                    body=record.data,
                    post_params=[],
                    files={},
                    response_type=None,
                    auth_settings=["ApiKeyAuth"],
                    async_req=False,
                    _return_http_data_only=False,
                    _preload_content=True,
                    _request_timeout=False,
                    collection_formats={},
                )
            else:
                # ignore other message types for now
                continue
        pass

    @staticmethod
    def create_stream(stream_api,stream: AirbyteStream):
        # singlel-column stream
        # stream_api.v1beta1_streams_post(timeplus_client.StreamDef(name=stream.name, columns=[timeplus_client.ColumnDef(name='raw',type='string')]))
        
        columns=[]
        for name,v in stream.json_schema['properties'].items():
            columns.append(timeplus_client.ColumnDef(name=name,type=DestinationTimeplus.type_mapping(v)))
        stream_api.v1beta1_streams_post(timeplus_client.StreamDef(name=stream.name,columns=columns))

    @staticmethod
    def type_mapping(v) -> str:
        airbyte_type=v['type']
        if airbyte_type=='number':return 'float'
        elif airbyte_type=='integer':return 'integer'
        elif airbyte_type=='boolean':return 'bool'
        elif airbyte_type=='object':return 'string'
        elif airbyte_type=='array':
            return f"array({DestinationTimeplus.type_mapping(v['items'])})"
        else:return 'string'

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
