#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from components import PINTEREST_STATUS_CHUNK_SIZE, StatusChunkPartitionRouter


@pytest.mark.parametrize(
    "values,expected",
    [
        pytest.param(None, [None], id="none_returns_single_none"),
        pytest.param([], [None], id="empty_returns_single_none"),
        pytest.param(
            ["RUNNING", "PAUSED"],
            [["RUNNING", "PAUSED"]],
            id="under_limit_single_chunk",
        ),
        pytest.param(
            ["A", "B", "C", "D", "E", "F"],
            [["A", "B", "C", "D", "E", "F"]],
            id="exactly_at_limit",
        ),
        pytest.param(
            ["A", "B", "C", "D", "E", "F", "G"],
            [["A", "B", "C", "D", "E", "F"], ["G"]],
            id="one_over_limit",
        ),
        pytest.param(
            ["A", "B", "C", "D", "E", "F", "G", "H"],
            [["A", "B", "C", "D", "E", "F"], ["G", "H"]],
            id="eight_values_two_chunks",
        ),
        pytest.param(
            list("ABCDEFGHIJKLM"),
            [list("ABCDEF"), list("GHIJKL"), ["M"]],
            id="thirteen_values_three_chunks",
        ),
    ],
)
def test_chunk(values, expected):
    assert StatusChunkPartitionRouter._chunk(values) == expected


@pytest.mark.parametrize(
    "campaign_statuses,ad_group_statuses,ad_statuses,expected_partitions",
    [
        pytest.param(
            None,
            None,
            None,
            [{}],
            id="no_statuses_yields_empty_partition",
        ),
        pytest.param(
            ["RUNNING", "PAUSED"],
            None,
            None,
            [{"campaign_statuses_chunk": ["RUNNING", "PAUSED"]}],
            id="single_field_under_limit",
        ),
        pytest.param(
            ["A", "B", "C", "D", "E", "F", "G", "H"],
            None,
            None,
            [
                {"campaign_statuses_chunk": ["A", "B", "C", "D", "E", "F"]},
                {"campaign_statuses_chunk": ["G", "H"]},
            ],
            id="single_field_over_limit_two_slices",
        ),
        pytest.param(
            ["RUNNING", "PAUSED"],
            ["ARCHIVED"],
            None,
            [
                {
                    "campaign_statuses_chunk": ["RUNNING", "PAUSED"],
                    "ad_group_statuses_chunk": ["ARCHIVED"],
                },
            ],
            id="two_fields_under_limit",
        ),
        pytest.param(
            ["A", "B", "C", "D", "E", "F", "G"],
            ["X", "Y", "Z", "W", "V", "U", "T"],
            None,
            [
                {
                    "campaign_statuses_chunk": ["A", "B", "C", "D", "E", "F"],
                    "ad_group_statuses_chunk": ["X", "Y", "Z", "W", "V", "U"],
                },
                {
                    "campaign_statuses_chunk": ["A", "B", "C", "D", "E", "F"],
                    "ad_group_statuses_chunk": ["T"],
                },
                {
                    "campaign_statuses_chunk": ["G"],
                    "ad_group_statuses_chunk": ["X", "Y", "Z", "W", "V", "U"],
                },
                {
                    "campaign_statuses_chunk": ["G"],
                    "ad_group_statuses_chunk": ["T"],
                },
            ],
            id="two_fields_over_limit_cartesian_product",
        ),
        pytest.param(
            ["A", "B", "C", "D", "E", "F", "G", "H"],
            ["X", "Y", "Z", "W", "V", "U", "T", "S"],
            ["P", "Q", "R", "S2", "S3", "S4", "S5", "S6"],
            # 2 campaign chunks × 2 ad_group chunks × 2 ad chunks = 8 slices
            None,  # checked via count below
            id="all_three_fields_over_limit_eight_combos",
        ),
    ],
)
def test_stream_slices(campaign_statuses, ad_group_statuses, ad_statuses, expected_partitions):
    router = StatusChunkPartitionRouter(
        config={},
        parameters={},
        campaign_statuses=campaign_statuses,
        ad_group_statuses=ad_group_statuses,
        ad_statuses=ad_statuses,
    )
    slices = list(router.stream_slices())
    partitions = [dict(s.partition) for s in slices]

    if expected_partitions is None:
        # For the 8-combo case, just verify the count and that every chunk ≤6
        assert len(partitions) == 8
        for p in partitions:
            for key, val in p.items():
                assert len(val) <= PINTEREST_STATUS_CHUNK_SIZE
    else:
        assert partitions == expected_partitions


def test_stream_slices_chunks_never_exceed_limit():
    """All emitted chunks respect the Pinterest per-request limit."""
    router = StatusChunkPartitionRouter(
        config={},
        parameters={},
        campaign_statuses=list("ABCDEFGHIJKLM"),  # 13 values → 3 chunks
        ad_group_statuses=list("NOPQRSTUVWXYZ"),  # 13 values → 3 chunks
        ad_statuses=list("abcdefgh"),  # 8 values → 2 chunks
    )
    slices = list(router.stream_slices())
    assert len(slices) == 3 * 3 * 2  # 18 combinations
    for s in slices:
        for key, val in s.partition.items():
            assert len(val) <= PINTEREST_STATUS_CHUNK_SIZE
