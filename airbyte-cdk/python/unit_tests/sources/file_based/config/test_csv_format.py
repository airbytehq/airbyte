#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from typing import Type
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
def test_csv_format_skip_rows_and_autogenerate_column_names(skip_rows_before_header, autogenerate_column_names, expected_error) -> None:
    if expected_error:
        with pytest.raises(expected_error):
            CsvFormat(skip_rows_before_header=skip_rows_before_header, autogenerate_column_names=autogenerate_column_names)
    else:
        CsvFormat(skip_rows_before_header=skip_rows_before_header, autogenerate_column_names=autogenerate_column_names)


@pytest.mark.parametrize(
    "infer_datatypes, infer_datatypes_legacy, expected_error",
    [
        pytest.param(True, True, ValueError, id="test_many_inferences_configured"),
        pytest.param(True, False, None, id="test_infer_datatypes"),
        pytest.param(False, True, None, id="test_infer_datatypes_legacy"),
        pytest.param(False, False, None, id="test_no_inference"),
    ]
)
def test_csv_format_inference(infer_datatypes: bool, infer_datatypes_legacy: bool, expected_error: Type[BaseException]) -> None:
    if expected_error:
        with pytest.raises(expected_error):
            CsvFormat(infer_datatypes=infer_datatypes, infer_datatypes_legacy=infer_datatypes_legacy)
    else:
        CsvFormat(infer_datatypes=infer_datatypes, infer_datatypes_legacy=infer_datatypes_legacy)
