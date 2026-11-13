# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""
Mock server tests pinning that PrestaShop records are emitted exactly as returned by the API.

The manifest previously attached a `CustomFieldTransformation` to every stream. Since the
manifest-only migration it never received a stream name, so it never altered records
(zero dates such as `0000-00-00 00:00:00` were passed through). The component was removed;
these tests guard that records, including zero-date values, keep being emitted unchanged.
"""

import json
from typing import Any, Dict

import pytest
from freezegun import freeze_time
from unit_tests.conftest import _YAML_FILE_PATH, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"access_key": "key", "url": "https://shop.example.com", "start_date": "2025-01-01"}
_API_URL = "https://shop.example.com/api"


def _address() -> Dict[str, Any]:
    return {
        "id": 1,
        "id_customer": "2",
        "alias": "home",
        "date_add": "0000-00-00 00:00:00",
        "date_upd": "2025-06-01 10:00:00",
    }


def _carrier() -> Dict[str, Any]:
    return {"id": 3, "name": "carrier", "deleted": "0", "date_add": "0000-00-00", "unexpected_zero_date": "0000-00-00 00:00:00"}


def _limit(offset: int) -> str:
    return f"{offset},50"


@pytest.mark.parametrize(
    "stream_name,sync_mode,requests,record",
    [
        pytest.param(
            "addresses",
            SyncMode.incremental,
            [
                {
                    "display": "full",
                    "limit": _limit(0),
                    "date": "1",
                    "sort": "[date_upd_ASC,id_ASC]",
                    "filter[date_upd]": "[2025-01-01 00:00:00,2025-12-31 23:59:59]",
                },
                {
                    "display": "full",
                    "limit": _limit(0),
                    "date": "1",
                    "sort": "[date_upd_ASC,id_ASC]",
                    "filter[date_upd]": "[2026-01-01 00:00:00,2026-10-06 12:00:00]",
                },
            ],
            _address(),
            id="incremental_stream",
        ),
        pytest.param(
            "carriers",
            SyncMode.full_refresh,
            [{"display": "full", "limit": _limit(0)}],
            _carrier(),
            id="full_refresh_stream",
        ),
    ],
)
@freeze_time("2026-10-06 12:00:00.123456")
def test_records_are_emitted_unchanged(stream_name, sync_mode, requests, record):
    with HttpMocker() as http_mocker:
        for query_params in requests:
            http_mocker.get(
                HttpRequest(f"{_API_URL}/{stream_name}", query_params=query_params),
                HttpResponse(json.dumps({stream_name: [record]}), 200),
            )
        catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
        output = read(get_source(config=_CONFIG), config=_CONFIG, catalog=catalog)

    assert output.errors == []
    assert [message.record.data for message in output.records] == [record] * len(requests)


def test_manifest_has_no_custom_components():
    manifest = _YAML_FILE_PATH.read_text()
    assert "CustomTransformation" not in manifest
    assert "source_declarative_manifest.components" not in manifest
    assert not (_YAML_FILE_PATH.parent / "components.py").exists()
