# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import freezegun
import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from mock_server.config import ADVERTISER_ID, BASE_URL, ConfigBuilder


_DAY_PARAMS = {"startDate": "2024-01-01", "endDate": "2024-01-01", "dateType": "transaction", "timezone": "UTC"}


@freezegun.freeze_time("2024-01-01T12:00:00Z")
@pytest.mark.parametrize(
    "stream, regions, responses",
    [
        pytest.param(
            "publisher_performance",
            [],
            [
                (
                    "reports/publisher",
                    {},
                    [
                        {"publisherId": 777, "region": "GB", "currency": "GBP", "clicks": 1},
                        {"publisherId": 777, "region": "DE", "currency": "EUR", "clicks": 2},
                    ],
                )
            ],
            id="publisher_performance",
        ),
        pytest.param(
            "creative_performance",
            ["GB", "US"],
            [
                ("reports/creative", {"region": region}, [{"creativeId": 1, "publisherId": 777, "region": region, "clicks": 1}])
                for region in ("GB", "US")
            ],
            id="creative_performance",
        ),
    ],
)
def test_rows_that_differ_only_by_region_keep_distinct_primary_keys(stream, regions, responses) -> None:
    config = ConfigBuilder().with_regions(regions).build()
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    with HttpMocker() as http_mocker:
        for path, extra_params, body in responses:
            http_mocker.get(
                HttpRequest(url=f"{BASE_URL}/advertisers/{ADVERTISER_ID}/{path}", query_params={**_DAY_PARAMS, **extra_params}),
                HttpResponse(body=json.dumps(body), status_code=200),
            )
        output = read(get_source(config=config, catalog=catalog), config, catalog)

    primary_key = next(
        s.source_defined_primary_key for s in discover(get_source(config=config), config).catalog.catalog.streams if s.name == stream
    )
    keys = [tuple(record.record.data.get(field[0]) for field in primary_key) for record in output.records]
    assert not output.errors
    assert len(keys) == 2
    assert len(set(keys)) == 2
    assert all(None not in key for key in keys)
