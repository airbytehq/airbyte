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
from datetime import datetime,timedelta
from typing import Dict, Generator
import xmltodict
import requests
from jsonschema import validate 
from datetime import datetime
from urllib.parse import urlencode
import traceback
import timeunit
from collections import OrderedDict

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
    SyncMode
)
from base_python import AirbyteLogger, Source

# STREAM NAMES
StreamGetSiteMetaData = "GetSiteMetaData"
StreamGetSensorMetaData = "GetSensorMetaData"
StreamGetSensorData = "GetSensorData"
# PARAM_NAMES
ConfigPropDataApiUrl = "data_api_url"
ConfigPropSystemKey = "system_key"
# OTHER CONSTANTS
HttpResponseTimeout = 30 # TIME TO WAIT FOR A RESPONSE FROM ONERAIN SERVER (IN SECONDS)
OneRainDateTimeFormat = "%Y-%m-%d %H:%M:%S" # DATE FORMAT USED BY ONERAIN FOR DATETIMES

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

            # PING CONFIGURED ONERAIN URL WITH GetTime REQUEST TO MAKE SURE IT'S A VALID ENDPOINT
            get_time_url = f'{url}?method=GetTime'
         
            # use GetTime method to validate well formed url and that it responds to this 
            # basic time get request    
            r = requests.get(get_time_url,timeout=HttpResponseTimeout)
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
                "location":{"desription":"describes site location","type":"string"},
                "owner":{"desription":"DEPRECATED","type":"string"},
                "system_id":{"description":"identifies the input system for which the site belongs.", "type":"integer"},
                "client_id":{"description":"identifies the client that owns the input system for which the site belongs.","type":"string"},
                "latitude_dec":{"description":"latitude of site in decimal form","type":"number"},
                "longitude_dec":{"description":"longitude of site in decimal form","type":"number"},
                "elevation":{"description":"elevation of site","type":"number"},
            },
        }
        streams.append(AirbyteStream(name=stream_name, 
                                     supported_sync_modes=["full_refresh"], # don't need incremental for site metadata. small dataset
                                     source_defined_cursor=False, # small dataset don't need 
                                     json_schema=json_schema))

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
                "location":{"description":"site name","type":"string"},
                "description":{"description":"sensor name", "type":"string"},
                "sensor_class":get_spec_def_obj('class'),
                "sensor_type":{"description":"source type of data","type":"string"},
                "units":get_spec_def_obj('units'),
                "translate":{"description":"text translation enabled", "type":"boolean"}, 
                "precision":{"description":"number of decimals displayed for Reading/Finished value in user interface", "type":"integer"},
                "last_time":{"description":"last data time; see GetSensorData A5","type":"string"},
                "last_value":{"description":"last Reading/Finished; see GetSensorData A8", "type":"number"},
                "last_time_received":{"description":"last data time; see GetSensorData A5", "type":"string"},
                "last_value_received":{"description":"last Reading/Finished value; see GetSensorData A8", "type":"number"},
                "last_raw_value":{"description":"last raw value; see GetSensorData A6", "type":"number"},
                "last_raw_value_received":{"description":"last raw value received; see GetSensorData A6","type":"number"},
                "change_time":{"description":"time of last change to sensor metadata","type":"string"},
                "normal":{"description":"is sensor in normal mode (not timed out)?", "type":"integer"}, # boolean?
                "active":{"description":"is sensor active (not in maintenance mode/out of service)?", "type":"integer"}, #boolean?
                "valid":{"description":"*may* indicate if last value is valid. unknown", "type":"integer"}, #boolean?
                "change_rate":{"description":"DEPRECATED/UNUSED", "type":"number"},
                "time_min_consec_zeros":{"description":"DEPRECATED/UNUSED", "type":"integer"},
                "validation":{"description":"validation protocol for finished value", "type":"string"},
                "value_max":{"description":"validation parameter: maximum value", "type":"number"},
                "value_min":{"description":"validation parameter: minimum value", "type":"number"},
                "delta_pos":{"description":"validation parameter: positive delta", "type":"number"},
                "delta_neg":{"description":"validation parameter: negative delta", "type":"number"},
                "rate_pos":{"description":"DEPRECATED", "type":"integer"},
                "rate_neg":{"description":"DEPRECATED", "type":"integer"},
                "time_max":{"description":"validation parameter: maximum time", "type":"integer"},
                "time_min":{"description":"validation parameter: minimum time", "type":"integer"},
                "slope":{"description":"used in data conversion; multiplicative value", "type":"number"},
                "offset":{"description":"used in data conversion; additive value", "type":"number"},
                "reference":{"description":"used in data conversion; additive value", "type":"number"},
                "utc_offset":{"description":"the numeric offset (in hours) from Universal Coordinated Time", "type":"integer"},
                "using_dst":{"description":"DEPRECATED", "type":"boolean"},
                "conversion":{"description":"conversion protocol for raw to finished value", "type":"string"},
                "usage":{"description":"DEPRECATED/UNUSED", "type":"string"},
                "protocol":{"description":"DEPRECATED/UNUSED", "type":"integer"}  

            }
        } 
        streams.append(AirbyteStream(name=stream_name, 
                                     supported_sync_modes=["full_refresh"], # don't need incremental. small dataset
                                     source_defined_cursor=False,
                                     json_schema=json_schema))

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
                    "description":"finished data value with precision (conversion) applied",
                 
                },
                "data_quality": get_spec_def_obj('data_quality'),
                "raw_value": {
                    "type":"number",
                    "description":"this is the value supplied by the source system. It is the value before any conversion or validation is applied.",
                },
                "units": get_spec_def_obj('units')
    
                
            }
        }

        streams.append(AirbyteStream(name=stream_name, 
                                     supported_sync_modes=["full_refresh","incremental"],
                                     source_defined_cursor=True,
                                     json_schema=json_schema))

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
         

        req_url = get_request_url(stream_name,config)


        # iterate configured streams and fetch their data
        for stream in catalog.streams:
            #logger.debug(f"configured catalog stream: {stream}")
            stream_name = stream.stream.name
            is_incremental = stream.sync_mode == SyncMode.incremental # and key in state

            logger.info(f"incremental state for stream {stream_name}: {is_incremental}: stream.sync_mode = '{stream.sync_mode}', SyncMode.incremental = '{SyncMode.incremental}'")
            req_url = get_request_url(stream_name,config)
            if stream_name == StreamGetSiteMetaData:
                data = get_site_metadata(req_url,logger,state,config,stream_name,is_incremental) 
            elif stream_name == StreamGetSensorMetaData:
                data = get_sensor_metadata(req_url,logger,state,config,stream_name,is_incremental)
            elif stream_name == StreamGetSensorData:
                data = get_sensor_data(logger,state,config,stream_name,is_incremental)
            else:
                raise NotImplementedError(f"read(): don't handle stream {key} found in catalog")

            result_count=0
            for d in data:
                result_count=result_count+1
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(stream=stream_name, data=d, emitted_at=int(datetime.now().timestamp()) * 1000),
                )

            if result_count < 1:
                logger.debug(f'no new data for {stream_name}: state={state.get(stream_name)}')



        # RETRIEVE SENSOR METADATA AND RETURN AS STREAM
        stream_name = StreamGetSensorMetaData

        req_url = get_request_url(stream_name,config)

        # RETRIEVE SENSOR DATA AND RETURN AS STREAM
        stream_name = StreamGetSensorData

        req_url = get_request_url(stream_name,config)



def str_to_bool(s):
    true_values = ['true','t','yes','y',1,'1']
    false_values = ['false','f','no','n',0,'0']

    if s.lower() in true_values:
        return True
    if s.lower() in false_values:
        return False

    raise ValueError(f"cannot convert '{s}' to boolean. expected {true_values} or {false_values}")

def assert_onerain_response(response_object,expect_http_code,logger):
    "ensure onerain response object is well formed"
    assert isinstance(expect_http_code,int)
    assert response_object.status_code == expect_http_code


    doc = xmltodict.parse(response_object.text)
    assert 'onerain' in doc
    if 'error' in doc['onerain']:
        err_msg  = doc['onerain']['error']
        raise ValueError(err_msg)
    

    # if 'row' key is not an ordered dictionary then return
    # empty ordered dictionary 
 
    try:
        general = doc['onerain']['response']['general']

        rows=None
        if general is not None and 'row' in  general:
            rows=general['row'] 
            if isinstance(rows,list):
                return rows #multiple rows
            elif isinstance(rows,OrderedDict):
                return [rows] #single row

    except Exception as e:
        logger.warn("expected one rain xml response element hierarchey onerain->response->general->row, found %s: %s" % (response_object.text,e))
 
    return []



def get_request_url(stream,config,override_query_params={}):
    "generate onerain url based on stream and config"
    query_params=dict()
    data_api_url = config[ConfigPropDataApiUrl]
    query_params[ConfigPropSystemKey] = config[ConfigPropSystemKey]

 
    if stream in config:
        for stream_prop in config[stream]:
            if stream_prop in override_query_params:
                query_params[stream_prop] = override_query_params[stream_prop]
            else:
                query_params[stream_prop] = config[stream][stream_prop]

    return f'{data_api_url}?method={stream}&{urlencode(query_params)}'

def get_site_metadata(req_url,logger,state,config,stream_name,is_incremental):
    "retreive sitemetadata from onerain"

    # RETRIEVE SITE METADATA
    try:
        logger.info(f'requesting {req_url}')
        r = requests.get(req_url,timeout=HttpResponseTimeout)

        # ITERATE SITE METADATA AND RETURN AS STREAM
        results = assert_onerain_response(r,200,logger)

        for row in results:
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

            yield data

    except Exception as e:
        logger.error(f'failed to process stream {stream_name}: {traceback.format_exc()}')

def get_sensor_metadata(req_url,logger,state,config,key,is_incremental):
    "retrieve sensor metadata from onerain"

    logger.info(f'requesting {req_url}')

    try:
        # submit request
        r = requests.get(req_url,timeout=HttpResponseTimeout)
        results = assert_onerain_response(r,200,logger) 
        
        for row in results:

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
            if 'change_time' in row: # not always populated
                data['change_time'] = row['change_time']
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
            data['rate_neg'] = int(row['rate_neg'])
            data['rate_pos'] = int(row['rate_pos'])

            yield data 

    except Exception as e:
        logger.error(f'failed to process stream {key}: {traceback.format_exc()}') 


def get_sensor_data(logger,state,config,stream_name,is_incremental):
    "retrieve sensor data from onerain"

    override_query_params = {}

    # check if either data_start     
    has_data_start = 'data_start' in config[stream_name]
    has_data_end = 'data_end' in config[stream_name]

    logger.info(f"has_data_start: {has_data_start}")

    if has_data_start:
        data_start = config[stream_name]['data_start']
        if is_incremental:
            # start date begins with last cursor value in incremental mode
            if stream_name in state: # may be in incremental mode but cursor not initialized yet
                data_start = override_query_params['data_start'] = state[stream_name]
                logger.debug(f"overriding config value 'data_start' for stream {stream_name} with current stream cursor value {state[stream_name]}")

        data_end = onerain_datetime_now() # default to now 
        if has_data_end:
            data_end = config[stream_name]['data_end'] # set end of date range to whatever is configured 
        else:
            # set configured end of data range to default (now)  
            config[stream_name]['data_end'] = data_end

        # iterate through supplied date range in 1 day increments. each day is an API call
        increment_days=1 
        for start_dt,end_dt in data_range(data_start,data_end,increment_days):
                override_query_params['data_start'] = start_dt
                override_query_params['data_end'] = end_dt
                for data in call_sensor_data_api(logger,state,config,stream_name,override_query_params,is_incremental):
                    yield data
    else:
        # no date range specified just call once
        for data in call_sensor_data_api(logger,state,config,stream_name,override_query_params,is_incremental):
            yield data


def call_sensor_data_api(logger,state,config,stream_name,override_query_params,is_incremental):
    "invoke onerain api 'GetSensorData' call and return results"
    req_url = get_request_url(stream_name,config,override_query_params)

    logger.info(f'requesting {req_url}')
    
    try:
        # submit request
        r = requests.get(req_url,timeout=HttpResponseTimeout)

        results = assert_onerain_response(r,200,logger)

        for row in results:
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
            data['data_quality'] = row['data_quality']

            yield data 

            # update cursor for this stream
            if is_incremental:
                state[stream_name] = data['data_time']
                update_state(state)

    except Exception as e:
        logger.error(f'failed to process stream {stream_name}: {traceback.format_exc()}') 

def update_state(state):
    "sends an update of the state variable to stdout"
    output_message = {"type":"STATE","state":{"data":state}}
    print(json.dumps(output_message))


def onerain_datetime_to_datetime(yyyy_mm_dd_hh_mm_ss):
    " takes a date (string) formatted as YYYY-MM-DD HH:MM:SS and converts to a datetime.datetime object"
    return datetime.strptime(yyyy_mm_dd_hh_mm_ss,OneRainDateTimeFormat)

def add_time_days(yyyy_mm_dd_hh_mm_ss,num_days):
    "add number of days to supplied date/time and return it as string in same format"

    # convert to datetime object   
    dt = onerain_datetime_to_datetime(yyyy_mm_dd_hh_mm_ss) 
    # add num days
    nt = dt + timedelta(days=num_days)
    # convert from datetime back to string in same format supplied
    return nt.strftime(OneRainDateTimeFormat)

def diff_days(d1,d2):
    "subtract d1 - d2 and return number of days difference. both dates are strings in yyyy-mm-dd hh:mm:ss format"

    dt1 = onerain_datetime_to_datetime(d1) #datetime.strptime(d1,OneRainDateTimeFormat)
    dt2 = onerain_datetime_to_datetime(d2) #datetime.strptime(d2,OneRainDateTimeFormat)
    return (dt1-dt2).days

def onerain_datetime_now():
    "return current time in onerain datetime format"
    return datetime.now().strftime(OneRainDateTimeFormat)

def data_range(dt_start,dt_end,increment_days):
    "use dt_start and dt_end range to return a list of date range tuple/pairs that span increment_days" 
    dt=onerain_datetime_to_datetime
    while dt(dt_start) < dt(dt_end):
            dt_incremental_end = add_time_days(dt_start,increment_days)
            if dt(dt_incremental_end) > dt(dt_end):
                dt_incremental_end = dt_end
            yield dt_start,dt_incremental_end
            dt_start = dt_incremental_end
 
