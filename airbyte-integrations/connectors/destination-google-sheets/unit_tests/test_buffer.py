#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import io
from typing import Iterable

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from destination_google_sheets.buffer import WriteBuffer

# ----- PREPARE ENV -----

# path to configured_catalog json file
TEST_CATALOG_PATH: str = "unit_tests/test_data/test_catalog.json"
# path to test records txt file
TEST_RECORDS_PATH: str = "integration_tests/messages.txt"

# reading prepared catalog with streams
TEST_CATALOG: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog.parse_file(TEST_CATALOG_PATH)
# instance of WriteBuffer
TEST_WRITE_BUFFER: WriteBuffer = WriteBuffer()


# reading input messages from file
def read_input_messages(records_path: str = TEST_RECORDS_PATH) -> Iterable[AirbyteMessage]:
    with open(records_path, "rb") as f:
        input_stream = io.TextIOWrapper(f, encoding="utf-8")
        for line in input_stream:
            yield AirbyteMessage.parse_raw(line)


# ----- END PREPARE ENV -----

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
def test_buffer_stream(buffer, stream_name):
    for configured_stream in TEST_CATALOG.streams:
        TEST_WRITE_BUFFER.buffer_stream(configured_stream)

    for stream in buffer:
        if stream_name in stream:
            assert stream_name in stream


def test_add_to_buffer(input_messages=read_input_messages()):
    for message in input_messages:
        if message.type == Type.RECORD:
            record = message.record
            TEST_WRITE_BUFFER.add_to_buffer(record.stream, record.data)
        else:
            continue

    for stream in TEST_WRITE_BUFFER.records_buffer:
        stream_name = list(stream.keys())[0]
        assert len(stream[stream_name]) > 0


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
    for stream in TEST_WRITE_BUFFER.records_buffer:
        if stream_name in stream:
            assert len(stream[stream_name]) == expected_count


@pytest.mark.parametrize(
    "stream_name",
    [
        ("stream_1"),
        ("stream_2"),
        ("stream_3"),
    ],
    ids=["stream_1", "stream_2", "stream_3"],
)
def test_flush_buffer(stream_name):
    TEST_WRITE_BUFFER.flush_buffer(stream_name)

    # check the buffer is cleaned
    for stream in TEST_WRITE_BUFFER.records_buffer:
        if stream_name in stream:
            assert len(stream[stream_name]) == 0


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
    actual = TEST_WRITE_BUFFER.normalize_record(stream_name, record)
    assert actual == expected


@pytest.mark.parametrize(
    "record, expected",
    [
        ({"id": 123}, ["123"]),
        ({"id": 123, "key2": "value"}, ["123", "value"]),
        ({}, []),
    ],
    ids=["num", "num / str", "empty_record"],
)
def test_get_record_values(record, expected):
    actual = TEST_WRITE_BUFFER.get_record_values(record)
    assert actual == expected


@pytest.mark.parametrize(
    "list_values, expected",
    [
        ([{"key": "value"}], ["{'key': 'value'}"]),
        ([123, ["str in list"]], ["123", "['str in list']"]),
        ([], []),
    ],
    ids=["key_value", "num / list", "empty_record"],
)
def test_values_to_str(list_values, expected):
    actual = TEST_WRITE_BUFFER.values_to_str(list_values)
    assert actual == expected


# ----- END TESTS -----
