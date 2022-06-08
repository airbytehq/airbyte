#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_google_sheets.writer import GoogleSheetsWriter
from integration_tests.test_spreadsheet import TEST_SPREADSHEET

# ----- PREPARE ENV -----


# path to configured_catalog json file
TEST_CATALOG_PATH: str = "integration_tests/test_data/test_writer_catalog.json"
# reading prepared catalog with streams
TEST_CATALOG: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog.parse_file(TEST_CATALOG_PATH)
# define test writer
TEST_WRITER: GoogleSheetsWriter = GoogleSheetsWriter(TEST_SPREADSHEET)
# set flush buffer interval
TEST_WRITER.flush_interval = 2
# test stream name
TEST_STREAM: str = "stream_1"


# ----- BEGIN TESTS -----


def _prepare_buffers():
    for configured_stream in TEST_CATALOG.streams:
        TEST_WRITER.init_buffer_stream(configured_stream)


def test_delete_stream_entries():
    _prepare_buffers()
    TEST_WRITER.delete_stream_entries(TEST_STREAM)
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    records = test_wks.get_all_records()
    assert len(records) == 0


def test_check_headers():
    TEST_WRITER.check_headers(TEST_STREAM)
    assert True if TEST_WRITER.stream_info[TEST_STREAM]["is_set"] else False


# define input records
# 3 records are defined, but 2 should be written, because of flush_interval
# the last one should be available for other tests.
input_records = [
    {
        "stream": TEST_STREAM,
        "data": {"id": 1},
    },
    {
        "stream": TEST_STREAM,
        "data": {"id": 2, "key1": "test"},
    },
    {
        "stream": TEST_STREAM,
        "data": {"id": 3, "key1": "test", "list": ["str_in_list"]},
    },
]


@pytest.mark.parametrize(
    "expected",
    [
        ([{"id": 1, "key1": "", "list": ""}, {"id": 2, "key1": "test", "list": ""}]),
    ],
    ids=["2/3 records"],
)
def test_queue_write_operation(expected):
    for record in input_records:
        stream_name = record["stream"]
        data = record["data"]
        TEST_WRITER.add_to_buffer(stream_name, data)
        TEST_WRITER.queue_write_operation(stream_name)

    # check expected records are written into target worksheet
    test_wks = TEST_SPREADSHEET.open_worksheet(stream_name)
    records = test_wks.get_all_records()
    assert records == expected


@pytest.mark.parametrize(
    "expected",
    [
        ([{"id": 1, "key1": "", "list": ""}, {"id": 2, "key1": "test", "list": ""}, {"id": 3, "key1": "test", "list": "['str_in_list']"}]),
    ],
    ids=["3/3 records"],
)
def test_write_whats_left(expected):
    TEST_WRITER.write_whats_left()

    # check expected records are written into target worksheet
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    records = test_wks.get_all_records()
    assert records == expected

    # clean worksheet for future tests
    test_wks.clear()


input_dup_records = [
    {
        "stream": TEST_STREAM,
        "data": {"id": 1, "key1": "test"},
    },
    {
        "stream": TEST_STREAM,
        "data": {"id": 1, "key1": "test"},
    },
]


@pytest.mark.parametrize(
    "expected",
    [
        ([{"id": 1, "key1": "test", "list": ""}]),
    ],
    ids=["dedup_records"],
)
def test_deduplicate_records(expected):
    # set `is_set` for headers to False
    # because previously the headers have been set already
    TEST_WRITER.stream_info[TEST_STREAM]["is_set"] = False

    # writing duplicates
    for record in input_dup_records:
        stream_name = record["stream"]
        data = record["data"]
        TEST_WRITER.add_to_buffer(stream_name, data)
        TEST_WRITER.queue_write_operation(stream_name)

    # removing duplicates
    for configured_stream in TEST_CATALOG.streams:
        TEST_WRITER.deduplicate_records(configured_stream)

    # checking result
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    records = test_wks.get_all_records()
    assert records == expected

    # remove the test worksheet after tests
    TEST_SPREADSHEET.spreadsheet.del_worksheet(test_wks)


# ----- END TESTS -----
