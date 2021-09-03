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
from typing import Any, Mapping, MutableMapping, Iterator, List, Type

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

    def sync_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)
        return [
            Campaigns(api=api, start_date=config.start_date, include_deleted=config.include_deleted),
            AdSets(api=api, start_date=config.start_date, include_deleted=config.include_deleted),
        ]

    def async_streams(self, config: Mapping[str, Any]):
        return [(), DummyAsyncStream()]

    def streams(self, config):
        return [*self.sync_streams(config), *self.async_streams(config)]

    def read_async(
            self, logger: AirbyteLogger, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog,
            state: MutableMapping[str, Any] = None
    ) -> Iterator[AirbyteMessage]:
        """Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification."""
        connector_state = copy.deepcopy(state or {})
        logger.info(f"Starting syncing {self.name}")
        configured_names = {configured_stream.stream.name for configured_stream in catalog.streams}
        stream_instances = {s.name: s for s in self.async_streams(config) if s.name in configured_names}
        iterators = [self._async_stream_iterator(stream, connector_state) for stream in stream_instances]
        yield from iter_over_async(self._read_async_stream_simultaneously(iterators), asyncio.get_event_loop())

    @staticmethod
    async def _read_async_stream_simultaneously(iterators):
        """ Read records from all streams"""
        async for record in aio_stream.merge(iterators):
            yield record

    @staticmethod
    async def _async_stream_iterator(stream, state) -> Iterator:
        """ Iterator over stream slices"""
        async for job in stream.map(stream.stream_slices(), stream.create_and_wait, task_limit=stream.task_limit, ordered=True):
            async for record in stream.read_records(job):
                yield record
