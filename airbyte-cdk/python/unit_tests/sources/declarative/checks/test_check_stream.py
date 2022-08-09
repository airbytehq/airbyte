#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.checks.check_stream import CheckStream

logger = None
config = dict()

stream_names = ["s1"]
record = MagicMock()


@pytest.mark.parametrize(
    "test_name, record, streams_to_check, expectation",
    [
        ("test success check", record, stream_names, (True, None)),
        ("test fail check", None, stream_names, (True, None)),
        ("test try to check invalid stream", record, ["invalid_stream_name"], None),
    ],
)
def test_check_stream(test_name, record, streams_to_check, expectation):
    stream = MagicMock()
    stream.name = "s1"
    stream.read_records.return_value = iter([record])

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(streams_to_check, options={})

    if expectation:
        actual = check_stream.check_connection(source, logger, config)
        assert actual == expectation
    else:
        with pytest.raises(ValueError):
            check_stream.check_connection(source, logger, config)
