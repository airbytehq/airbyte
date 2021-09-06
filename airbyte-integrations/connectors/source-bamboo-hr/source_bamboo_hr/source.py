#
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
#


import base64
import json
from datetime import datetime
from typing import Dict, Generator

import requests
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
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode
from airbyte_cdk.sources import Source
from requests.models import Response


class BambooHrClient(object):
    def __init__(self, config: json) -> None:
        self.api_key = config["api_key"]
        self.subdomain = config["subdomain"]

    def _prepare_request_auth(self):
        return base64.b64encode("{}:x".format(self.api_key).encode("utf-8")).decode("utf-8")

    def request(self, uri: str, method: str = "GET", data={}, **kwargs) -> Response:
        url = "https://api.bamboohr.com/api/gateway.php/{}/v1/{}".format(self.subdomain, uri)
        headers = kwargs.get("headers", {})
        headers.update(
            {
                "Authorization": "Basic {}".format(self._prepare_request_auth()),
                "Accept": "application/json",
                "Content-Type": kwargs.get("content_type") or "application/json",
            }
        )

        if data and not isinstance(data, str) and headers["Content-Type"] == "application/json":
            data = json.dumps(data)

        response = requests.request(method=method, url=url, headers=headers)
        response.raise_for_status()
        return response


class SourceBambooHr(Source):
    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            bamboo = BambooHrClient(config)
            bamboo.request("employees/directory")
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

        bamboo = BambooHrClient(config)
        fields = bamboo.request("meta/fields").json()
        properties = {}

        for field in fields:
            # All fields are nullable strings
            # https://documentation.bamboohr.com/docs/field-types
            properties[field.get("alias", field["name"])] = {"type": ["null", "string"]}

        stream_name = "employee"
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
        }
        streams.append(
            AirbyteStream(
                name=stream_name,
                json_schema=json_schema,
                supported_sync_modes=[SyncMode.full_refresh],
                supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
            )
        )
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
        stream_name = "employee"

        bamboo = BambooHrClient(config)
        data = bamboo.request("employees/directory").json()
        employees = data["employees"]

        for employee in employees:
            yield AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(stream=stream_name, data=employee, emitted_at=int(datetime.now().timestamp()) * 1000),
            )
