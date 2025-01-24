#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from source_airtable import SourceAirtable


class TestSourceAirtable:
    config = {"credentials": {"auth_method": "api_key", "api_key": "api key value"}}

    def test_streams(self, tables_requests_mock):
        streams = SourceAirtable(catalog={}, config=self.config, state={}).streams(config=self.config)
        assert len(streams) == 2
        assert [stream.name for stream in streams] == ["base_1/table_1/table_id_1", "base_1/table_2/table_id_2"]

    def test_streams_schema(self, tables_requests_mock):
        catalog = SourceAirtable(catalog={}, config=self.config, state={}).discover(logger=MagicMock(), config=self.config)

        schema = catalog.streams[0].json_schema["properties"]
        assert schema == {
            "_airtable_created_time": {"type": ["null", "string"]},
            "_airtable_id": {"type": ["null", "string"]},
            "_airtable_table_name": {"type": ["null", "string"]},
            "attachments": {"type": ["null", "string"]},
            "clo_with_empty_strings": {"type": ["null", "string"]},
            "name": {"type": ["null", "string"]},
            "notes": {"type": ["null", "string"]},
            "status": {"type": ["null", "string"]},
        }

        schema = catalog.streams[1].json_schema["properties"]
        assert schema == {
            "_airtable_created_time": {"type": ["null", "string"]},
            "_airtable_id": {"type": ["null", "string"]},
            "_airtable_table_name": {"type": ["null", "string"]},
            "assignee": {"type": ["null", "array"], "items": {"type": ["null", "number"]}},
            "assignee_(from_table_6)": {"type": ["null", "array"], "items": {"type": ["null", "number"]}},
            "barcode": {"type": ["null", "string"]},
            "float": {"type": ["null", "number"]},
            "integer": {"type": ["null", "number"]},
            "name": {"type": ["null", "string"]},
            "status": {"type": ["null", "string"]},
            "table_6": {"type": ["null", "array"], "items": {"type": ["null", "string"]}},
        }

    def test_check_connection(self, tables_requests_mock, airtable_streams_requests_mock):
        status = SourceAirtable(catalog={}, config=self.config, state={}).check_connection(logger=MagicMock(), config=self.config)
        assert status == (True, None)

    def test_check_connection_failed(self, tables_requests_mock, airtable_streams_403_status_code_requests_mock):
        status = SourceAirtable(catalog={}, config=self.config, state={}).check_connection(logger=MagicMock(), config=self.config)
        assert status == (False, "Permission denied or entity is unprocessable.")

    def test_check_connection_no_streams_available(self, requests_mock):
        requests_mock.get(
            "https://api.airtable.com/v0/meta/bases",
            status_code=200,
            json={"bases": []},
        )
        status, reason = SourceAirtable(catalog={}, config=self.config, state={}).check_connection(logger=MagicMock(), config=self.config)
        assert "No streams to connect to from source" in reason
        assert status is False
