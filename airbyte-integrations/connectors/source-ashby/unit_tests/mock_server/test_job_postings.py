# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Mock server tests for the `job_postings` stream on `source-ashby`."""

import json
import logging
from typing import Any, Dict, List
from unittest import TestCase

from jsonschema import Draft7Validator, FormatChecker
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import AshbyRequestBuilder


_STREAM_NAME = "job_postings"


def _page(records: List[Dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"success": True, "results": records, "moreDataAvailable": False}), status_code=200)


def _job_postings_request() -> HttpRequest:
    return AshbyRequestBuilder.endpoint("/jobPosting.list").with_api_key("test-api-key").with_limit(100).build()


class TestJobPostings(TestCase):
    @HttpMocker()
    def test_published_date_is_a_date_and_record_validates(self, http_mocker: HttpMocker):
        config = ConfigBuilder().build()
        source = get_source(config=config)
        catalog = source.discover(logging.getLogger("airbyte"), config)
        schema = {stream.name: stream for stream in catalog.streams}[_STREAM_NAME].json_schema
        record = {"id": "posting-1", "publishedDate": "2024-01-15"}

        http_mocker.post(_job_postings_request(), _page([record]))
        read_output = read(
            source,
            config=config,
            catalog=CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
            state=StateBuilder().build(),
        )

        assert read_output.errors == []
        emitted_record = read_output.records[0].record.data
        assert emitted_record == record
        assert schema["properties"]["publishedDate"]["format"] == "date"
        errors = list(Draft7Validator(schema, format_checker=FormatChecker()).iter_errors(emitted_record))
        assert errors == []
