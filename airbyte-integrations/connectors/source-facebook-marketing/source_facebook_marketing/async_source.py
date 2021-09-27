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

import asyncio

from aiostream import stream as aio_stream
import copy
from typing import Any, Mapping, MutableMapping, Iterator, List

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
)

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_facebook_marketing.streams import Campaigns, AdSets
from source_facebook_marketing.source import ConnectorConfig
from source_facebook_marketing.api import API
from source_facebook_marketing.async_streams import AdsInsights, AdsInsightsAgeAndGender
from source_facebook_marketing.async_stream import AsyncStream


def iter_over_async(async_iterator, loop) -> Iterator:
    """ Async generator -> Sync generator"""
    ait = async_iterator.__aiter__()

    async def get_next():
        try:
            obj = await ait.__anext__()
            return False, obj
        except StopAsyncIteration:
            return True, None

    while True:
        done, obj = loop.run_until_complete(get_next())
        if done:
            break
        yield obj


class AsyncSource(AbstractSource):
    """ Async Source, supports Sync & Async streams
    """
    def read(
            self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog,
            state: MutableMapping[str, Any] = None
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification."""
        all_streams = self.streams(config)
        sync_streams = [stream for stream in all_streams if not isinstance(stream, AsyncStream)]
        async_streams = [stream for stream in all_streams if isinstance(stream, AsyncStream)]
        yield from super().read(logger=logger, config=config, catalog=catalog, state=state)

        connector_state = copy.deepcopy(state or {})
        logger.info(f"Starting syncing {self.name}")
        configured_names = {configured_stream.stream.name for configured_stream in catalog.streams}
        stream_instances = {s.name: s for s in async_streams if s.name in configured_names}

        for stream in stream_instances:
            yield from iter_over_async(self._async_stream_iterator(stream, connector_state), asyncio.get_event_loop())

    @staticmethod
    async def _async_stream_iterator(stream, state) -> Iterator:
        """ Iterator over stream slices"""
        async for job in aio_stream.map(stream.stream_slices(), stream.create_and_wait, task_limit=stream.task_limit, ordered=True):
            async for record in stream.read_records(job):
                yield record


class FBSource(AsyncSource):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)

        instances = [
            cls(api=api, start_date=config.start_date, include_deleted=config.include_deleted,)
            for cls in (Campaigns, AdSets)
        ]
        instances += [
            cls(
                api=api,
                start_date=config.start_date,
                buffer_days=config.insights_lookback_window,
                days_per_job=config.insights_days_per_job,
            )
            for cls in (AdsInsightsAgeAndGender, AdsInsights)
        ]

        # TODO: sort by name?

        return instances
