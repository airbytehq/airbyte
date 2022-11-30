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
    "test_name, record, streams_to_check, stream_slice, expectation",
    [
        ("test_success_check", record, stream_names, {}, (True, None)),
        ("test_success_check_stream_slice", record, stream_names, {"slice": "slice_value"}, (True, None)),
        ("test_fail_check", None, stream_names, {}, (True, None)),
        ("test_try_to_check_invalid stream", record, ["invalid_stream_name"], {}, None),
    ],
)
@pytest.mark.parametrize("slices_as_list", [True, False])
def test_check_stream_with_slices_as_list(test_name, record, streams_to_check, stream_slice, expectation, slices_as_list):
    stream = MagicMock()
    stream.name = "s1"
    if slices_as_list:
        stream.stream_slices.return_value = [stream_slice]
    else:
        stream.stream_slices.return_value = iter([stream_slice])

    stream.read_records.side_effect = mock_read_records({frozenset(stream_slice): iter([record])})

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(streams_to_check, options={})

    if expectation:
        actual = check_stream.check_connection(source, logger, config)
        assert actual == expectation
    else:
        with pytest.raises(ValueError):
            check_stream.check_connection(source, logger, config)


def mock_read_records(responses, default_response=None, **kwargs):
    return lambda stream_slice, sync_mode: responses[frozenset(stream_slice)] if frozenset(stream_slice) in responses else default_response
