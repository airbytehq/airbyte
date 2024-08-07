#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import datetime
from io import BytesIO
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import ExcelFormat, FileBasedStreamConfig, ValidationPolicy
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, RecordParseError
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader, FileReadMode
from airbyte_cdk.sources.file_based.file_types.excel_parser import ExcelParser
from airbyte_cdk.sources.file_based.remote_file import RemoteFile


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
        validation_policy=ValidationPolicy.emit_record
    )


@pytest.fixture
def remote_file():
    return RemoteFile(uri="s3://mybucket/test.xlsx", last_modified=datetime.datetime.now())


@pytest.fixture
def sample_excel_data():
    data = {
        'A': [1, 2, 3],
        'B': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'C': [True, False, True]
    }
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        return buffer.getvalue()


@pytest.mark.asyncio
async def test_infer_schema(mock_stream_reader, mock_logger, file_config, remote_file, sample_excel_data):
    parser = ExcelParser()
    with patch("builtins.open", mock_open(read_data=sample_excel_data)):
        with patch("pandas.ExcelFile") as mock_excel:
            mock_excel.return_value.parse.return_value = pd.read_excel(BytesIO(sample_excel_data))

            schema = await parser.infer_schema(file_config, remote_file, mock_stream_reader, mock_logger)

    expected_schema = {
        'A': {"type": "number"},
        'B': {"type": "string"},
        'C': {"type": "boolean"}
    }

    assert schema == expected_schema


def test_invalid_format(mock_stream_reader, mock_logger, remote_file):
    parser = ExcelParser()
    invalid_config = FileBasedStreamConfig(
        name="test.xlsx",
        file_type="csv",
        format={"filetype": "csv"},
        validation_policy=ValidationPolicy.emit_record
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
