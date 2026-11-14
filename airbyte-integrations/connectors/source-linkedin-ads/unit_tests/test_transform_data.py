#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest

from .samples.test_data_for_tranform import input_test_data, output_test_data


def test_transform_data(components_module):
    """
    As far as we transform the data within the generator object,
    we use list() to have the actual output for the test assertion.
    """
    transform_data = components_module.transform_data
    assert list(transform_data(input_test_data)) == output_test_data


@pytest.mark.parametrize(
    "transform_campaign_statistics_pivots,expected_record",
    [
        pytest.param(
            False,
            {
                "pivotValues": ["urn:li:sponsoredCampaign:1001", "CONNECTED_TV"],
                "string_of_pivot_values": "urn:li:sponsoredCampaign:1001,CONNECTED_TV",
            },
            id="shared_extractor_preserves_campaign_pivot",
        ),
        pytest.param(
            True,
            {
                "pivotValues": ["CONNECTED_TV"],
                "string_of_pivot_values": "CONNECTED_TV",
                "sponsoredCampaign": "1001",
            },
            id="impression_device_extractor_moves_campaign_pivot",
        ),
    ],
)
def test_transform_data_campaign_statistics_pivots(components_module, transform_campaign_statistics_pivots, expected_record):
    records = [{"pivotValues": ["urn:li:sponsoredCampaign:1001", "CONNECTED_TV"]}]

    assert list(
        components_module.transform_data(
            records,
            transform_campaign_statistics_pivots=transform_campaign_statistics_pivots,
        )
    ) == [expected_record]
