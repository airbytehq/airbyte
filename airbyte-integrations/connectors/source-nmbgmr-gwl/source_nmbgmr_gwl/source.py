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
import uuid

import requests
import json
from datetime import datetime
from typing import Dict, Generator

from airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    AirbyteStateMessage,
    Status,
    Type,
    SyncMode
)
from base_python import AirbyteLogger, Source


class SourceNmbgmrGwl(Source):
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
            url = f'{sitemetadata_url(config)}?count=1'
            resp = get_resp(logger, url)
            if not resp.status_code == 200:
                raise Exception
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
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """
        pressure_gwl_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                               'type': 'object',
                               'properties': {'OBJECTID': {'type': 'number'},
                                              'PointID': {'type': 'string'},
                                              'WellID': {'type': 'string'},
                                              'GlobalID': {'type': 'string'},
                                              'DateTimeMeasured': {'type': 'string',
                                                                   'format': 'date-time'},
                                              'DepthToWaterBGS': {'type': 'number'},
                                              'WaterHead': {'type': 'number'},
                                              'WaterHeadAdjusted': {'type': 'number'},
                                              'DataSource': {'type': 'string'},
                                              'MeasuringAgency': {'type': 'string'},
                                              'MeasurementMethod': {'type': 'string'},
                                              }
                               }
        acoustic_gwl_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                               'type': 'object',
                               'properties': {'OBJECTID': {'type': 'number'},
                                              'PointID': {'type': 'string'},
                                              'WellID': {'type': 'string'},
                                              'GlobalID': {'type': 'string'},
                                              'DateTimeMeasured': {'type': 'string',
                                                                   'format': 'date-time'},
                                              'DepthToWaterBGS': {'type': 'number'},
                                              'DataSource': {'type': 'string'},
                                              'MeasuringAgency': {'type': 'string'},
                                              'MeasurementMethod': {'type': 'string'},
                                              'import_uuid': {'type': 'string'}
                                              }
                               }
        manual_gwl_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                             'type': 'object',
                             'properties': {'OBJECTID': {'type': 'number'},
                                            'PointID': {'type': 'string'},
                                            'WellID': {'type': 'string'},
                                            'GlobalID': {'type': 'string'},
                                            'DateTimeMeasured': {'type': 'string',
                                                                 'format': 'date-time'},
                                            'DepthToWaterBGS': {'type': 'number'},
                                            'DepthToWater': {'type': 'number'},
                                            'SiteNotes': {'type': 'string'},
                                            'DataSource': {'type': 'string'},
                                            'MeasuringAgency': {'type': 'string'},
                                            'MeasurementMethod': {'type': 'string'},
                                            'LevelStatus': {'type': 'string'},
                                            'DataQuality': {'type': 'string'},
                                            'MPHeight': {'type': 'number'},
                                            }
                             }

        site_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                       'type': 'object',
                       'properties': {'OBJECTID': {'type': 'number'},
                                      'PointID': {'type': 'string'},
                                      'OSEWellID': {'type': 'string'},
                                      'WellID': {'type': 'string'},
                                      'OSEWelltagID': {'type': 'string'},
                                      'HoleDepth': {'type': 'number'},
                                      'WellDepth': {'type': 'number'},
                                      'DepthSource': {'type': 'string'},
                                      'CompletionDate': {'type': 'string'},
                                      'CompletionSource': {'type': 'string'},
                                      'MeasuringPoint': {'type': 'string'},
                                      'MPHeight': {'type': 'number'},
                                      'CasingDiameter': {'type': 'number'},
                                      'CasingDepth': {'type': 'number'},
                                      'CasingDescription': {'type': 'string'},
                                      'DrillerName': {'type': 'string'},
                                      'ConstructionMethod': {'type': 'string'},
                                      'ConstructionNotes': {'type': 'string'},
                                      'AquiferType': {'type': 'string'},
                                      'AqClass': {'type': 'string'},
                                      'FormationZone': {'type': 'string'},
                                      'StaticWater': {'type': 'number'},
                                      'WaterNotes': {'type': 'string'},
                                      'Status': {'type': 'string'},
                                      'StatusDescription': {'type': 'string'},
                                      'CurrentUse': {'type': 'string'},
                                      'CurrentUseDescription': {'type': 'string'},
                                      'StatusUserNotes': {'type': 'string'},
                                      'MonitoringStatus': {'type': 'string'},
                                      'OpenWellLoggerOK': {'type': 'string'},
                                      'MonitorOK': {'type': 'string'},
                                      'SampleOK': {'type': 'string'},
                                      'DataSource': {'type': 'string'},
                                      'Notes': {'type': 'string'},
                                      'MonitorGroup': {'type': 'number'},
                                      'WellPdf': {'type': 'string'},
                                      'MonitorStatusReason': {'type': 'string'},
                                      'HydrographInterp': {'type': 'string'},
                                      'PrimaryUseSite_USGS': {'type': 'string'},
                                      'PrimaryUseWater_USGS': {'type': 'string'},
                                      'DateCreated': {'type': 'string'},
                                      'SiteNames': {'type': 'string'},
                                      'SiteID': {'type': 'string'},
                                      'AlternateSiteID': {'type': 'string'},
                                      'AlternateSiteID2': {'type': 'string'},
                                      'SiteDate': {'type': 'string'},
                                      'DataReliability': {'type': 'string'},
                                      'Confidential': {'type': 'boolean'},
                                      'SiteType': {'type': 'string'},
                                      'WL_Continuous': {'type': 'boolean'},
                                      'WL_Intermittent': {'type': 'boolean'},
                                      'WaterQuality': {'type': 'boolean'},
                                      'WaterFlow': {'type': 'boolean'},
                                      'Hydraulic': {'type': 'boolean'},
                                      'Subsurface': {'type': 'boolean'},
                                      'WellorSpgNoData': {'type': 'boolean'},
                                      'SubsurfaceType': {'type': 'string'},
                                      'Easting': {'type': 'number'},
                                      'Northing': {'type': 'number'},
                                      'UTMDatum': {'type': 'string'},
                                      'CoordinateNotes': {'type': 'string'},
                                      'Altitude': {'type': 'number'},
                                      'AltitudeAccuracy': {'type': 'string'},
                                      'AltitudeMethod': {'type': 'string'},
                                      'AltDatum': {'type': 'string'},
                                      'Latitude': {'type': 'number'},
                                      'Longitude': {'type': 'number'},
                                      'LatLonDatum': {'type': 'string'},
                                      'CoordinateAccuracy': {'type': 'string'},
                                      'CoordinateMethod': {'type': 'string'},
                                      'Township': {'type': 'number'},
                                      'TownshipDirection': {'type': 'string'},
                                      'Range': {'type': 'string'},
                                      'RangeDirection': {'type': 'string'},
                                      'SectionQuarters': {'type': 'number'},
                                      'SPX': {'type': 'string'},
                                      'SPY': {'type': 'string'},
                                      'QuadName': {'type': 'string'},
                                      'County': {'type': 'string'},
                                      'State': {'type': 'string'},
                                      'LocationNotes': {'type': 'string'},
                                      'WLReportDeliver': {'type': 'string'},
                                      'ChemistryReportDeliver': {'type': 'string'},
                                      'WLReportNote': {'type': 'string'},
                                      'ChemistryReportNote': {'type': 'string'},
                                      'X_NAD83_Zone12': {'type': 'number'},
                                      'Y_NAD83_Zone12': {'type': 'number'},
                                      'projectname': {'type': 'string'},
                                      'USGSProjectID': {'type': 'string'},
                                      'LatitudeDD': {'type': 'string'},
                                      'LongitudeDD': {'type': 'string'},
                                      'PublicRelease': {'type': 'boolean'},
                                      }}

        screens_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                          'type': 'object',
                          'properties': {'WellID': {'type': 'string'},
                                         'WDBID': {'type': 'number'},
                                         'PointID': {'type': 'string'},
                                         'counter': {'type': 'number'},
                                         'ScreenTop': {'type': 'number'},
                                         'ScreenBottom': {'type': 'number'},
                                         'ScreenDescription': {'type': 'string'},
                                         'OBJECTID': {'type': 'number'},
                                         'GlobalID': {'type': 'string'},
                                         }}

        streams = [
            AirbyteStream(name='ManualGWL',
                          supported_sync_modes=["full_refresh", ],
                          source_defined_cursor=True,
                          json_schema=manual_gwl_schema),
            AirbyteStream(name='PressureGWL',
                          supported_sync_modes=["full_refresh", ],
                          source_defined_cursor=True,
                          json_schema=pressure_gwl_schema),
            # AirbyteStream(name='Manual',
            #               supported_sync_modes=["full_refresh", "incremental"],
            #               source_defined_cursor=True,
            #               json_schema=gwl_schema),
            # AirbyteStream(name='Pressure',
            #               supported_sync_modes=["full_refresh", "incremental"],
            #               source_defined_cursor=True,
            #               json_schema=gwl_schema),
            AirbyteStream(name='AcousticGWL',
                          supported_sync_modes=["full_refresh", ],
                          source_defined_cursor=True,
                          json_schema=acoustic_gwl_schema
                          ),
            AirbyteStream(name='WellScreens',
                          supported_sync_modes=["full_refresh", ],
                          source_defined_cursor=True,
                          json_schema=screens_schema),
            AirbyteStream(name='SiteMetaData',
                          supported_sync_modes=['full_refresh', ],
                          source_defined_cursor=True,
                          json_schema=site_schema)]

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

        for stream in catalog.streams:
            name = stream.stream.name
            key = stream.stream.name
            logger.debug(f'****** mode {stream.sync_mode} state={state}')
            if key == 'SiteMetaData':
                url = sitemetadata_url(config)
            elif key == 'WellScreens':
                url = screens_url(config)
            elif key == 'ManualGWL':
                url = manual_water_levels_url(config)
            elif key == 'PressureGWL':
                url = pressure_water_levels_url(config)
            elif key == 'AcousticGWL':
                url = acoustic_water_levels_url(config)
            else:
                continue

            while 1:
                objectid = state[key]
                if objectid:
                    curl = f'{url}?objectid={objectid}'
                else:
                    curl = url

                logger.info(f'fetching url={curl}')
                jobj = get_json(logger, curl)
                if jobj:
                    state[key] = jobj[-1]['OBJECTID']
                else:
                    break

                for di in jobj:
                    di['import_uuid'] = str(uuid.uuid4())
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=name, data=di,
                                                    emitted_at=int(datetime.now().timestamp()) * 1000))


def update_state(state):
    output_message = {"type": "STATE", "state": {"data": state}}
    print(json.dumps(output_message))


def public_url(config):
    return f'{config["url"]}/maps/data/waterlevels'


def records_url(config, tag):
    pu = public_url(config)
    url = f'{pu}/records_{tag}'
    return url


def sitemetadata_url(config):
    return f'{public_url(config)}/sitemetadata'


def screens_url(config):
    return f'{public_url(config)}/wellscreens'


def manual_water_levels_url(config):
    return f'{public_url(config)}/manual_gwl'


def pressure_water_levels_url(config):
    return f'{public_url(config)}/pressure_gwl'


def acoustic_water_levels_url(config):
    return f'{public_url(config)}/acoustic_gwl'


def get_resp(logger, url):
    resp = requests.get(url)
    logger.debug(f'url={url}, resp={resp}')
    if resp.status_code == 200:
        return resp


def get_json(logger, url):
    resp = get_resp(logger, url)
    if resp:
        jobj = resp.json()
        return jobj

# EOF ========================================================================
# is_incremental = stream.sync_mode == SyncMode.incremental and key in state
# if key == 'SiteMetaData':
#     # data = get_sitemetadata(logger, state, config, key, is_incremental)
#
# elif key == 'Screens':
#     url = screens_url(config)
#     while 1:
#         url = f'{url}?objectid={state[key]}'
#         jobj = get_json(logger, url)
#         if jobj:
#             state[key] = jobj[-1]['OBJECTID']
#         for di in data:
#             yield AirbyteMessage(
#                 type=Type.RECORD,
#                 record=AirbyteRecordMessage(stream=name, data=di,
#                                             emitted_at=int(datetime.now().timestamp()) * 1000))
#     update_state(state)
#     return
# else:
#     data = get_waterlevels(logger, state, config, key, is_incremental)
#
# if data:
#     for di in data:
#         yield AirbyteMessage(
#             type=Type.RECORD,
#             record=AirbyteRecordMessage(stream=name, data=di,
#                                         emitted_at=int(datetime.now().timestamp()) * 1000))
# else:
#     logger.debug('no new data for {}. state={}'.format(name, state.get(name)))

# data = get_data(logger, stream, state, config)
# if data:
#
# else:
#     logger.debug('no new data for {}. state={}'.format(name, state.get(name)))


# def get_screens(logger, state, config, key, is_incremental):
#     url = screens_url(config)
#     # if is_incremental:
#     #     url = f'{url}?objectid={state[key]}'
#     # else:
#     #     url = f'{url}?objectid=0'
#     screens = []
#     while 1:
#         url = f'{url}?objectid={state[key]}'
#         jobj = get_json(logger, url)
#         if jobj:
#             state[key] = jobj[-1]['OBJECTID']
#         screens.append(jobj)
#
#     update_state(state)
#     return jobj
#     # else:
# need to emit the current state to make sure it cares forward
# update_state(state)
# to allow looping dont emit the state.
# since the state is now None the next iteration the cursor will reset
# this allows for sites to be edited


# def get_sitemetadata(logger, state, config, key, is_incremental):
#     url = sitemetadata_url(config)
#     if is_incremental:
#         url = f'{url}?objectid={state[key]}'
#     else:
#         url = f'{url}?objectid=0'
#
#     jobj = get_json(logger, url)
#     if jobj:
#         state[key] = jobj[-1]['OBJECTID']
#         update_state(state)
#         return jobj
#     else:
#         # need to emit the current state to make sure it cares forward
#         update_state(state)


# def get_waterlevels(logger, state, config, key, is_incremental):
#     cursor_key = 'OBJECTID'
#
#     url = records_url(config, key.lower())
#     if is_incremental:
#         ndata = []
#         for i in range(10):
#             nurl = f'{url}?objectid={state[key]}&count=5000'
#             jobj = get_json(logger, nurl)
#             if jobj:
#                 # update state
#                 state[key] = jobj[-1][cursor_key]
#                 update_state(state)
#                 ndata.extend(jobj)
#             else:
#                 break
#         update_state(state)
#         return ndata
#     else:
#         url = f'{url}?objectid=0'
#         jobj = get_json(logger, url)
#         if jobj:
#             # update state
#             state[key] = jobj[-1][cursor_key]
#             update_state(state)
#             return jobj
#         else:
#             update_state(state)
