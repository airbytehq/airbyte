# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import datetime
import io
import random
import struct
import zipfile
import zlib
from unittest.mock import MagicMock, patch

import pytest
from source_s3.v4.zip_reader import (
    WINZIP_AES_COMPRESSION_TYPE,
    DecompressedStream,
    RemoteFileInsideArchive,
    ZipContentReader,
    ZipFileHandler,
)


# --- ZipCrypto test fixture helpers ---------------------------------------------------------
#
# Python's stdlib `zipfile` can *read* ZipCrypto-encrypted entries but has no support for
# *writing* them, so there's no way to build a password-protected test fixture with stdlib alone.
# `_zip_crypto_encrypt` is a small, from-scratch implementation of the traditional PKWARE ("ZipCrypto")
# stream cipher, mirroring the key schedule in `zipfile._ZipDecrypter`. It's used only to author
# genuine password-protected zip bytes for these tests; production code never encrypts, only decrypts.


def _zip_crypto_encrypt(password: bytes, data: bytes, crc: int) -> bytes:
    """Encrypt `data` (already compressed) with the traditional ZipCrypto cipher, prefixed with
    the mandatory 12-byte encryption header, mirroring `zipfile._ZipDecrypter`'s key schedule."""
    key0, key1, key2 = 305419896, 591751049, 878082192
    crctable = [zipfile._gen_crc(i) for i in range(256)]

    def crc32(byte, crc_):
        return (crc_ >> 8) ^ crctable[(crc_ ^ byte) & 0xFF]

    def update_keys(byte):
        nonlocal key0, key1, key2
        key0 = crc32(byte, key0)
        key1 = (key1 + (key0 & 0xFF)) & 0xFFFFFFFF
        key1 = (key1 * 134775813 + 1) & 0xFFFFFFFF
        key2 = crc32(key1 >> 24, key2)

    for byte in password:
        update_keys(byte)

    # First 11 header bytes are random; the 12th is the password-check byte.
    header = bytes(bytearray(random.getrandbits(8) for _ in range(11)) + bytes([(crc >> 24) & 0xFF]))

    encrypted = bytearray()
    for plain_byte in header + data:
        keystream_byte = ((key2 | 2) * ((key2 | 2) ^ 1) >> 8) & 0xFF
        encrypted.append(plain_byte ^ keystream_byte)
        update_keys(plain_byte)
    return bytes(encrypted)


def build_encrypted_zip_bytes(filename: str, content: bytes, password: bytes) -> bytes:
    """Build the bytes of a minimal, valid, single-entry ZipCrypto-encrypted zip file."""
    crc = zlib.crc32(content) & 0xFFFFFFFF
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    compressed = compressor.compress(content) + compressor.flush()
    encrypted = _zip_crypto_encrypt(password, compressed, crc)  # 12-byte header + ciphertext

    fname = filename.encode()
    flag_bits = 0x1  # bit 0: entry is encrypted
    mod_time, mod_date = 0, 0x21

    local_header = struct.pack(
        "<4sHHHHHLLLHH",
        b"PK\x03\x04",
        20,
        flag_bits,
        zipfile.ZIP_DEFLATED,
        mod_time,
        mod_date,
        crc,
        len(encrypted),
        len(content),
        len(fname),
        0,
    )
    local_entry = local_header + fname + encrypted

    central_header = struct.pack(
        "<4sHHHHHHLLLHHHHHLL",
        b"PK\x01\x02",
        20,
        20,
        flag_bits,
        zipfile.ZIP_DEFLATED,
        mod_time,
        mod_date,
        crc,
        len(encrypted),
        len(content),
        len(fname),
        0,
        0,
        0,
        0,
        0,
        0,
    )
    central_entry = central_header + fname

    cd_start = len(local_entry)
    eocd = struct.pack("<4sHHHHLLH", b"PK\x05\x06", 0, 0, 1, 1, len(central_entry), cd_start, 0)

    return local_entry + central_entry + eocd


def encrypted_file_info(uri: str, content: bytes, crc: int) -> RemoteFileInsideArchive:
    """A RemoteFileInsideArchive matching the layout produced by `build_encrypted_zip_bytes` (always ZIP_DEFLATED)."""
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    compressed_size = len(compressor.compress(content) + compressor.flush()) + DecompressedStream.ZIP_CRYPTO_HEADER_SIZE
    return RemoteFileInsideArchive(
        uri=uri,
        last_modified=datetime.datetime(2022, 12, 28),
        start_offset=0,
        compressed_size=compressed_size,
        uncompressed_size=len(content),
        compression_method=zipfile.ZIP_DEFLATED,
        flag_bits=0x1,
        crc=crc,
    )


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


# --- Password-protected (ZipCrypto) decryption tests ----------------------------------------


def test_decompressed_stream_decrypts_with_correct_password():
    content = b"row,value\n1,alpha\n2,beta\n" * 50
    password = "s3cr3t!"
    zip_bytes = build_encrypted_zip_bytes("data.csv", content, password.encode())
    crc = zlib.crc32(content) & 0xFFFFFFFF
    file_info = encrypted_file_info("data.csv", content, crc)

    stream = DecompressedStream(io.BytesIO(zip_bytes), file_info, password=password)

    assert stream.read() == content


def test_decompressed_stream_decrypts_correctly_after_seek():
    content = (b"0123456789" * 100)  # 1000 bytes; easy to verify arbitrary offsets
    password = "s3cr3t!"
    zip_bytes = build_encrypted_zip_bytes("data.bin", content, password.encode())
    crc = zlib.crc32(content) & 0xFFFFFFFF
    file_info = encrypted_file_info("data.bin", content, crc)

    stream = DecompressedStream(io.BytesIO(zip_bytes), file_info, password=password)
    stream.seek(500)

    assert stream.read(10) == content[500:510]


def test_decompressed_stream_via_zip_content_reader():
    content = b"line one\nline two\nline three\n"
    password = "s3cr3t!"
    zip_bytes = build_encrypted_zip_bytes("data.txt", content, password.encode())
    crc = zlib.crc32(content) & 0xFFFFFFFF
    file_info = encrypted_file_info("data.txt", content, crc)

    stream = DecompressedStream(io.BytesIO(zip_bytes), file_info, password=password)
    reader = ZipContentReader(stream, encoding="utf-8")

    assert list(reader) == ["line one\n", "line two\n", "line three\n"]


def test_decompressed_stream_wrong_password_raises():
    content = b"top secret payload" * 10
    zip_bytes = build_encrypted_zip_bytes("secret.csv", content, b"correct-password")
    crc = zlib.crc32(content) & 0xFFFFFFFF
    file_info = encrypted_file_info("secret.csv", content, crc)

    with pytest.raises(ValueError, match="Incorrect zip password"):
        DecompressedStream(io.BytesIO(zip_bytes), file_info, password="wrong-password")


def test_decompressed_stream_missing_password_raises():
    file_info = RemoteFileInsideArchive(
        uri="secret.csv",
        last_modified=datetime.datetime(2022, 12, 28),
        start_offset=0,
        compressed_size=100,
        uncompressed_size=200,
        compression_method=zipfile.ZIP_DEFLATED,
        flag_bits=0x1,  # encrypted
        crc=0,
    )

    with pytest.raises(ValueError, match="no zip password was configured"):
        DecompressedStream(io.BytesIO(b"\x00" * 30), file_info)


def test_decompressed_stream_aes_encryption_not_supported():
    file_info = RemoteFileInsideArchive(
        uri="secret.csv",
        last_modified=datetime.datetime(2022, 12, 28),
        start_offset=0,
        compressed_size=100,
        uncompressed_size=200,
        compression_method=WINZIP_AES_COMPRESSION_TYPE,
        flag_bits=0x1,  # encrypted
        crc=0,
    )

    with pytest.raises(ValueError, match="AES-encrypted"):
        DecompressedStream(io.BytesIO(b"\x00" * 30), file_info, password="whatever")


def test_decompressed_stream_ignores_password_for_unencrypted_file():
    mock_file = MagicMock(spec=io.IOBase)
    mock_file.read = MagicMock(return_value=b"test")
    mock_file.tell.return_value = 0

    file_info = RemoteFileInsideArchive(
        uri="plain.csv",
        last_modified=datetime.datetime(2022, 12, 28),
        start_offset=0,
        compressed_size=100,
        uncompressed_size=200,
        compression_method=zipfile.ZIP_STORED,
    )

    # A password supplied for a file that was never encrypted should simply be unused.
    stream = DecompressedStream(mock_file, file_info, password="unused-password")

    assert stream._decrypter is None
