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
from jsonschema import validate 
from datetime import datetime

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

# STREAM NAMES
StreamGetSiteMetaData = "GetSiteMetaData"
StreamGetSensorMetaData = "GetSensorMetaData"
StreamGetSensorData = "GetSensorData"
# PARAM_NAMES
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
            # VALIDATE CONFIG AGAINST JSON SCHEMA (spec.json)
            validate( instance=config, schema=self.spec(logger).connectionSpecification) 
            # try to get time (ping) from configured URL
            url = config[ConfigPropDataApiUrl]

            def assertAliasedParamsNotBothPresent(config,stream,paramName1,paramName2):
                if paramName1 in config[stream] and paramName2 in config[stream]:
                    raise AssertionError(f"{stream}: cannot specify both aliased parameters '{paramName1}' and '{paramName2}'. choose one.")

            def assertOneRainDateFormat(config,stream,paramName):
                try:
                    if paramName in config[stream]:
                        return datetime.strptime(config[stream][paramName],'%Y-%m-%d %H:%M:%S')
                except ValueError as e:
                    raise ValueError(stream,paramName,str(e))
 
            # ADDITIONAL GetSiteMetadata STREAM CONFIG CHECKS
            assertAliasedParamsNotBothPresent(config,StreamGetSiteMetaData,"or_site_id","site_id")



            # ADDITIONAL GetSensorMetaData STREAM CONFIG CHECKS
            assertAliasedParamsNotBothPresent(config,StreamGetSensorMetaData,"or_sensor_id","sensor_id")
            assertAliasedParamsNotBothPresent(config,StreamGetSensorMetaData,"or_site_id","site_id")

            # ADDITIONAL GetSensorData STREAM CONFIG CHECKS
            assertAliasedParamsNotBothPresent(config,StreamGetSensorData,"or_site_id","site_id")
            assertAliasedParamsNotBothPresent(config,StreamGetSensorData,"or_sensor_id","sensor_id")
            assertOneRainDateFormat(config,StreamGetSensorData,"data_start")
            assertOneRainDateFormat(config,StreamGetSensorData,"data_end")
            assertOneRainDateFormat(config,StreamGetSensorData,"receive_start")
            assertOneRainDateFormat(config,StreamGetSensorData,"receive_end")

            # PING CONFIGURED ONERAIN URL WITH GetTime REQUEST TO MAKE SURE IT'S A VALID ENDPOINT
            get_time_url = f'{url}?method=GetTime'
         
            # use GetTime method to validate well formed url and that it responds to this 
            # basic time get request    
            r = requests.get(get_time_url)
            assert r.status_code == 200 
 
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

        # GET SPEC TO GRAB DESCRIPTIONS OF FIELDS
        spec = self.spec(logger).connectionSpecification
        defs = spec['definitions']

        def get_spec_def_obj(name):
            return defs[name]
        def get_spec_def_desc(name):
            return defs[name]['description']
        def get_spec_def_type(name):
            return defs[name]['type']
        def get_spec_def_prop(spec_def_name,def_prop_name):
            return defs[spec_def_name][def_prop_name]

        # ADD SCHEMA FOR StreamGetSiteMetaData
        stream_name = StreamGetSiteMetaData 
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "or_site_id": get_spec_def_obj('or_site_id'),
                "site_id": get_spec_def_obj('site_id'),
                "location":{"desription":"descriptive site location","type":"string"},
                "owner":{"desription":"site owner","type":"string"},
                "system_id":{"description":"system id?", "type":"number"},
                "client_id":{"description":"???","type":"string"},
                "latitude_dec":{"description":"decimal latitude","type":"number"},
                "longitude_dec":{"description":"decimal longitude","type":"number"},
                "elevation":{"description":"site elevation (in units of ???)","type":"number"},
            },
        }
        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema))

        # ADD SCHEMA FOR StreamGetSensorMetaData
        stream_name = StreamGetSensorMetaData
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "site_id": get_spec_def_obj('site_id'),
                "sensor_id": get_spec_def_obj('sensor_id'),
                "or_site_id": get_spec_def_obj('or_site_id'),
                "or_sensor_id":get_spec_def_obj('or_sensor_id'),
                "location":{"description":"","type":"string"},
                "description":{"description":"", "type":"string"},
                "sensor_class":get_spec_def_obj('class'),
                "sensor_type":{"description":"Sensor type","type":"string"},
                "units":get_spec_def_obj('units'),
                "translate":{"description":"", "type":"boolean"}, 
                "precision":{"description":"", "type":"integer"},
                "last_time":{"description":"","type":"string"},
                "last_value":{"description":"", "type":"number"},
                "last_time_received":{"description":"", "type":"string"},
                "last_value_received":{"description":"", "type":"number"},
                "last_raw_value":{"description":"", "type":"number"},
                "last_raw_value_received":{"description":"","type":"number"},
                "change_time":{"description":"","type":"string"},
                "normal":{"description":"", "type":"integer"}, # boolean?
                "active":{"description":"", "type":"integer"}, #boolean?
                "valid":{"description":"", "type":"integer"}, #boolean?
                "change_rate":{"description":"", "type":"number"},
                "time_min_consec_zeros":{"description":"", "type":"integer"},
                "validation":{"description":"", "type":"string"},
                "value_max":{"description":"", "type":"number"},
                "value_min":{"description":"", "type":"number"},
                "delta_pos":{"description":"", "type":"number"},
                "delta_neg":{"description":"", "type":"number"},
                "rate_pos":{"description":"", "type":"number"},
                "rate_neg":{"description":"", "type":"number"},
                "time_max":{"description":"", "type":"integer"},
                "time_min":{"description":"", "type":"integer"},
                "slope":{"description":"", "type":"number"},
                "offset":{"description":"", "type":"number"},
                "reference":{"description":"", "type":"number"},
                "utc_offset":{"description":"", "type":"integer"},
                "using_dst":{"description":"", "type":"boolean"},
                "conversion":{"description":"", "type":"string"},
                "usage":{"description":"", "type":"string"},
                "protocol":{"description":"", "type":"integer"}  

            }
        } 
        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema))

        # ADD STREAM FOR StreamGetSensorData
        stream_name = StreamGetSensorData
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "site_id":get_spec_def_obj('site_id'),
                "sensor_id":get_spec_def_obj('sensor_id'),
                "or_site_id":get_spec_def_obj('or_site_id'),
                "or_sensor_id":get_spec_def_obj('or_sensor_id'),
                "sensor_class":get_spec_def_obj('class'),
                "data_time": {
                    "type": get_spec_def_type('onerain_datetime'),
                    "description":"date/time data was captured",
                    "pattern":get_spec_def_prop('onerain_datetime','pattern')
                },
                "data_value": {
                    "type":"number",
                    "description":"data value",
                 
                },
                "raw_value": {
                    "type":"number",
                    "description":"raw data value",
                },
                "units": get_spec_def_obj('units')
    
                
            }
        }

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
        stream_name = StreamGetSiteMetaData  # Example

        data_api_url = config[ConfigPropDataApiUrl]
        system_key = config[ConfigPropSystemKey]

        req_url = f"{data_api_url}?method={stream_name}&system_key={system_key}"

        # RETRIEVE SITE METADATA
        try:
            r = requests.get(req_url)
            assert r.status_code == 200 

            # ITERATE SITE METADATA AND RETURN AS STREAM
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
            logger.error(f'failed to process stream {stream_name}: {str(e)}')

        # RETRIEVE SENSOR METADATA AND RETURN AS STREAM
        stream_name = StreamGetSensorMetaData

        req_url = f'{data_api_url}?method={stream_name}&system_key={system_key}' 

        try:
            # submit request
            r = requests.get(req_url)
            assert r.status_code == 200
            #logger.info(r.text)
            doc = xmltodict.parse(r.text)
            
            for row in doc['onerain']['response']['general']['row']:

                data=dict()
                data['site_id'] = row['site_id']
                data['sensor_id'] = int(row['sensor_id'])
                data['or_site_id'] = int(row['or_site_id'])
                data['or_sensor_id'] = int(row['or_sensor_id'])
                data['location'] = row['location']
                data['description'] = row['description']        
                data['sensor_class'] = int(row['sensor_class'])
                data['sensor_type'] =row['sensor_type']
                data['units'] = row['units']
                data['translate'] = str_to_bool(row['translate'])
                data['precision'] = int(row['precision'])
                data['last_time'] = row['last_time']
                data['last_value'] = row['last_value']
                data['last_time_received'] = row['last_time_received']
                data['last_value_received'] = float(row['last_value_received'])
                data['last_raw_value'] = float(row['last_raw_value'])
                data['last_raw_value_received'] = float(row['last_raw_value_received'])
                #data['change_time'] = row['change_time']
                data['normal'] = int(row['normal'])
                data['active'] = int(row['active'])
                data['valid'] = int(row['valid'])
                data['change_rate'] = float(row['change_rate'])
                data['time_min_consec_zeros'] = int(row['time_min_consec_zeros'])
                data['validation'] = row['validation']
                data['value_max'] = float(row['value_max'])
                data['value_min'] = float(row['value_min'])
                data['delta_pos'] = float(row['delta_pos'])
                data['delta_neg'] = float(row['delta_neg'])
                data['time_max'] = int(row['time_max'])
                data['time_min'] = int(row['time_min'])
                data['slope'] = float(row['slope'])
                data['offset'] = float(row['offset'])
                data['reference'] = float(row['reference'])
                data['utc_offset'] = int(row['utc_offset'])
                data['using_dst'] = str_to_bool(row['using_dst']) 
                data['conversion'] = row['conversion']
                data['usage'] = row['usage']
                data['protocol'] = int(row['protocol'])

                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                )       
        except Exception as e:
            logger.error(f'failed to process stream {stream_name}: {str(e)}') 

        # RETRIEVE SENSOR DATA AND RETURN AS STREAM
        stream_name = StreamGetSensorData

        req_url = f"{data_api_url}?method={stream_name}&system_key={system_key}"
        
        try:
            # submit request
            r = requests.get(req_url)
            assert r.status_code == 200
            doc = xmltodict.parse(r.text)

            for row in doc['onerain']['response']['general']['row']:
                data=dict()
                data['site_id'] = row['site_id']
                data['sensor_id'] = row['sensor_id']
                data['or_site_id'] = int(row['or_site_id'])
                data['or_sensor_id'] = int(row['or_sensor_id'])
                data['sensor_class'] = int(row['sensor_class'])
                data['data_time'] = row['data_time']
                data['data_value'] = float(row['data_value'])
                data['raw_value'] = float(row['raw_value'])
                data['units'] = row['units']
                 
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                )       
        except Exception as e:
            logger.error(f'failed to process stream {stream_name}: {str(e)}') 

def str_to_bool(s):
    true_values = ['true','t','yes','y',1]
    false_values = ['false','f','no','n',0]

    if s.lower() in true_values:
        return True
    if s.lower() in false_values:
        return False

    raise ValueError(f"cannot convert '{s}' to boolean. expected {true_values} or {false_values}")

