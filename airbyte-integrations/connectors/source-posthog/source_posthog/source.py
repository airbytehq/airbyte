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


from typing import Any, Iterator, List, Mapping, MutableMapping, Tuple

import dateutil.parser
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteStream, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from .streams import (  # EventsSessions,
    Annotations,
    Cohorts,
    Elements,
    Events,
    FeatureFlags,
    Insights,
    InsightsPath,
    InsightsSessions,
    Persons,
    Trends,
)


class SourcePosthog(AbstractSource):
    def _read_incremental(
        self,
        logger: AirbyteLogger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
    ) -> Iterator[AirbyteMessage]:
        """
        overridden: accept stream_state both dict and tuple
        if Tuple:
            second element is dict state
            first element- any - says to break a loop
            Reason: descendant reading records, break on cursor_val <= state
            Alternative: filter whole responce by cursor_field, not that great.
        """
        stream_name = configured_stream.stream.name
        stream_state = connector_state.get(stream_name, {})
        if stream_state:
            logger.info(f"Setting state of {stream_name} stream to {stream_state.get(stream_name)}")

        checkpoint_interval = stream_instance.state_checkpoint_interval
        slices = stream_instance.stream_slices(
            cursor_field=configured_stream.cursor_field, sync_mode=SyncMode.incremental, stream_state=stream_state
        )
        for slice_ in slices:
            record_counter = 0
            records = stream_instance.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=slice_,
                stream_state=stream_state,
                cursor_field=configured_stream.cursor_field or None,
            )
            for record_data in records:
                stream_state = stream_instance.get_updated_state(stream_state, record_data)
                if isinstance(stream_state, tuple):
                    stream_state = stream_state[1]
                    break
                record_counter += 1
                yield self._as_airbyte_record(stream_name, record_data)

                if checkpoint_interval and record_counter % checkpoint_interval == 0:
                    yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)

            yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            _ = dateutil.parser.isoparse(config["start_date"])
            authenticator = TokenAuthenticator(token=config["api_key"])
            _ = next(Annotations(authenticator=authenticator).read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        event/sessions stream is dynamic. Probably, it contains a list of CURRENT sessions.
        In Next day session may expire and wont be available via this endpoint.
        So we need a dynamic load data before tests.
        This stream was requested to be removed due to this reason.
        """
        authenticator = TokenAuthenticator(token=config["api_key"])
        return [
            Annotations(authenticator=authenticator),
            Cohorts(authenticator=authenticator),
            Elements(authenticator=authenticator),
            Events(start_date=config["start_date"], authenticator=authenticator),
            # EventsSessions(authenticator=authenticator),
            FeatureFlags(authenticator=authenticator),
            Insights(authenticator=authenticator),
            InsightsPath(authenticator=authenticator),
            InsightsSessions(authenticator=authenticator),
            Persons(authenticator=authenticator),
            Trends(authenticator=authenticator),
        ]
