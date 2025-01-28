# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import datetime
from typing import Any, Dict, Optional
from unittest import TestCase

from source_klaviyo import SourceKlaviyo

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    create_record_builder,
    create_response_builder,
    find_template,
)
from integration.config import KlaviyoConfigBuilder


_ENDPOINT_TEMPLATE_NAME = "profiles"
_START_DATE = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
_STREAM_NAME = "profiles"
_RECORDS_PATH = FieldPath("data")


def _config() -> KlaviyoConfigBuilder:
    return KlaviyoConfigBuilder().with_start_date(_START_DATE)


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()


def _a_profile_request(start_date: datetime) -> HttpRequest:
    return HttpRequest(
        url=f"https://a.klaviyo.com/api/profiles",
        query_params={
            "additional-fields[profile]": "predictive_analytics",
            "page[size]": "100",
            "filter": f"greater-than(updated,{start_date.strftime('%Y-%m-%dT%H:%M:%S%z')})",
            "sort": "updated",
        },
    )


def _a_profile() -> RecordBuilder:
    return create_record_builder(
        find_template(_ENDPOINT_TEMPLATE_NAME, __file__),
        _RECORDS_PATH,
        record_id_path=FieldPath("id"),
        record_cursor_path=NestedPath(["attributes", "updated"]),
    )


def _profiles_response() -> HttpResponseBuilder:
    return create_response_builder(
        find_template(_ENDPOINT_TEMPLATE_NAME, __file__),
        _RECORDS_PATH,
    )


def _read(
    config_builder: KlaviyoConfigBuilder, sync_mode: SyncMode, state: Optional[Dict[str, Any]] = None, expecting_exception: bool = False
) -> EntrypointOutput:
    catalog = _catalog(sync_mode)
    config = config_builder.build()
    return read(SourceKlaviyo(catalog, config, state), config, catalog, state, expecting_exception)


class FullRefreshTest(TestCase):
    @HttpMocker()
    def test_when_read_then_extract_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_profile_request(_START_DATE),
            _profiles_response().with_record(_a_profile()).build(),
        )

        output = _read(_config(), SyncMode.full_refresh)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_region_is_number_when_read_then_cast_as_string(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_profile_request(_START_DATE),
            _profiles_response().with_record(_a_profile().with_field(NestedPath(["attributes", "location", "region"]), 10)).build(),
        )

        output = _read(_config(), SyncMode.full_refresh)

        assert len(output.records) == 1
        assert isinstance(output.records[0].record.data["attributes"]["location"]["region"], str)
