#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.file_based.config.csv_format import CsvFormat
from pydantic import ValidationError


@pytest.mark.parametrize(
    "skip_rows_before_header, autogenerate_column_names, expected_error",
    [
        pytest.param(1, True, ValidationError, id="test_skip_rows_before_header_and_autogenerate_column_names"),
        pytest.param(1, False, ValidationError, id="test_skip_rows_before_header_and_no_autogenerate_column_names"),
        pytest.param(0, True, ValidationError, id="test_no_skip_rows_before_header_and_autogenerate_column_names"),
        pytest.param(0, False, ValidationError, id="test_no_skip_rows_before_header_and_no_autogenerate_column_names"),
    ]
)
def test_csv_format(skip_rows_before_header, autogenerate_column_names, expected_error):
    if expected_error:
        with pytest.raises(ValidationError):
            CsvFormat(skip_rows_before_header=1, autogenerate_column_names=True)
    else:
        CsvFormat(skip_rows_before_header=1, autogenerate_column_names=True)
