# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


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
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import Source
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.oauth2.credentials import Credentials

class SourceGoogleAds(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            if(len(config['streams'] )== 0):
                raise Exception("No streams defined. Add at least one stream.")

            self.discover(logger, config)

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def _search(self, query, config: json):
        client = GoogleAdsClient.load_from_dict(config)
        ga_service = client.get_service("GoogleAdsService")

        search_request = client.get_type("SearchGoogleAdsStreamRequest")
        search_request.customer_id = config['customer_id']
        search_request.query = query
        response = ga_service.search_stream(search_request)
#https://github.com/googleads/google-ads-python/issues/384
        response.service_reference = ga_service
        return response


    field_type_dict = {
        bool: "boolean",
        int: "integer",
        float: "number",
        str: "string"
    }

    def extract_schema(self, stream_config, response):
        props = {}
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": props,
        }
        for batch in response:
            for row in batch.results:
                error_keys = []
                for key in batch.field_mask.paths:
                    try:
                        parts = key.split('.')
                        obj = getattr(row, parts[0])
                        fld = getattr(obj, parts[1])
                        typ = self.field_type_dict[type(fld)]
                        props[key] = {'type': typ}
                    except Exception as e:
                        error_keys.append(key)

                if(len(error_keys)>0):
                    raise Exception(f"The {stream_config['name']} GAQL contains invalid keys, try removing them from the GAQL. Keys: {str(error_keys)}")
                return json_schema

        raise Exception(f"The reponse has now rows. Please modify the {stream_config['name']} GAQL so that it returns at least one row") 


    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        For example, given valid credentials to a Postgres database,
        returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """
        streams = []

        for stream_config in config['streams']:
            query = stream_config['gaql']
            stream_name = stream_config['name']
            response = self._search(query, config)
            json_schema = self.extract_schema(stream_config, response)
            stream = AirbyteStream(name=stream_name, json_schema=json_schema)
            stream.supported_sync_modes = [SyncMode.full_refresh, SyncMode.incremental]
            streams.append(stream)

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
            the properties of the spec.json file
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

        for stream_catalog in catalog['streams']:
            stream_name = stream_catalog['stream']['name']
            stream_config = None
            for config in config["streams"]:
                if config["name"] == stream_name:
                    stream_config = config

            if stream_config is None:
                #TODO Can we map the configured name back to original somehow?
                logger.error("Renaming of streams not supported. Please use the original stream name defined in the config.")
                continue

            query = stream_config['gaql']
            response = self._search(query, config)

            for batch in response:
                for row in batch.results:
                    data = {}
                    for key in batch.field_mask.paths:
                        parts = key.split('.')
                        obj = getattr(row, parts[0])
                        fld = getattr(obj, parts[1])
                        data[key] = fld
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
