# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from collections import namedtuple

import pytest
from source_google_ads.components import CustomGAQuerySchemaLoader

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.mock_server.config import ConfigBuilder
from unit_tests.mock_server.conftest import create_source
from unit_tests.mock_server.helpers import (
    API_BASE,
    build_error_response,
    build_full_refresh_query,
    build_google_ads_query_error_response,
    build_stream_response,
    setup_full_refresh_parent_mocks,
)


_CUSTOMER_ID = "1234567890"
_CUSTOM_QUERY = "SELECT asset_group_asset.asset, asset_group_asset.performance_label FROM asset_group_asset"
_CUSTOM_QUERY_STREAM = "asset_group_asset_report"

_STREAM_RECORDS = {
    "label": {
        "customer": {"id": _CUSTOMER_ID},
        "label": {
            "id": "100001",
            "name": "Test Label",
            "resourceName": "customers/1234567890/labels/100001",
            "status": "ENABLED",
            "textLabel": {
                "backgroundColor": "#ffffff",
                "description": "desc",
            },
        },
    },
    "audience": {
        "customer": {"id": _CUSTOMER_ID},
        "audience": {
            "id": "200001",
            "name": "Test Audience",
            "description": "desc",
            "resourceName": "customers/1234567890/audiences/200001",
            "status": "ENABLED",
        },
    },
    "customer_label": {
        "customerLabel": {
            "resourceName": "customers/1234567890/customerLabels/300001",
            "customer": "customers/1234567890",
            "label": "customers/1234567890/labels/100001",
        },
        "customer": {"id": _CUSTOMER_ID},
    },
    "ad_group_label": {
        "adGroup": {"id": "400001", "resourceName": "customers/1234567890/adGroups/400001"},
        "label": {"id": "100001", "name": "Test Label"},
        "adGroupLabel": {"resourceName": "customers/1234567890/adGroupLabels/400001~100001"},
    },
    "ad_group_ad_label": {
        "adGroup": {"id": "400001"},
        "adGroupAd": {
            "ad": {
                "id": "500001",
                "resourceName": "customers/1234567890/ads/500001",
            },
        },
        "adGroupAdLabel": {"resourceName": "customers/1234567890/adGroupAdLabels/400001~500001~100001"},
        "label": {"name": "Test Label"},
    },
    "ad_group_criterion_label": {
        "adGroup": {"id": "400001"},
        "label": {"id": "100001"},
        "adGroupCriterionLabel": {
            "adGroupCriterion": "customers/1234567890/adGroupCriteria/400001~600001",
            "label": "customers/1234567890/labels/100001",
            "resourceName": "customers/1234567890/adGroupCriterionLabels/400001~600001~100001",
        },
    },
    "campaign_label": {
        "campaign": {"id": "700001", "resourceName": "customers/1234567890/campaigns/700001"},
        "label": {"id": "100001", "name": "Test Label"},
        "campaignLabel": {"resourceName": "customers/1234567890/campaignLabels/700001~100001"},
    },
    "user_interest": {
        "userInterest": {
            "name": "Test Interest",
            "resourceName": "customers/1234567890/userInterests/800001",
            "taxonomyType": "AFFINITY",
            "userInterestId": "800001",
            "launchedToAll": True,
        },
    },
}

_KEY_FIELD_CHECKS = {
    "label": ("label.id", 100001),
    "audience": ("audience.id", 200001),
    "customer_label": ("customer_label.resource_name", "customers/1234567890/customerLabels/300001"),
    "ad_group_label": ("ad_group.id", 400001),
    "ad_group_ad_label": ("ad_group.id", 400001),
    "ad_group_criterion_label": ("ad_group.id", 400001),
    "campaign_label": ("campaign.id", 700001),
    "user_interest": ("user_interest.name", "Test Interest"),
}

FULL_REFRESH_STREAMS = [
    "label",
    "audience",
    "customer_label",
    "ad_group_label",
    "ad_group_ad_label",
    "ad_group_criterion_label",
    "campaign_label",
    "user_interest",
]


@pytest.fixture
def mock_custom_query_schema_loader(mocker):
    data_type = namedtuple("DataType", ["name"])
    node = namedtuple("Node", ["data_type", "enum_values", "is_repeated"])
    fields_metadata = {
        "asset_group_asset.asset": node(data_type("STRING"), [], False),
        "asset_group_asset.performance_label": node(data_type("ENUM"), ["UNSPECIFIED", "UNKNOWN", "BEST"], False),
    }
    mocker.patch.object(
        CustomGAQuerySchemaLoader,
        "google_ads_client",
        return_value=mocker.Mock(get_fields_metadata=lambda fields: fields_metadata),
    )


def _read_custom_query(response):
    config = ConfigBuilder().with_custom_queries([{"query": _CUSTOM_QUERY, "table_name": _CUSTOM_QUERY_STREAM}]).build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": _CUSTOM_QUERY}),
            ),
            response,
        )

        catalog = CatalogBuilder().with_stream(_CUSTOM_QUERY_STREAM, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        return read(source, config=config, catalog=catalog)


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in FULL_REFRESH_STREAMS],
)
def test_full_refresh_read(stream_name):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            build_stream_response([_STREAM_RECORDS[stream_name]]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 1
    record = output.records[0].record.data
    key_field, expected_value = _KEY_FIELD_CHECKS[stream_name]
    assert record[key_field] == expected_value


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in FULL_REFRESH_STREAMS],
)
def test_full_refresh_empty(stream_name):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            build_stream_response([]),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0


@pytest.mark.parametrize(
    "stream_name",
    [pytest.param(s, id=s) for s in FULL_REFRESH_STREAMS],
)
def test_full_refresh_403_ignored(stream_name):
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            HttpResponse(
                body=json.dumps({"error": {"code": 403, "message": "Permission denied"}}),
                status_code=403,
            ),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert len(output.records) == 0


@pytest.mark.parametrize("wrap_in_list", [True, False], ids=["list-wrapped", "object-wrapped"])
def test_custom_query_400_fails_as_config_error_with_google_message(wrap_in_list, mock_custom_query_schema_loader):
    output = _read_custom_query(
        build_google_ads_query_error_response(
            query_error="UNRECOGNIZED_FIELD",
            message="Unrecognized field in the query: 'asset_group_asset.performance_label'.",
            wrap_in_list=wrap_in_list,
        )
    )

    assert not output.records
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type.value == "config_error"
    assert (
        error.message
        == "Google Ads rejected the custom query for stream 'asset_group_asset_report': Unrecognized field in the query: 'asset_group_asset.performance_label'. Correct or remove the invalid field or clause in the custom query configuration."
    )


def test_custom_query_400_without_details_falls_back_to_error_message(mock_custom_query_schema_loader):
    output = _read_custom_query(build_error_response(400, "Request contains an invalid argument."))

    assert not output.records
    assert output.errors
    error = output.errors[0].trace.error
    assert error.failure_type.value == "config_error"
    assert (
        error.message
        == "Google Ads rejected the custom query for stream 'asset_group_asset_report': Request contains an invalid argument. Correct or remove the invalid field or clause in the custom query configuration."
    )


def test_custom_query_successful_response_body_not_parsed_by_error_handler(mocker, mock_custom_query_schema_loader):
    from airbyte_cdk.sources.declarative.requesters.error_handlers.http_response_filter import HttpResponseFilter

    spy = mocker.spy(HttpResponseFilter, "_safe_response_json")
    output = _read_custom_query(
        build_stream_response(
            [
                {
                    "assetGroupAsset": {
                        "asset": "customers/1234567890/assets/1",
                        "performanceLabel": "BEST",
                    }
                }
            ]
        )
    )

    assert len(output.records) == 1
    assert spy.call_count == 0


def test_builtin_stream_400_remains_system_error():
    stream_name = "label"
    config = ConfigBuilder().build()
    with HttpMocker() as http_mocker:
        setup_full_refresh_parent_mocks(http_mocker)
        http_mocker.post(
            HttpRequest(
                url=f"{API_BASE}/customers/{_CUSTOMER_ID}/googleAds:searchStream",
                body=json.dumps({"query": build_full_refresh_query(stream_name)}),
            ),
            build_google_ads_query_error_response(
                query_error="UNRECOGNIZED_FIELD",
                message="Unrecognized field in the query: 'asset_group_asset.performance_label'.",
            ),
        )

        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        source = create_source(config=config, catalog=catalog)
        output = read(source, config=config, catalog=catalog)

    assert not output.records
    assert output.errors
    assert output.errors[0].trace.error.failure_type.value == "system_error"
