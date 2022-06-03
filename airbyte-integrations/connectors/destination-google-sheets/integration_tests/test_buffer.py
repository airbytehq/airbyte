#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import io
from typing import Iterable

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from destination_google_sheets.buffer import WriteBufferMixin

# ----- PREPARE ENV -----

# path to configured_catalog json file
TEST_CATALOG_PATH: str = "integration_tests/test_data/test_buffer_catalog.json"
# path to test records txt file
TEST_RECORDS_PATH: str = "integration_tests/test_data/messages.txt"
# reading prepared catalog with streams
TEST_CATALOG: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog.parse_file(TEST_CATALOG_PATH)
# instance of WriteBufferMixin
TEST_WRITE_BUFFER: WriteBufferMixin = WriteBufferMixin()


# reading input messages from file
def read_input_messages(records_path: str) -> Iterable[AirbyteMessage]:
    with open(records_path, "rb") as f:
        input_stream = io.TextIOWrapper(f, encoding="utf-8")
        for line in input_stream:
            yield AirbyteMessage.parse_raw(line)


# ----- BEGIN TESTS -----


def test_logger():
    test_logger = TEST_WRITE_BUFFER.logger
    assert isinstance(test_logger, AirbyteLogger)


@pytest.mark.parametrize(
    "buffer, stream_name",
    [
        (TEST_WRITE_BUFFER.records_buffer, "stream_1"),
        (TEST_WRITE_BUFFER.records_buffer, "stream_2"),
        (TEST_WRITE_BUFFER.records_buffer, "stream_3"),
        ((TEST_WRITE_BUFFER.stream_info), "stream_1"),
        (TEST_WRITE_BUFFER.stream_info, "stream_2"),
        (TEST_WRITE_BUFFER.stream_info, "stream_2"),
    ],
    ids=[
        "records_buf_stream_1",
        "records_buf_stream_2",
        "records_buf_stream_3",
        "stream_info_stream_1",
        "stream_info_stream_2",
        "stream_info_stream_3",
    ],
)
def test_init_buffer_stream(buffer, stream_name):
    for configured_stream in TEST_CATALOG.streams:
        TEST_WRITE_BUFFER.init_buffer_stream(configured_stream)

    for stream in buffer:
        if stream_name in stream:
            assert stream_name in stream


def test_add_to_buffer(input_messages=read_input_messages(TEST_RECORDS_PATH)):
    for message in input_messages:
        if message.type == Type.RECORD:
            record = message.record
            TEST_WRITE_BUFFER.add_to_buffer(record.stream, record.data)
        else:
            continue

    for stream in TEST_WRITE_BUFFER.records_buffer:
        assert len(TEST_WRITE_BUFFER.records_buffer[stream]) > 0


@pytest.mark.parametrize(
    "stream_name, expected_count",
    [
        ("stream_1", 7),
        ("stream_2", 6),
        ("stream_3", 6),
    ],
    ids=["stream_1", "stream_2", "stream_3"],
)
def test_records_count_in_buffer(stream_name, expected_count):
    assert len(TEST_WRITE_BUFFER.records_buffer[stream_name]) == expected_count


@pytest.mark.parametrize(
    "stream_name",
    [
        ("stream_1"),
        ("stream_2"),
        ("stream_3"),
    ],
    ids=["stream_1", "stream_2", "stream_3"],
)
def test_clear_buffer(stream_name):
    TEST_WRITE_BUFFER.clear_buffer(stream_name)
    # check the buffer is cleaned
    assert len(TEST_WRITE_BUFFER.records_buffer[stream_name]) == 0


@pytest.mark.parametrize(
    "stream_name, record, expected",
    [
        ("stream_1", {"id": 123}, {"id": 123, "key1": "", "list": ""}),
        ("stream_2", {"id": 123, "key2": "value"}, {"id": 123, "key1": "", "list": ""}),
        ("stream_3", {}, {"id": "", "key1": "", "list": ""}),
    ],
    ids=["Undersetting", "Oversetting", "empty_record"],
)
def test_normalize_record(stream_name, record, expected):
    actual = TEST_WRITE_BUFFER._normalize_record(stream_name, record)
    assert actual == expected


@pytest.mark.parametrize(
    "buffer, expected_len",
    [
        (TEST_WRITE_BUFFER.records_buffer, 0),
        (TEST_WRITE_BUFFER.stream_info, 0),
    ],
    ids=["records_buffer", "stream_info"],
)
def test_check_buffers_are_null(buffer, expected_len):
    buffer.clear()
    assert len(buffer) == expected_len


# ----- END TESTS -----
