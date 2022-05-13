#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

from airbyte_cdk.sources.cac.checks.check_stream import CheckStream

logger = None
config = dict()


def test_check_stream():
    record = MagicMock()
    stream = MagicMock()
    stream.read_records.return_value = iter([record])

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(source)

    connected, error = check_stream.check_connection(logger, config)
    assert connected
    assert error is None


def test_check_stream_no_records():
    stream = MagicMock()
    stream.read_records.return_value = iter([])

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(source)

    connected, error = check_stream.check_connection(logger, config)
    assert not connected
    assert error is not None
