#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Type

import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import AvroFormat, CsvFormat, ParquetFormat
from jsonschema import ValidationError, validate
from pydantic.v1 import BaseModel


@pytest.mark.parametrize(
    "file_format, file_type, expected_error",
    [
        pytest.param(ParquetFormat, "parquet", None, id="test_parquet_format_is_a_valid_parquet_file_type"),
        pytest.param(AvroFormat, "avro", None, id="test_avro_format_is_a_valid_avro_file_type"),
        pytest.param(CsvFormat, "parquet", ValidationError, id="test_csv_format_is_not_a_valid_parquet_file_type"),
    ],
)
def test_parquet_file_type_is_not_a_valid_csv_file_type(file_format: BaseModel, file_type: str, expected_error: Type[Exception]) -> None:
    format_config = {file_type: {"filetype": file_type, "decimal_as_float": True}}

    if expected_error:
        with pytest.raises(expected_error):
            validate(instance=format_config[file_type], schema=file_format.schema())
    else:
        validate(instance=format_config[file_type], schema=file_format.schema())
