#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from samples.test_data_for_tranform import input_test_data, output_test_data
from source_linkedin_ads.utils import transform_data


def test_transfrom_data():
    """
    As far as we transform the data within the generator object,
    we use list() to have the actual output for the test assertion.
    """
    assert list(transform_data(input_test_data)) == output_test_data
