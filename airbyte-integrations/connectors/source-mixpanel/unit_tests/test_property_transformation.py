#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""
Test case, when custom Export, ExportSchema properties contains names,
that will conflict in further data normalization, like:
`userName` and `username`
"""

from unittest.mock import MagicMock

import pytest
from source_mixpanel.streams import Export

from airbyte_cdk.models import SyncMode

from .utils import get_url_to_mock, setup_response


@pytest.fixture
def export_response():
    return setup_response(
        200,
        {
            "event": "Problem event",
            "properties": {
                "distinct_id": "1d694fd9-31a5-4b99-9eef-ae63112063ed",
                "$userName": "1",
                "userName": "2",
                "username": "3",
                "time": 1485302410,
            },
        },
    )


def test_export_stream_conflict_names(requests_mock, export_response, config):
    stream = Export(authenticator=MagicMock(), **config)
    # Remove requests limit for test
    stream.reqs_per_hour_limit = 0
    requests_mock.register_uri("GET", get_url_to_mock(stream), export_response)

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)
    records = [record for record in records]
    assert len(records) == 1
    record = records[0]

    assert sorted(record.keys()) == sorted(
        [
            "event",
            "distinct_id",
            "userName",
            "_userName",
            "__username",
            "time",
        ]
    )
    assert record["userName"] == "1"
    assert record["_userName"] == "2"
    assert record["__username"] == "3"
