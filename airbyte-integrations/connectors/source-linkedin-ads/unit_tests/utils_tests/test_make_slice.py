#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_linkedin_ads.utils import get_parent_stream_values


@pytest.mark.parametrize(
    "record, key_value_map, output_slice",
    [
        ({"id": 123, "ref": "abc"}, {"acc_id": "id"}, {"acc_id": 123}),
        ({"id": 123, "ref": "abc"}, {"acc_id": "id", "ref_id": "ref"}, {"acc_id": 123, "ref_id": "abc"}),
    ],
)
def test_get_parent_stream_values(record, key_value_map, output_slice):
    assert get_parent_stream_values(record, key_value_map) == output_slice
