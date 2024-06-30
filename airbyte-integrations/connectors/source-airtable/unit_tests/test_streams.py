#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

import pytest
import requests
from source_airtable.streams import URL_BASE, AirtableBases, AirtableStream, AirtableTables


class TestBases:

    bases_instance = AirtableBases(authenticator=MagicMock())

    def test_url_base(self):
        assert self.bases_instance.url_base == URL_BASE

    def test_primary_key(self):
        assert self.bases_instance.primary_key is None

    def test_path(self):
        assert self.bases_instance.path() == "meta/bases"

    def test_stream_name(self):
        assert self.bases_instance.name == "bases"

    @pytest.mark.parametrize(
        ("http_status", "should_retry"),
        [
            (200, False),
            (403, False),
            (422, False),
            (401, False),
        ],
    )
    def test_should_retry(self, http_status, should_retry):
        response_mock = MagicMock()
        response_mock.status_code = http_status
        assert self.bases_instance.should_retry(response_mock) == should_retry

    @pytest.mark.parametrize(
        ("http_status", "expected_backoff_time"),
        [
            (200, None),
            (429, 30),
        ],
    )
    def test_backoff_time(self, http_status, expected_backoff_time, requests_mock):
        url = "https://api.airtable.com/v0/meta/bases/"
        requests_mock.get(url, status_code=http_status, json={})
        response = requests.get(url)
        assert self.bases_instance.backoff_time(response) == expected_backoff_time

    def test_next_page(self, requests_mock):
        url = "https://api.airtable.com/v0/meta/bases/"
        requests_mock.get(url, status_code=200, json={"offset": "xyz"})
        response = requests.get(url)
        assert self.bases_instance.next_page_token(response) == {"offset": "xyz"}

    @pytest.mark.parametrize(
        ("next_page", "expected"),
        [
            (None, {}),
            ({"offset": "xyz"}, {"offset": "xyz"}),
        ],
    )
    def test_request_params(self, next_page, expected):
        assert self.bases_instance.request_params(next_page) == expected

    def test_parse_response(self, fake_bases_response, expected_bases_response, requests_mock):
        url = "https://api.airtable.com/v0/meta/bases/"
        requests_mock.get(url, status_code=200, json=fake_bases_response)
        response = requests.get(url)
        assert list(self.bases_instance.parse_response(response)) == expected_bases_response


class TestTables:

    tables_instance = AirtableTables(base_id="test_base_id", authenticator=MagicMock())

    def test_path(self):
        assert self.tables_instance.path() == "meta/bases/test_base_id/tables"

    def test_stream_name(self):
        assert self.tables_instance.name == "tables"


class TestAirtableStream:
    def stream_instance(self, prepared_stream):
        return AirtableStream(
            stream_path=prepared_stream["stream_path"],
            stream_name=prepared_stream["stream"].name,
            stream_schema=prepared_stream["stream"].json_schema,
            table_name=prepared_stream["table_name"],
            authenticator=MagicMock(),
        )

    def test_streams_url_base(self, prepared_stream):
        assert self.stream_instance(prepared_stream).url_base == URL_BASE

    def test_streams_primary_key(self, prepared_stream):
        assert self.stream_instance(prepared_stream).primary_key == "id"

    def test_streams_name(self, prepared_stream):
        assert self.stream_instance(prepared_stream).name == "test_base/test_table"

    def test_streams_path(self, prepared_stream):
        assert self.stream_instance(prepared_stream).path() == "some_base_id/some_table_id"

    @pytest.mark.parametrize(
        ("http_status", "should_retry"),
        [
            (200, False),
            (403, False),
            (422, False),
            (401, False),
        ],
    )
    def test_streams_should_retry(self, http_status, should_retry, prepared_stream):
        response_mock = MagicMock()
        response_mock.status_code = http_status
        assert self.stream_instance(prepared_stream).should_retry(response_mock) == should_retry

    @pytest.mark.parametrize(
        ("http_status", "expected_backoff_time"),
        [
            (200, None),
            (429, 30),
        ],
    )
    def test_streams_backoff_time(self, http_status, expected_backoff_time, prepared_stream, requests_mock):
        url = "https://api.airtable.com/v0/meta/bases/"
        requests_mock.get(url, status_code=http_status, json={})
        response = requests.get(url)
        assert self.stream_instance(prepared_stream).backoff_time(response) == expected_backoff_time

    def test_streams_get_json_schema(self, prepared_stream):
        assert self.stream_instance(prepared_stream).get_json_schema() == prepared_stream["stream"].json_schema

    def test_streams_next_page(self, prepared_stream, requests_mock):
        url = "https://api.airtable.com/v0/meta/bases/"
        requests_mock.get(url, status_code=200, json={"offset": "xyz"})
        response = requests.get(url)
        assert self.stream_instance(prepared_stream).next_page_token(response) == {"offset": "xyz"}

    @pytest.mark.parametrize(
        ("next_page", "expected"),
        [
            (None, {}),
            ({"offset": "xyz"}, {"offset": "xyz"}),
        ],
    )
    def test_streams_request_params(self, next_page, expected, prepared_stream):
        assert self.stream_instance(prepared_stream).request_params(next_page) == expected

    def test_streams_parse_response(self, prepared_stream, streams_json_response, streams_processed_response, requests_mock):
        stream = self.stream_instance(prepared_stream)
        url = f"{stream.url_base}/{stream.path()}"
        requests_mock.get(url, status_code=200, json=streams_json_response)
        response = requests.get(url)
        assert list(stream.parse_response(response)) == streams_processed_response
