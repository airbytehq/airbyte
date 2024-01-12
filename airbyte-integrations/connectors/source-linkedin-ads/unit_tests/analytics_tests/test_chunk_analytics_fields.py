#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_linkedin_ads.analytics_streams import LinkedInAdsAnalyticsStream

# Test chunk size for each field set
TEST_FIELDS_CHUNK_SIZE = 3
# Test fields assuming they are really available for the fetch
TEST_ANALYTICS_FIELDS = [
    "field_1",
    "base_field_1",
    "field_2",
    "base_field_2",
    "field_3",
    "field_4",
    "field_5",
    "field_6",
    "field_7",
    "field_8",
]


def test_chunk_analytics_fields():
    """
    We expect to truncate the field list into the chunks of equal size,
    with "dateRange" field presented in each chunk.
    """
    expected_output = [
        ["field_1", "base_field_1", "field_2", "dateRange"],
        ["base_field_2", "field_3", "field_4", "dateRange"],
        ["field_5", "field_6", "field_7", "dateRange"],
        ["field_8", "dateRange"]
    ]

    assert list(LinkedInAdsAnalyticsStream.chunk_analytics_fields(TEST_ANALYTICS_FIELDS,
                                                                  TEST_FIELDS_CHUNK_SIZE)) == expected_output
