#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest


@pytest.fixture
def config():
    return {
        "api_key": "key1234567890",
    }


@pytest.fixture
def tables_requests_mock(requests_mock):
    requests_mock.get(
        "https://api.airtable.com/v0/meta/bases",
        status_code=200,
        json={"bases": [{"id": "base_1", "name": "base 1", "permissionLevel": "create"}]},
    )
    requests_mock.get(
        "https://api.airtable.com/v0/meta/bases/base_1/tables",
        status_code=200,
        json={
            "tables": [
                {
                    "id": "table_id_1",
                    "name": "Table 1",
                    "primaryFieldId": "primaryFieldId_tabel_1",
                    "fields": [
                        {"type": "singleLineText", "id": "primaryFieldId_tabel_1", "name": "Name"},
                        {"type": "multilineText", "id": "multilineText", "name": "Notes"},
                        {"type": "multipleAttachments", "options": {"isReversed": False}, "id": "id", "name": "Attachments"},
                        {
                            "type": "singleSelect",
                            "options": {
                                "choices": [
                                    {"id": "id", "name": "Todo", "color": "redLight2"},
                                    {"id": "id", "name": "In progress", "color": "yellowLight2"},
                                    {"id": "id", "name": "Done", "color": "greenLight2"},
                                    {"id": "id", "name": "test", "color": "grayLight2"},
                                ]
                            },
                            "id": "id",
                            "name": "Status",
                        },
                        {"type": "multilineText", "id": "id", "name": "clo_with_empty_strings"},
                    ],
                },
                {
                    "id": "table_id_2",
                    "name": "Table 2",
                    "primaryFieldId": "primaryFieldId_table_2",
                    "fields": [
                        {"type": "singleLineText", "id": "id", "name": "Name"},
                        {
                            "type": "formula",
                            "options": {
                                "isValid": True,
                                "formula": "1+1",
                                "referencedFieldIds": [],
                                "result": {"type": "number", "options": {"precision": 0}},
                            },
                            "id": "id",
                            "name": "Assignee",
                        },
                        {
                            "type": "singleSelect",
                            "options": {
                                "choices": [
                                    {"id": "id", "name": "Todo", "color": "redLight2"},
                                    {"id": "id", "name": "In progress", "color": "yellowLight2"},
                                    {"id": "id", "name": "Done", "color": "greenLight2"},
                                ]
                            },
                            "id": "id",
                            "name": "Status",
                        },
                        {"type": "number", "options": {"precision": 1}, "id": "id", "name": "Float"},
                        {"type": "number", "options": {"precision": 0}, "id": "id", "name": "Integer"},
                        {"type": "barcode", "id": "fld899obV6ycadgWS", "name": "Barcode"},
                        {
                            "type": "multipleRecordLinks",
                            "options": {"linkedTableId": "id", "isReversed": False, "prefersSingleRecordLink": False},
                            "id": "id",
                            "name": "Table 6",
                        },
                        {
                            "type": "multipleLookupValues",
                            "options": {
                                "isValid": True,
                                "recordLinkFieldId": "id",
                                "fieldIdInLinkedTable": "id",
                                "result": {"type": "number", "options": {"precision": 0}},
                            },
                            "id": "id",
                            "name": "Assignee (from Table 6)",
                        },
                    ],
                },
            ]
        },
    )


@pytest.fixture
def airtable_streams_requests_mock(requests_mock):
    requests_mock.get(
        "https://api.airtable.com/v0/base_1/table_id_1",
        status_code=200,
        json={
            "records": [
                {
                    "id": "table_1_record_id_1",
                    "createdTime": "2021-11-16T13:30:17.000Z",
                    "fields": {"Name": "test2", "Status": "test", "Notes": "test_note2"},
                },
                {
                    "id": "table_1_record_id_2",
                    "createdTime": "2022-12-22T20:58:05.000Z",
                    "fields": {
                        "Name": "test4_after_empty",
                        "clo_with_empty_strings": "bla bla bla",
                        "Status": "In progress",
                        "Notes": "test_note4",
                    },
                },
                {
                    "id": "table_1_record_id_3",
                    "createdTime": "2021-11-16T13:30:17.000Z",
                    "fields": {"Name": "test3", "clo_with_empty_strings": "test text here", "Status": "test", "Notes": "test-note3"},
                },
            ]
        },
    )
    requests_mock.get(
        "https://api.airtable.com/v0/base_1/table_id_2",
        status_code=200,
        json={
            "records": [
                {
                    "id": "table_2_record_id_1",
                    "createdTime": "2020-01-25T02:04:26.000Z",
                    "fields": {
                        "Name": "test_negative",
                        "Table 6": ["table_2_record_id_1", "table_2_record_id_3"],
                        "Float": 0.3,
                        "Status": "In progress",
                        "Integer": -1,
                        "Assignee": [2],
                        "Assignee (from Table 6)": [2, 2],
                    },
                },
                {
                    "id": "table_2_record_id_2",
                    "createdTime": "2020-01-25T02:04:26.000Z",
                    "fields": {
                        "Name": "test_attachment",
                        "Table 6": ["table_2_record_id_2", "table_2_record_id_3"],
                        "Float": 0.3,
                        "Status": "Todo",
                        "Integer": 1,
                        "Assignee": [2],
                        "Assignee (from Table 6)": [2, 2],
                    },
                },
                {
                    "id": "table_2_record_id_3",
                    "createdTime": "2020-01-25T02:04:26.000Z",
                    "fields": {
                        "Name": "test_normal",
                        "Table 6": ["table_2_record_id_3", "table_2_record_id_1", "table_2_record_id_2"],
                        "Float": 0.7,
                        "Status": "Done",
                        "Integer": 2,
                        "Assignee": [2],
                        "Assignee (from Table 6)": [2, 2, 2],
                    },
                },
            ]
        },
    )


@pytest.fixture
def expected_records():
    expected_records = {
        "base_1/table_1/table_id_1": [
            {
                "_airtable_created_time": "2021-11-16T13:30:17.000Z",
                "_airtable_id": "table_1_record_id_1",
                "_airtable_table_name": "Table 1",
                "name": "test2",
                "notes": "test_note2",
                "status": "test",
            },
            {
                "_airtable_created_time": "2022-12-22T20:58:05.000Z",
                "_airtable_id": "table_1_record_id_2",
                "_airtable_table_name": "Table 1",
                "clo_with_empty_strings": "bla bla bla",
                "name": "test4_after_empty",
                "notes": "test_note4",
                "status": "In progress",
            },
            {
                "_airtable_created_time": "2021-11-16T13:30:17.000Z",
                "_airtable_id": "table_1_record_id_3",
                "_airtable_table_name": "Table 1",
                "clo_with_empty_strings": "test text here",
                "name": "test3",
                "notes": "test-note3",
                "status": "test",
            },
        ],
        "base_1/table_2/table_id_2": [
            {
                "_airtable_created_time": "2020-01-25T02:04:26.000Z",
                "_airtable_id": "table_2_record_id_1",
                "_airtable_table_name": "Table 2",
                "assignee": [2],
                "assignee_(from_table_6)": [2, 2],
                "float": 0.3,
                "integer": -1,
                "name": "test_negative",
                "status": "In progress",
                "table_6": ["table_2_record_id_1", "table_2_record_id_3"],
            },
            {
                "_airtable_created_time": "2020-01-25T02:04:26.000Z",
                "_airtable_id": "table_2_record_id_2",
                "_airtable_table_name": "Table 2",
                "assignee": [2],
                "assignee_(from_table_6)": [2, 2],
                "float": 0.3,
                "integer": 1,
                "name": "test_attachment",
                "status": "Todo",
                "table_6": ["table_2_record_id_2", "table_2_record_id_3"],
            },
            {
                "_airtable_created_time": "2020-01-25T02:04:26.000Z",
                "_airtable_id": "table_2_record_id_3",
                "_airtable_table_name": "Table 2",
                "assignee": [2],
                "assignee_(from_table_6)": [2, 2, 2],
                "float": 0.7,
                "integer": 2,
                "name": "test_normal",
                "status": "Done",
                "table_6": ["table_2_record_id_3", "table_2_record_id_1", "table_2_record_id_2"],
            },
        ],
    }
    return expected_records


@pytest.fixture
def airtable_streams_with_pagination_requests_mock(requests_mock):
    requests_mock.get(
        "https://api.airtable.com/v0/base_1/table_id_1",
        status_code=200,
        json={
            "records": [
                {
                    "id": "table_1_record_id_1",
                    "createdTime": "2021-11-16T13:30:17.000Z",
                    "fields": {"Name": "test2", "Status": "test", "Notes": "test_note2"},
                },
                {
                    "id": "table_1_record_id_2",
                    "createdTime": "2022-12-22T20:58:05.000Z",
                    "fields": {
                        "Name": "test4_after_empty",
                        "clo_with_empty_strings": "bla bla bla",
                        "Status": "In progress",
                        "Notes": "test_note4",
                    },
                },
                {
                    "id": "table_1_record_id_3",
                    "createdTime": "2021-11-16T13:30:17.000Z",
                    "fields": {"Name": "test3", "clo_with_empty_strings": "test text here", "Status": "test", "Notes": "test-note3"},
                },
            ],
            "offset": "nextpage",
        },
    )
    requests_mock.get(
        "https://api.airtable.com/v0/base_1/table_id_1?offset=nextpage",
        status_code=200,
        json={
            "records": [
                {
                    "id": "table_1_record_id_1",
                    "createdTime": "2021-11-16T13:30:17.000Z",
                    "fields": {"Name": "test2", "Status": "test", "Notes": "test_note2"},
                },
                {
                    "id": "table_1_record_id_2",
                    "createdTime": "2022-12-22T20:58:05.000Z",
                    "fields": {
                        "Name": "test4_after_empty",
                        "clo_with_empty_strings": "bla bla bla",
                        "Status": "In progress",
                        "Notes": "test_note4",
                    },
                },
                {
                    "id": "table_1_record_id_3",
                    "createdTime": "2021-11-16T13:30:17.000Z",
                    "fields": {"Name": "test3", "clo_with_empty_strings": "test text here", "Status": "test", "Notes": "test-note3"},
                },
            ],
        },
    )


@pytest.fixture
def airtable_streams_403_status_code_requests_mock(requests_mock):
    requests_mock.get("https://api.airtable.com/v0/base_1/table_id_1", status_code=403, json={})
