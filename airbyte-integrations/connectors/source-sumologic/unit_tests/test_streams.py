#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_sumologic.client import Client
from source_sumologic.source import SumologicStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(SumologicStream, "__abstractmethods__", set())


def test_init(patch_base_class):
    client = Client(access_id="foo", access_key="bar")
    config = MagicMock()
    stream = SumologicStream(client, config)
    assert stream.primary_key == "_messageid"
    assert stream.client == client
    assert stream.config == config
