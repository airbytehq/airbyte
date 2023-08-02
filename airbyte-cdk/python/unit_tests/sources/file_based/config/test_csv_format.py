#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat


@pytest.mark.parametrize(
    "skip_rows_before_header, autogenerate_column_names, expected_error",
    [
        pytest.param(1, True, ValueError, id="test_skip_rows_before_header_and_autogenerate_column_names"),
        pytest.param(1, False, None, id="test_skip_rows_before_header_and_no_autogenerate_column_names"),
        pytest.param(0, True, None, id="test_no_skip_rows_before_header_and_autogenerate_column_names"),
        pytest.param(0, False, None, id="test_no_skip_rows_before_header_and_no_autogenerate_column_names"),
    ]
)
def test_csv_format(skip_rows_before_header, autogenerate_column_names, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            CsvFormat(skip_rows_before_header=skip_rows_before_header, autogenerate_column_names=autogenerate_column_names)
    else:
        CsvFormat(skip_rows_before_header=skip_rows_before_header, autogenerate_column_names=autogenerate_column_names)
