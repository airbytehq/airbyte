#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from samples.test_data_for_analytics import test_input_result_record_chunks, test_output_merged_chunks
from source_linkedin_ads.analytics import merge_chunks

TEST_MERGE_BY_KEY = "end_date"


def test_merge_chunks():
    """`merge_chunks` is the generator object, to get the output the list() function is applied"""
    assert list(merge_chunks(test_input_result_record_chunks, TEST_MERGE_BY_KEY)) == test_output_merged_chunks
