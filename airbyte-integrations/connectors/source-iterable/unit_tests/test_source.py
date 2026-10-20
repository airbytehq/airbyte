#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from source_iterable.source import SourceIterable
from source_iterable.streams import IterableStream


@responses.activate
@pytest.mark.parametrize("body, status, expected_streams", [(b"alpha@gmail.com\nbeta@gmail.com", 200, 44)])
def test_source_streams(config, body, status, expected_streams):
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})
    responses.add(responses.GET, "https://api.iterable.com/api/lists/getUsers?listId=1", body=body, status=status)

    streams = SourceIterable().streams(config=config)

    assert len(streams) == expected_streams


@responses.activate
@pytest.mark.parametrize(
    "region, expected_url_base",
    [
        pytest.param("US", "https://api.iterable.com/api/", id="us_region"),
        pytest.param("EU", "https://api.eu.iterable.com/api/", id="eu_region"),
    ],
)
def test_source_streams_region_propagation(config, region, expected_url_base):
    responses.get(expected_url_base + "lists", json={"lists": [{"id": 1}]})
    responses.add(responses.GET, expected_url_base + "lists/getUsers?listId=1", body=b"user@example.com", status=200)

    config_with_region = {**config, "region": region}
    streams = SourceIterable().streams(config=config_with_region)

    python_streams = [s for s in streams if isinstance(s, IterableStream)]
    assert len(python_streams) > 0
    for stream in python_streams:
        assert stream.url_base == expected_url_base, f"{stream.name} has url_base={stream.url_base}, expected {expected_url_base}"


@responses.activate
def test_source_check_connection_failed(config):
    responses.get("https://api.iterable.com/api/lists", json={}, status=401)

    assert SourceIterable().check_connection(MagicMock(), config=config)[0] is False


@responses.activate
def test_source_check_connection_ok(config):
    responses.get("https://api.iterable.com/api/lists", json={"lists": [{"id": 1}]})

    assert SourceIterable().check_connection(MagicMock(), config=config) == (True, None)
