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
            resp = get_resp(logger, public_url(config))
            if not resp.status_code == 200:
                raise BaseException
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
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"PointID": {"type": "string"},
                           "DateMeasured": {"type": "string"},
                           "DepthToWaterBGS": {"type": "float"}}}

        streams = [AirbyteStream(name='Acoustic',
                                 supported_sync_modes=["full_refresh", "incremental"],
                                 source_defined_cursor=True,
                                 json_schema=json_schema),
                   AirbyteStream(name='Manual',
                                 supported_sync_modes=["full_refresh", "incremental"],
                                 source_defined_cursor=True,
                                 json_schema=json_schema),
                   AirbyteStream(name='Pressure',
                                 supported_sync_modes=["full_refresh", "incremental"],
                                 source_defined_cursor=True,
                                 json_schema=json_schema)]
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
            data = get_data(logger, stream, state, config)
            if data:
                for di in data:
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=name, data=di,
                                                    emitted_at=int(datetime.now().timestamp()) * 1000))
            else:
                logger.debug('no new data for {}. state={}'.format(name, state.get(name)))


def public_url(config):
    return f'{config["url"]}/maps/data/waterlevels'


def records_url(config, tag):
    pu = public_url(config)
    url = f'{pu}/records/{tag}'
    return url


def get_data(logger, stream, state, config):
    key = stream.stream.name
    url = records_url(config, key.lower())
    logger.debug(f'****** mode {stream.sync_mode} state={state}')
    if stream.sync_mode == SyncMode.incremental and key in state:
        url = f'{url}?start_date={state.get(key)}'
    else:
        url = f'{url}?count=10'

    jobj = get_json(logger, url)
    if jobj:
        # update state
        state[key] = jobj[-1]['DateMeasured']
        output_message = {"type": "STATE", "state": {"data": state}}
        print(json.dumps(output_message))
        return jobj


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
