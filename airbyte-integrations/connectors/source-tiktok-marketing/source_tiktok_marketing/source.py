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


import json
from datetime import datetime
from typing import Dict, Generator
from airbyte_cdk.models import ConnectorSpecification
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
from airbyte_cdk.sources import Source
from .spec import SourceTikTokMarketingSpec
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


DOCUMENTATION_URL = "https://docs.airbyte.io/integrations/sources/tiktok-marketing"


class TiktokTokenAuthenticator(TokenAuthenticator):
    """
    Docs: https://ads.tiktok.com/marketing_api/docs?rid=sta6fe2yww&id=1701890922708994
    """

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Access-Token": self._token}




class SourceTiktokMarketing(Source):

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """Returns the spec for this integration."""
        # make dummy instance of stream_class in order to get 'supports_incremental' property
        # incremental = self.stream_class(dataset="", provider="", format="", path_pattern="").supports_incremental

        # supported_dest_sync_modes = [DestinationSyncMode.overwrite]
        # if incremental:
        #     supported_dest_sync_modes.extend([DestinationSyncMode.append, DestinationSyncMode.append_dedup])
        
        return ConnectorSpecification(
            documentationUrl=DOCUMENTATION_URL,
            changelogUrl=DOCUMENTATION_URL,
            # supportsIncremental=incremental,
            # supported_destination_sync_modes=supported_dest_sync_modes,
            connectionSpecification=SourceTikTokMarketingSpec.schema(),
        )




    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """

        # Define the endpoint from user's config
        url_base = get_url_base(config["is_sandbox"])
        try:
            ZuoraAuthenticator(
                token_refresh_endpoint=f"{url_base}/oauth/token",
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                refresh_token=None,  # Zuora doesn't have Refresh Token parameter.
            ).get_auth_header()
            return True, None
        except Exception as e:
            return False, e


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

        stream_name = "TableName"  # Example
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"columnName": {"type": "string"}},
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
        stream_name = "TableName"  # Example
        data = {"columnName": "Hello World"}  # Example

        # Not Implemented

        yield AirbyteMessage(
            type=Type.RECORD,
            record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
        )
