import json
import os
from logging import Logger
from pathlib import Path
from typing import Mapping, Any
from unittest import TestCase
from unittest.mock import Mock

import requests_mock
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.utils.slice_logger import SliceLogger

from source_stripe import SourceStripe


class CatalogBuilder:
    def __init__(self) -> None:
        self._streams = []

    def with_stream(self, name: str, sync_mode: SyncMode) -> "CatalogBuilder":
        self._streams.append({
            "stream": {
                "name": name,
                "json_schema": {},
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_primary_key": [["id"]]
            },
            "primary_key": [["id"]],
            "sync_mode": sync_mode.name,
            "destination_sync_mode": "overwrite"
        })
        return self

    def build(self) -> ConfiguredAirbyteCatalog:
        return ConfiguredAirbyteCatalog.parse_obj({"streams": self._streams})


class RecordBuilder:
    @classmethod
    def from_file(cls, template_path: str) -> "RecordBuilder":
        with open(template_path, "r") as template_file:
            return RecordBuilder(json.load(template_file))

    def __init__(self, template: dict):
        self._record = template

    def with_id(self, identifier: Any) -> "RecordBuilder":
        self._record["id"] = identifier
        return self

    def build(self) -> dict:
        return self._record


class ResponseBuilder:
    # Long shot comment:
    # This implementation is specific to stripe but I don't see a reason why this couldn't be an interface that we ask sources to create
    # implementation to that our test framework can leverage this. The same applies for RecordBuilder where we could configure domain level
    # important fields like id, cursor_field, etc...
    @classmethod
    def from_file(cls, template_path: str) -> "ResponseBuilder":
        with open(template_path, "r") as template_file:
            return ResponseBuilder(template_file.read())

    def __init__(self, template: str):
        self._records = []
        self._response = template
        self._has_next_page = False

    def with_record(self, record: RecordBuilder) -> "ResponseBuilder":
        self._records.append(record)
        return self

    def with_pagination(self) -> "ResponseBuilder":
        # I'm wondering if we also need to have something on top of ResponseBuilder to coordinate the multiple responses involved in the
        # pagination
        self._has_next_page = True
        return self

    def build_json(self) -> dict:
        self._response = self._response.replace("%RECORDS%", f"[{'.'.join(map(lambda builder: json.dumps(builder.build()), self._records))}]")
        json_response = json.loads(self._response)
        if self._has_next_page:
            json_response["has_more"] = True
        return json_response


_CONFIG = {"client_secret": "client_secret", "account_id": "account_id", "start_date": "2023-09-28T20:15:00Z"}
_NO_STATE = {}
_RESPONSE_TEMPLATE_PATH = Path(__file__).parent / "response"


class FullRefreshAccountStream(TestCase):

    def setUp(self) -> None:
        self._logger = Mock(spec=Logger)
        self._slice_logger = Mock(spec=SliceLogger)
        # TODO clean cache
        # something like: os.remove(Path(__file__).parent / os.getenv(ENV_REQUEST_CACHE_PATH) / account_stream.cache_filename)

    def source(self) -> SourceStripe:
        return SourceStripe(_NO_STATE, CatalogBuilder().with_stream("accounts", SyncMode.full_refresh).build())

    @requests_mock.Mocker()
    def test_given_one_page_when_read_then_return_record(self, requests_mocker) -> None:
        requests_mocker.get(
            "https://api.stripe.com/v1/accounts?limit=100",
            json=self._a_response().with_record(self._a_record()).build_json()
        )
        account_stream = self.source().streams(_CONFIG)[0]
        records = self._records(account_stream)
        assert len(records) == 1

    @requests_mock.Mocker()
    def test_given_two_pages_when_read_then_return_records(self, requests_mocker) -> None:
        requests_mocker.get(
            "https://api.stripe.com/v1/accounts?limit=100",
            json=self._a_response().with_pagination().with_record(self._a_record().with_id("last_page_record_id")).build_json()
        )
        requests_mocker.get(
            "https://api.stripe.com/v1/accounts?starting_after=last_page_record_id&limit=100",
            json=self._a_response().with_record(self._a_record()).build_json()
        )
        account_stream = self.source().streams(_CONFIG)[0]
        records = self._records(account_stream)
        assert len(records) == 2

    def _a_response(self):
        return ResponseBuilder.from_file(os.path.join(_RESPONSE_TEMPLATE_PATH, "accounts_response_template.txt"))

    def _a_record(self):
        return RecordBuilder.from_file(os.path.join(_RESPONSE_TEMPLATE_PATH, "accounts_record_template.txt"))

    def _records(self, stream):
        return list(message for message in stream.read_full_refresh(None, self._logger, self._slice_logger) if isinstance(message, Mapping))
