"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from datetime import datetime
from typing import Dict, Generator
import xmltodict
import requests

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from base_python import AirbyteLogger, Source

StreamSiteMetadata = "SiteMetaData"
ConfigPropDataApiUrl = "data_api_url"
ConfigPropSystemKey = "system_key"

class SourceOnerainApi(Source):
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
            # Not Implemented
            if ConfigPropDataApiUrl not in config:
                raise ValueError("missing configuration property '%s'" % ConfigPropDataApiUrl)
            if ConfigPropSystemKey not in config:
                raise ValueError("missing configuration property '%s'" % ConfigPropSystemKey)

            
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
        the properties of the spec.json file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:q
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """
        streams = []

        stream_name = StreamSiteMetadata  # Example
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "or_site_id": {"description":"OneRain Contrail Site ID. These IDs are unique to the OneRain hosted Contrail Server or any Contrail Base Station","type": "number"},
                "site_id": {"description":"Alias Site ID, how the Site is identified by the collecting sytem","type":"string"},
                "location":{"desription":"descriptive site location","type":"string"},
                "owner":{"desription":"site owner","type":"string"},
                "system_id":{"description":"system id?", "type":"number"},
                "client_id":{"description":"???","type":"string"},
                "latitude_dec":{"description":"decimal latitude","type":"number"},
                "longitude_dec":{"description":"decimal longitude","type":"number"},
                "elevation":{"description":"site elevation (in units of ???)","type":"number"},
            },
        }

        # Not Implemented

        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema))
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
        stream_name = StreamSiteMetadata  # Example

        data_api_url = config[ConfigPropDataApiUrl]
        system_key = config[ConfigPropSystemKey]

        req_url = "%s?method=GetSiteMetadata&system_key=%s" % (data_api_url,system_key)

        # RETRIEVE SITE METADATA
        try:
            r = requests.get(req_url)
        except Exception as e:
            logger.error("OneRain request method 'GetSiteMetadata' failed: %s" % str(e))
            return
        # ITERATE SITE METADATA AND RETURN AS STREAM
        try:
            doc = xmltodict.parse(r.text)
            for row in doc['onerain']['response']['general']['row']:
                or_site_id = int(row['or_site_id'])
                site_id = row['site_id']
                location = row['location']
                owner = row['owner']
                system_id = int(row['system_id'])
                client_id = row['client_id']  
                latitude_dec = float(row['latitude_dec'])
                longitude_dec = float(row['longitude_dec'])
                elevation = int(row['elevation'])
       
                data = dict()
                data['or_site_id'] = or_site_id
                data['site_id'] = site_id
                data['location'] = location
                data['owner'] = owner
                data['system_id'] = system_id
                data['client_id'] = client_id
                data['latitude_dec'] = latitude_dec
                data['longitude_dec'] = longitude_dec
                data['elevation'] = elevation

                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                )       

        except Exception as e:
            logger.error("failed to process 'GetSiteMetadata' response object: %s" % str(e))
            return
        
