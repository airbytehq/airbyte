#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import pytest
import requests
from source_airtable import SourceAirtable

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors


class TestAirtableStream:
    config = {"credentials": {"auth_method": "api_key", "api_key": "api key value"}}

    def test_read_records(self, tables_requests_mock, airtable_streams_requests_mock, expected_records):
        streams = SourceAirtable(catalog={}, config=self.config, state={}).streams(config=self.config)
        for stream in streams:
            data = [record.data for record in stream.read_records(sync_mode=SyncMode.full_refresh)]
            assert data == expected_records[stream.name]

    def test_pagination(self, tables_requests_mock, airtable_streams_with_pagination_requests_mock):
        stream = SourceAirtable(catalog={}, config=self.config, state={}).streams(config=self.config)[0]
        data = list(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert len(data) == 6

    def test_read_records_403_error(self, tables_requests_mock, airtable_streams_403_status_code_requests_mock):
        with pytest.raises(MessageRepresentationAirbyteTracedErrors) as exc_info:
            stream = SourceAirtable(catalog={}, config=self.config, state={}).streams(config=self.config)[0]
            data = list(stream.read_records(sync_mode=SyncMode.full_refresh))

        assert exc_info.value.failure_type == FailureType.config_error
        assert exc_info.value.message == "Permission denied or entity is unprocessable."
