#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import datetime
from io import BytesIO
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd
import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import ExcelFormat, FileBasedStreamConfig, ValidationPolicy
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.excel_parser import ExcelParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from airbyte_cdk.sources.file_based.schema_helpers import SchemaType


@pytest.fixture
def mock_stream_reader():
    return Mock(spec=AbstractFileBasedStreamReader)


@pytest.fixture
def mock_logger():
    return Mock()


@pytest.fixture
def file_config():
    return FileBasedStreamConfig(
        name="test.xlsx",
        file_type="excel",
        format=ExcelFormat(sheet_name="Sheet1"),
        validation_policy=ValidationPolicy.emit_record,
    )


@pytest.fixture
def remote_file():
    return RemoteFile(uri="s3://mybucket/test.xlsx", last_modified=datetime.datetime.now())


@pytest.fixture
def setup_parser(remote_file):
    parser = ExcelParser()

    # Sample data for the mock Excel file
    data = pd.DataFrame(
        {
            "column1": [1, 2, 3],
            "column2": ["a", "b", "c"],
            "column3": [True, False, True],
            "column4": pd.to_datetime(["2021-01-01", "2022-01-01", "2023-01-01"]),
        }
    )

    # Convert the DataFrame to an Excel byte stream
    excel_bytes = BytesIO()
    with pd.ExcelWriter(excel_bytes, engine="xlsxwriter") as writer:
        data.to_excel(writer, index=False)
    excel_bytes.seek(0)

    # Mock the stream_reader's open_file method to return the Excel byte stream
    stream_reader = MagicMock(spec=AbstractFileBasedStreamReader)
    stream_reader.open_file.return_value = BytesIO(excel_bytes.read())

    return parser, FileBasedStreamConfig(name="test_stream", format=ExcelFormat()), remote_file, stream_reader, MagicMock(), data


@patch("pandas.ExcelFile")
@pytest.mark.asyncio
async def test_infer_schema(mock_excel_file, setup_parser):
    parser, config, file, stream_reader, logger, data = setup_parser

    # Mock the parse method of the pandas ExcelFile object
    mock_excel_file.return_value.parse.return_value = data

    # Call infer_schema
    schema = await parser.infer_schema(config, file, stream_reader, logger)

    # Define the expected schema
    expected_schema: SchemaType = {
        "column1": {"type": "number"},
        "column2": {"type": "string"},
        "column3": {"type": "boolean"},
        "column4": {"type": "string", "format": "date-time"},
    }

    # Validate the schema
    assert schema == expected_schema

    # Assert that the stream_reader's open_file was called correctly
    stream_reader.open_file.assert_called_once_with(file, parser.file_read_mode, parser.ENCODING, logger)

    # Assert that the logger was not used for warnings/errors
    logger.info.assert_not_called()
    logger.error.assert_not_called()


def test_invalid_format(mock_stream_reader, mock_logger, remote_file):
    parser = ExcelParser()
    invalid_config = FileBasedStreamConfig(
        name="test.xlsx",
        file_type="csv",
        format={"filetype": "csv"},
        validation_policy=ValidationPolicy.emit_record,
    )

    with pytest.raises(ConfigValidationError):
        list(parser.parse_records(invalid_config, remote_file, mock_stream_reader, mock_logger))


def test_file_read_error(mock_stream_reader, mock_logger, file_config, remote_file):
    parser = ExcelParser()
    with patch("builtins.open", mock_open(read_data=b"corrupted data")):
        with patch("pandas.ExcelFile") as mock_excel:
            mock_excel.return_value.parse.side_effect = ValueError("Failed to parse file")

            with pytest.raises(RecordParseError):
                list(parser.parse_records(file_config, remote_file, mock_stream_reader, mock_logger))
