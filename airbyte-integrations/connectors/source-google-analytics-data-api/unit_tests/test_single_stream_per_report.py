#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json

import pytest
import requests_mock

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from unit_tests.conftest import get_source


_BASE_CONFIG = {
    "credentials": {
        "auth_type": "Client",
        "client_id": "client-id",
        "client_secret": "client-secret",
        "refresh_token": "refresh-token",
    },
    "date_ranges_start_date": "2025-01-01",
    "date_ranges_end_date": "2025-01-01",
    "window_in_days": 1,
    "property_ids": ["111", "222"],
}


def _config(single_stream_per_report=False):
    config = _BASE_CONFIG.copy()
    config["custom_reports_array"] = [
        {"name": "first_report", "dimensions": ["date"], "metrics": ["sessions"]},
        {"name": "second_report", "dimensions": ["date"], "metrics": ["sessions"]},
    ]
    if single_stream_per_report:
        config["single_stream_per_report"] = True
    return config


@pytest.mark.parametrize(
    "single_stream_per_report",
    [
        pytest.param(False, id="one_stream_per_property"),
        pytest.param(True, id="one_stream_per_report"),
    ],
)
def test_stream_names(single_stream_per_report):
    config = _config(single_stream_per_report)
    streams = get_source(config).streams(config=config)
    stream_names = [stream.name for stream in streams]
    report_names = [name for name in stream_names if "Property" not in name]

    assert len(report_names) == 59
    assert "devices" in report_names
    if single_stream_per_report:
        assert "devicesProperty222" not in stream_names
    else:
        assert "devicesProperty222" in stream_names
    assert len(stream_names) == len(report_names) * (1 if single_stream_per_report else 2)
    if single_stream_per_report:
        stream = next(stream for stream in streams if stream.name == "first_report")
        partitions = list(stream.generate_partitions())
        assert [partition.to_slice()["property_id"] for partition in partitions] == ["111", "222"]
        assert all("start_time" in partition.to_slice() for partition in partitions)


def test_single_stream_per_report_reads_each_property_partition():
    config = _config(single_stream_per_report=True)
    catalog = CatalogBuilder().with_stream("first_report", SyncMode.full_refresh).build()
    metadata_response = {"metrics": [{"apiName": "sessions", "type": "TYPE_INTEGER"}]}
    report_response = {
        "dimensionHeaders": [{"name": "date"}],
        "metricHeaders": [{"name": "sessions", "type": "TYPE_INTEGER"}],
        "rows": [{"dimensionValues": [{"value": "20250101"}], "metricValues": [{"value": "7"}]}],
    }

    with requests_mock.Mocker() as http_mocker:
        http_mocker.post(
            "https://www.googleapis.com/oauth2/v4/token",
            json={"access_token": "access-token", "expires_in": 3600},
        )
        http_mocker.get(
            "https://analyticsdata.googleapis.com/v1beta/properties/111/metadata",
            json=metadata_response,
        )
        for property_id in config["property_ids"]:
            http_mocker.post(
                f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport",
                json=report_response,
            )

        output = read(get_source(config), config, catalog)

    report_requests = [request for request in http_mocker.request_history if request.path_url.endswith(":runReport")]
    assert [request.path_url for request in report_requests] == [
        "/v1beta/properties/111:runReport",
        "/v1beta/properties/222:runReport",
    ]
    assert [request.json() for request in report_requests] == [
        {
            "dimensions": [{"name": "date"}],
            "metrics": [{"name": "sessions"}],
            "returnPropertyQuota": True,
            "keepEmptyRows": False,
            "limit": 100000,
            "dateRanges": [{"startDate": "2025-01-01", "endDate": "2025-01-01"}],
        }
    ] * 2
    assert sorted(record.record.data["property_id"] for record in output.records) == ["111", "222"]
