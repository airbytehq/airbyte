# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Mapping, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import AirbyteStateBlob, AirbyteStreamState, ConfiguredAirbyteCatalog, FailureType, StreamDescriptor, SyncMode
from source_survey_monkey_demo import SourceSurveyMonkeyDemo

_A_CONFIG = {
    "access_token": "1234",
    "start_date": "2021-01-01T00:00:00Z",
}
_NOW = datetime.now(timezone.utc)

@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    @HttpMocker()
    def test_read_a_single_page(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            HttpRequest(url="https://api.surveymonkey.com/v3/surveys?per_page=100"),
            HttpResponse(body="""
            {
  "data": [
    {
      "id": "1234",
      "title": "My Survey",
      "nickname": "",
      "href": "https://api.surveymonkey.com/v3/surveys/1234"
    }
  ],
  "per_page": 100,
  "page": 1,
  "total": 1,
  "links": {
    "self": "https://api.surveymonkey.com/v3/surveys?page=1&per_page=100"
  }
}
""", status_code=200)
        )

        output = self._read(_A_CONFIG, _configured_catalog("surveys", SyncMode.full_refresh))

        assert len(output.records) == 1

    def _read(self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, configured_catalog=configured_catalog, expecting_exception=expecting_exception)

    @HttpMocker()
    def test_read_multiple_pages(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            HttpRequest(url="https://api.surveymonkey.com/v3/surveys?per_page=100"),
            HttpResponse(body="""
            {
    "data": [
    {
        "id": "1234",
        "title": "My Survey",
        "nickname": "",
        "href": "https://api.surveymonkey.com/v3/surveys/1234"
    }
    ],
    "per_page": 100,
    "page": 1,
    "total": 2,
    "links": {
    "self": "https://api.surveymonkey.com/v3/surveys?page=1&per_page=100",
    "next": "https://api.surveymonkey.com/v3/surveys?page=2&per_page=100"
    }
    }
    """, status_code=200)
        )

        http_mocker.get(
            HttpRequest(url="https://api.surveymonkey.com/v3/surveys?page=2&per_page=100"),
            HttpResponse(body="""
            {
    "data": [
    {
        "id": "5678",
        "title": "My Survey",
        "nickname": "",
        "href": "https://api.surveymonkey.com/v3/surveys/5678"
    }
    ],
    "per_page": 100,
    "page": 2,
    "total": 2,
    "links": {
    "self": "https://api.surveymonkey.com/v3/surveys?page=2&per_page=50"
    }
    }
    """, status_code=200)
        )

        output = self._read(_A_CONFIG, _configured_catalog("surveys", SyncMode.full_refresh))

        assert len(output.records) == 2
  
def _read(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    return read(_source(configured_catalog, config, state), config, configured_catalog, state, expecting_exception)


def _configured_catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceSurveyMonkeyDemo:
    return SourceSurveyMonkeyDemo()