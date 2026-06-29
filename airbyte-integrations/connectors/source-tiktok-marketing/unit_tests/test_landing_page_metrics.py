# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from urllib.parse import parse_qs, urlparse

import pytest
import requests_mock as rm
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder

from .conftest import _YAML_FILE_PATH


LANDING_PAGE_METRICS = [
    "total_landing_page_view",
    "cost_per_landing_page_view",
    "landing_page_view_rate",
]


def _load_manifest():
    with open(_YAML_FILE_PATH) as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "retriever_key",
    [
        pytest.param("base_report_retriever", id="daily_retriever"),
        pytest.param("base_report_hourly_retriever", id="hourly_retriever"),
    ],
)
def test_landing_page_metrics_in_retriever_templates(retriever_key):
    manifest = _load_manifest()
    retriever = manifest["definitions"][retriever_key]
    metrics_template = retriever["requester"]["request_parameters"]["metrics"]
    for metric in LANDING_PAGE_METRICS:
        assert metric in metrics_template, f"{metric} missing from {retriever_key} metrics template"


def test_landing_page_metrics_in_lifetime_retriever():
    manifest = _load_manifest()
    lifetime_def = manifest["definitions"]["base_report_lifetime"]
    metrics_template = lifetime_def["retriever"]["requester"]["request_parameters"]["metrics"]
    for metric in LANDING_PAGE_METRICS:
        assert metric in metrics_template, f"{metric} missing from base_report_lifetime metrics template"


@pytest.mark.parametrize(
    "schema_key",
    [
        pytest.param("base_report", id="base_report_schema"),
        pytest.param("base_report_by_country", id="base_report_by_country_schema"),
    ],
)
def test_landing_page_metrics_in_schemas(schema_key):
    manifest = _load_manifest()
    metric_props = manifest["definitions"]["schemas"][schema_key]["properties"]["metrics"]["properties"]
    for metric in LANDING_PAGE_METRICS:
        assert metric in metric_props, f"{metric} missing from {schema_key} schema properties"
        prop = metric_props[metric]
        assert "null" in prop["type"], f"{metric} should be nullable"
        assert "string" in prop["type"], f"{metric} should have string type"


@pytest.mark.parametrize(
    "stream_name",
    [
        pytest.param("ads_reports_daily", id="ads_daily"),
        pytest.param("ad_groups_reports_daily", id="ad_groups_daily"),
        pytest.param("campaigns_reports_daily", id="campaigns_daily"),
    ],
)
def test_landing_page_metrics_in_api_request(stream_name):
    config = {
        "access_token": "TOKEN",
        "start_date": "2024-01-01",
        "end_date": "2024-01-03",
        "environment": {"advertiser_id": "12345"},
    }

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=[])

    with rm.Mocker() as m:
        m.get(
            "https://business-api.tiktok.com/open_api/v1.3/report/integrated/get/",
            json={
                "code": 0,
                "message": "ok",
                "data": {
                    "list": [],
                    "page_info": {"page": 1, "page_size": 1000, "total_page": 1, "total_number": 0},
                },
            },
        )
        list(source.read(logger=None, config=config, catalog=catalog, state=[]))

        report_requests = [h for h in m.request_history if "report/integrated/get" in h.path]
        assert len(report_requests) > 0, f"Expected at least one report API request for {stream_name}"

        for req in report_requests:
            params = parse_qs(urlparse(req.url).query)
            metrics_str = params.get("metrics", [""])[0]
            for metric in LANDING_PAGE_METRICS:
                assert metric in metrics_str, f"{metric} not found in {stream_name} API request metrics parameter"
