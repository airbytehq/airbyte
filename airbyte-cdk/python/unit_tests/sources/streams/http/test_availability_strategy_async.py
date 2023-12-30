#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import asyncio
import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import aiohttp
import pytest
from aioresponses import aioresponses
from airbyte_cdk.sources.abstract_source_async import AsyncAbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy_async import AsyncHttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.http_async import AsyncHttpStream

logger = logging.getLogger("airbyte")


class MockHttpStream(AsyncHttpStream):
    url_base = "https://test_base_url.com"
    primary_key = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resp_counter = 1

    async def next_page_token(self, response: aiohttp.ClientResponse) -> Optional[Mapping[str, Any]]:
        return None

    def path(self, **kwargs) -> str:
        return ""

    async def parse_response(self, response: aiohttp.ClientResponse, **kwargs) -> Iterable[Mapping]:
        stub_resp = {"data": self.resp_counter}
        self.resp_counter += 1
        yield stub_resp

    def retry_factor(self) -> float:
        return 0.01


@pytest.mark.parametrize(
    ("status_code", "expected_is_available", "expected_messages"),
    [
        (
            403,
            False,
            [
                "This is most likely due to insufficient permissions on the credentials in use.",
            ],
        ),
        (200, True, []),
    ],
)
@pytest.mark.parametrize(
    ("include_source", "expected_docs_url_messages"),
    [
        (True, ["Please visit https://docs.airbyte.com/integrations/sources/MockSource to learn more."]),
        (False, ["Please visit the connector's documentation to learn more."]),
    ],
)
def test_default_http_availability_strategy(
    status_code,
    expected_is_available,
    expected_messages,
    include_source,
    expected_docs_url_messages,
):
    class MockListHttpStream(MockHttpStream):
        async def read_records(self, *args, **kvargs):
            async for record in super().read_records(*args, **kvargs):
                yield record

    http_stream = MockListHttpStream()
    assert isinstance(http_stream.availability_strategy, AsyncHttpAvailabilityStrategy)

    class MockSource(AsyncAbstractSource):
        def __init__(self, streams: List[Stream] = None):
            self._streams = streams
            super().__init__()

        async def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
            return True, ""

        def streams(self, config: Mapping[str, Any]) -> List[Stream]:
            if not self._streams:
                raise Exception("Stream is not set")
            return self._streams

    loop = asyncio.get_event_loop()
    loop.run_until_complete(http_stream.ensure_session())

    with aioresponses() as m:
        m.get(http_stream.url_base, status=status_code)

        if include_source:
            source = MockSource(streams=[http_stream])
            actual_is_available, reason = loop.run_until_complete(http_stream.check_availability(logger, source))
        else:
            actual_is_available, reason = loop.run_until_complete(http_stream.check_availability(logger))

        assert expected_is_available == actual_is_available
        if expected_is_available:
            assert reason is None
        else:
            all_expected_messages = expected_messages + expected_docs_url_messages
            for message in all_expected_messages:
                assert message in reason

    loop.run_until_complete(http_stream._session.close())


def test_http_availability_raises_unhandled_error(mocker):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, AsyncHttpAvailabilityStrategy)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(http_stream.ensure_session())

    with aioresponses() as m:
        m.get(http_stream.url_base, status=404)

        with pytest.raises(aiohttp.ClientResponseError):
            loop.run_until_complete(http_stream.check_availability(logger))


def test_send_handles_retries_when_checking_availability(caplog):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, AsyncHttpAvailabilityStrategy)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(http_stream.ensure_session())

    call_counter = 0

    def request_callback(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

    with aioresponses() as m:
        m.get(http_stream.url_base, status=429, callback=request_callback)
        m.get(http_stream.url_base, status=503, callback=request_callback)
        m.get(http_stream.url_base, status=200, callback=request_callback)

        with caplog.at_level(logging.INFO):
            stream_is_available, _ = loop.run_until_complete(http_stream.check_availability(logger))

    assert stream_is_available
    assert call_counter == 3
    for message in ["Caught retryable error", "Response Code: 429", "Response Code: 503"]:
        assert message in caplog.text


def test_http_availability_strategy_on_empty_stream(mocker):
    empty_stream_called = False
    async def empty_aiter(*args, **kwargs):
        nonlocal empty_stream_called
        empty_stream_called = True
        yield

    class MockEmptyHttpStream(mocker.MagicMock, MockHttpStream):
        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            self.read_records = empty_aiter

    empty_stream = MockEmptyHttpStream()
    assert isinstance(empty_stream, AsyncHttpStream)
    assert isinstance(empty_stream.availability_strategy, AsyncHttpAvailabilityStrategy)

    logger = logging.getLogger("airbyte.test-source")
    loop = asyncio.get_event_loop()
    stream_is_available, _ = loop.run_until_complete(empty_stream.check_availability(logger))

    assert stream_is_available
    assert empty_stream_called
