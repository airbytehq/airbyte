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

import copy
from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import split_config

from .api import UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .streams import BulkIncrementalSalesforceStream, BulkSalesforceStream, IncrementalSalesforceStream, SalesforceStream


class SourceSalesforce(AbstractSource):
    @staticmethod
    def _get_sf_object(config: Mapping[str, Any]) -> Salesforce:
        sf = Salesforce(**config)
        sf.login()
        return sf

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        _ = self._get_sf_object(config)
        return True, None

    def streams(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog = None) -> List[Stream]:
        sf = self._get_sf_object(config)
        authenticator = TokenAuthenticator(sf.access_token)
        stream_names = sf.get_validated_streams(catalog=catalog)

        if config["api_type"] == "REST":
            full_refresh, incremental = SalesforceStream, IncrementalSalesforceStream
        else:
            full_refresh, incremental = BulkSalesforceStream, BulkIncrementalSalesforceStream

        streams = []
        for stream_name in stream_names:
            json_schema = sf.generate_schema(stream_name)
            pk, replication_key = sf.get_pk_and_replication_key(json_schema)
            streams_kwargs = dict(sf_api=sf, pk=pk, stream_name=stream_name, schema=json_schema, authenticator=authenticator)
            if replication_key and stream_name not in UNSUPPORTED_FILTERING_STREAMS:
                streams.append(incremental(**streams_kwargs, replication_key=replication_key, start_date=config["start_date"]))
            else:
                streams.append(full_refresh(**streams_kwargs))

        return streams

    def read(
        self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog, state: MutableMapping[str, Any] = None
    ) -> Iterator[AirbyteMessage]:
        """
        Overwritten to dynamically receive only those streams that are necessary for reading for significant speed gains
        (Salesforce has a strict API limit on requests).
        """
        connector_state = copy.deepcopy(state or {})
        config, internal_config = split_config(config)
        # get the streams once in case the connector needs to make any queries to generate them
        logger.info("Starting generating streams")
        stream_instances = {s.name: s for s in self.streams(config, catalog=catalog)}
        logger.info(f"Starting syncing {self.name}")
        for configured_stream in catalog.streams:
            stream_instance = stream_instances.get(configured_stream.stream.name)
            if not stream_instance:
                raise KeyError(
                    f"The requested stream {configured_stream.stream.name} was not found in the source. Available streams: {stream_instances.keys()}"
                )

            try:
                yield from self._read_stream(
                    logger=logger,
                    stream_instance=stream_instance,
                    configured_stream=configured_stream,
                    connector_state=connector_state,
                    internal_config=internal_config,
                )
            except Exception as e:
                logger.exception(f"Encountered an exception while reading stream {self.name}")
                raise e

        logger.info(f"Finished syncing {self.name}")
