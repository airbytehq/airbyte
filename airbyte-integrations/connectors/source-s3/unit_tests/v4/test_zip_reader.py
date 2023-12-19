# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import datetime
import io
import struct
import zipfile
from unittest.mock import MagicMock, patch

import pytest
from source_s3.v4.zip_reader import DecompressedStream, RemoteFileInsideArchive, ZipContentReader, ZipFileHandler


# Mocking the S3 client and config for testing
@pytest.fixture
def mock_s3_client():
    return MagicMock()


@pytest.fixture
def mock_config():
    return MagicMock(bucket="test-bucket")


@pytest.fixture
def zip_file_handler(mock_s3_client, mock_config):
    return ZipFileHandler(mock_s3_client, mock_config)


def test_fetch_data_from_s3(zip_file_handler):
    zip_file_handler._fetch_data_from_s3("test_file", 0, 10)
    zip_file_handler.s3_client.get_object.assert_called_with(Bucket="test-bucket", Key="test_file", Range="bytes=0-9")


def test_find_signature(zip_file_handler):
    zip_file_handler.s3_client.head_object.return_value = {"ContentLength": 1024}

    # Mocking the _fetch_data_from_s3 method
    zip_file_handler._fetch_data_from_s3 = MagicMock(return_value=b"test" + ZipFileHandler.EOCD_SIGNATURE + b"data")

    result = zip_file_handler._find_signature("test_file", ZipFileHandler.EOCD_SIGNATURE)
    assert ZipFileHandler.EOCD_SIGNATURE in result


def test_get_central_directory_start(zip_file_handler):
    zip_file_handler._find_signature = MagicMock(return_value=b"\x00" * 16 + struct.pack("<L", 12345))
    zip_file_handler._find_signature.return_value = b"\x00" * 16 + struct.pack("<L", 12345)
    assert zip_file_handler._get_central_directory_start("test_file") == 12345


def test_get_zip_files(zip_file_handler):
    zip_file_handler._get_central_directory_start = MagicMock(return_value=0)
    zip_file_handler._fetch_data_from_s3 = MagicMock(return_value=b"dummy_data")
    with patch("io.BytesIO", return_value=MagicMock(spec=io.BytesIO)):
        with patch("zipfile.ZipFile", return_value=MagicMock(spec=zipfile.ZipFile)):
            result, cd_start = zip_file_handler.get_zip_files("test_file")
            assert cd_start == 0


def test_decompressed_stream_seek():
    mock_file = MagicMock(spec=io.IOBase)
    mock_file.read = MagicMock()
    mock_file.read.return_value = b"test"

    # Mocking the tell method to return 0
    mock_file.tell.return_value = 0

    file_info = RemoteFileInsideArchive(
        uri="test_file.csv",
        last_modified=datetime.datetime(2022, 12, 28),
        start_offset=0,
        compressed_size=100,
        uncompressed_size=200,
        compression_method=zipfile.ZIP_STORED,
    )
    stream = DecompressedStream(mock_file, file_info)
    assert stream.seek(2) == 2


def test_decompressed_stream_seek_out_of_bounds():
    mock_file = MagicMock(spec=io.IOBase)
    mock_file.read = MagicMock()
    mock_file.read.return_value = b"test"

    mock_file.tell.return_value = 0

    file_info = RemoteFileInsideArchive(
        uri="test_file.csv",
        last_modified=datetime.datetime(2022, 12, 28),
        start_offset=0,
        compressed_size=4,
        uncompressed_size=8,
        compression_method=zipfile.ZIP_STORED,
    )
    stream = DecompressedStream(mock_file, file_info)
    assert stream.seek(10) == 8  # Assumes the seek will adjust to the file's size


def test_zip_content_reader_readline():
    mock_stream = MagicMock(spec=DecompressedStream)
    mock_stream.read.return_value = b"test\n"
    reader = ZipContentReader(mock_stream, encoding="utf-8")
    assert reader.readline() == "test\n"


def test_zip_content_reader_read():
    mock_stream = MagicMock(spec=DecompressedStream)
    mock_stream.read.return_value = b"test_data"
    reader = ZipContentReader(mock_stream, encoding="utf-8")
    assert reader.read(4) == "test"


def test_zip_content_reader_readline_newline_combinations():
    # Test for "\n" newline
    mock_stream = MagicMock(spec=DecompressedStream)
    mock_stream.read.side_effect = [b"test1\n", b""]
    reader = ZipContentReader(mock_stream, encoding="utf-8")
    assert reader.readline() == "test1\n"

    # Test for "\r" newline
    mock_stream.read.side_effect = [b"test2\r", b""]
    reader = ZipContentReader(mock_stream, encoding="utf-8")
    assert reader.readline() == "test2\r"

    # Test for "\r\n" newline
    mock_stream.read.side_effect = [b"test3\r", b"\n", b""]
    reader = ZipContentReader(mock_stream, encoding="utf-8")
    assert reader.readline() == "test3\r\n"


def test_zip_content_reader_iteration():
    # Setting up mock stream to return sequential strings ending in various newline combinations
    mock_stream = MagicMock(spec=DecompressedStream)
    mock_stream.read.side_effect = [b"line1\n", b"line2\r", b"line3\r\n", b"line4\n", b""]
    reader = ZipContentReader(mock_stream, encoding="utf-8")

    # Extract lines from the reader using iteration
    lines = list(reader)

    # Verify the lines extracted match expected values
    assert lines == ["line1\n", "line2\r", "line3\r\n", "line4\n"]
