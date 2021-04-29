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
import csv
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
    Status,
    Type,
    SyncMode
)
from base_python import AirbyteLogger, Source

from .email_client import Client


class SourceCabqGwl(Source):
    _client = None

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
            # client = get_client(logger, config)
            self._client = Client(config)
            self._client.login()
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
        streams = []

        stream_name = "GWL"  # Example
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            # "properties": {"columnName": {"type": "string"}},
            "properties": {'facility_id': {'type': 'string'},
                           'facility_code': {'type': 'string'},
                           'sys_loc_code': {'type': 'string'},
                           'loc_name': {'type': 'string'},
                           'loc_group': {'type': 'string'},
                           'loc_report_order': {'type': 'string'},
                           'measurement_date': {'type': 'string'},
                           'reference_elev': {'type': 'string'},
                           'water_level': {'type': 'string'},
                           'exact_elev': {'type': 'string'},
                           'measured_depth_of_well': {'type': 'string'},
                           'depth_unit': {'type': 'string'},
                           'batch_number': {'type': 'string'},
                           'technician': {'type': 'string'},
                           'dry_indicator_yn': {'type': 'string'},
                           'measurement_method': {'type': 'string'},
                           'dip_or_elevation': {'type': 'string'},
                           'remark': {'type': 'string'},
                           'equipment_code': {'type': 'string'},
                           'lnapl_cas_rn': {'type': 'string'},
                           'lnapl_depth': {'type': 'string'},
                           'lnapl_thickness': {'type': 'string'},
                           'lnapl_density': {'type': 'string'},
                           'water_depth': {'type': 'string'},
                           'dnapl_cas_rn': {'type': 'string'},
                           'dnapl_depth': {'type': 'string'},
                           'dnapl_thickness': {'type': 'string'},
                           'task_code': {'type': 'string'},
                           'approval_code': {'type': 'string'},
                           'x_coord': {'type': 'string'},
                           'y_coord': {'type': 'string'},
                           'longitude': {'type': 'string'},
                           'latitude': {'type': 'string'},
                           }
        }

        streams.append(AirbyteStream(name=stream_name,
                                     supported_sync_modes=["full_refresh", "incremental"],
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
        logger.debug('readadfasfasdfasdf')

        # stream_name = "TableName"  # Example
        data = {"columnName": "Hello World"}  # Example
        for stream in catalog.streams:
            key = stream.stream.name
            prid = None
            if stream.sync_mode == SyncMode.incremental and key in state:
                prid = state.get(key)

            ret = self._get_records(logger, config, prid)
            if ret is not None:
                rid, records = ret
                if records:

                    for data in records:
                        for k, v in data.items():
                            if v.isdigit():
                                continue

                            try:
                                data[k] = float(v)
                            except ValueError:
                                pass
                        # print(data)
                        # print(json.dumps(data))
                        record = AirbyteRecordMessage(stream=key, data=data,
                                                      emitted_at=int(datetime.now().timestamp()) * 1000)
                        yield AirbyteMessage(type=Type.RECORD,
                                             record=record)

                    state[key] = rid
                    output_message = {"type": "STATE", "state": {"data": state}}
                    print(json.dumps(output_message))

    def _get_records(self, logger, config, prev_id):
        if self._client is None:
            self._client = Client(config)
            self._client.login()

        ret = self._client.fetch_attachment(logger, prev_id)
        if ret is not None:
            header, f = ret
            dialect = csv.Sniffer().sniff(f.readline())
            f.seek(0)

            records = [row for row in csv.DictReader(f, dialect=dialect)]
            # print('sad', records)
            return header, records
