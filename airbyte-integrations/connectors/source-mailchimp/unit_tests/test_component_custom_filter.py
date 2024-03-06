#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.sources.declarative.types import StreamSlice
from source_mailchimp.components import MailChimpRecordFilter


@pytest.mark.parametrize(
    ["config", "stream_state", "len_expected_records"],
    [
        [
            {"start_date": "2020-02-16T17:30:00.000Z"},
            {
                "states": [
                    {
                        "partition": {
                            "id": "7847cdaeff",
                            "parent_slice": {"end_time": "2023-01-07T12:50:16.411612Z", "start_time": "2022-12-07T12:50:17.411612Z"},
                        },
                        "cursor": {"timestamp": "2024-02-19T12:50:18+0000"},
                    }
                ]
            },
            0,
        ],
        [{"start_date": "2020-02-16T17:30:00.000Z"}, {}, 2],
        [{}, {}, 2],
        [
            {},
            {
                "states": [
                    {
                        "partition": {
                            "id": "7847cdaeff",
                            "parent_slice": {"end_time": "2023-01-07T12:50:16.411612Z", "start_time": "2022-12-07T12:50:17.411612Z"},
                        },
                        "cursor": {"timestamp": "2021-02-19T12:50:18+0000"},
                    }
                ]
            },
            1,
        ],
    ],
    ids=[
        "start_date_and_stream_state",
        "start_date_and_NO_stream_state",
        "NO_start_date_and_NO_stream_state",
        "NO_start_date_and_stream_state",
    ],
)
def test_mailchimp_custom_filter(config: dict, stream_state: dict, len_expected_records: int):
    stream_slice = StreamSlice(
        partition={"id": "7847cdaeff"}, cursor_slice={"end_time": "2024-02-19T13:33:56+0000", "start_time": "2022-10-07T13:33:56+0000"}
    )
    parameters = {
        "name": "segment_members",
        "cursor_field": "timestamp",
    }
    record_filter = MailChimpRecordFilter(config=config, condition="", parameters=parameters)

    records = [
        {
            "id": "1dd067951f91190b65b43305b9166bc7",
            "timestamp": "2020-12-27T08:34:39+00:00",
            "campaign_id": "7847cdaeff",
            "segment_id": 13506120,
        },
        {
            "id": "1dd067951f91190b65b43305b9166bc7",
            "timestamp": "2022-12-27T08:34:39+00:00",
            "campaign_id": "7847cdaeff",
            "segment_id": 13506120,
        },
    ]

    actual_records = record_filter.filter_records(records, stream_state=stream_state, stream_slice=stream_slice)
    assert len(actual_records) == len_expected_records
