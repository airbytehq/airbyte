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
    assert "property_metadata" in stream_names
    report_names = [name for name in stream_names if name != "property_metadata"]

    if single_stream_per_report:
        # One stream per report, each covering every property and suffixed `Consolidated`.
        assert len(report_names) == 59
        assert all(name.endswith("Consolidated") for name in report_names)
        assert "devicesConsolidated" in report_names

        stream = next(stream for stream in streams if stream.name == "first_reportConsolidated")
        partitions = list(stream.generate_partitions())
        assert [partition.to_slice()["property_id"] for partition in partitions] == ["111", "222"]
        assert all("start_time" in partition.to_slice() for partition in partitions)
    else:
        # One stream per report per property: the first property keeps the plain report name and
        # the rest get a `Property<id>` suffix.
        plain_names = [name for name in report_names if "Property" not in name]
        assert len(plain_names) == 59
        assert "devices" in plain_names
        assert "devicesProperty222" in report_names
        assert len(report_names) == len(plain_names) * 2


def test_enabling_the_flag_never_reuses_a_per_property_stream_name():
    """
    Destination tables and incremental state are both keyed by stream name, so a consolidated
    stream that reused `<report_name>` would look to the platform like a continuation of the
    single-property stream. It would inherit that stream's cursor -- which only ever tracked the
    FIRST property -- and every other property would resume from it rather than backfilling,
    silently losing history with no error. Distinct names force a full initial sync instead.

    `property_metadata` is the one intentional overlap: it is a static stream that already covers
    all properties and is identical in both modes.
    """
    per_property = {stream.name for stream in get_source(_config(False)).streams(config=_config(False))}
    consolidated = {stream.name for stream in get_source(_config(True)).streams(config=_config(True))}

    assert per_property & consolidated == {"property_metadata"}


# GA4 lets each property define its own custom metrics, so the metric fields in a stream's
# schema are property-specific. `customEvent:signup` exists ONLY on property 222 here.
_METRIC_ON_BOTH = "sessions"
_METRIC_ON_SECOND_PROPERTY_ONLY = "customEvent:signup"

_PROPERTY_METADATA = {
    "111": {"metrics": [{"apiName": _METRIC_ON_BOTH, "type": "TYPE_INTEGER"}]},
    "222": {
        "metrics": [
            {"apiName": _METRIC_ON_BOTH, "type": "TYPE_INTEGER"},
            {"apiName": _METRIC_ON_SECOND_PROPERTY_ONLY, "type": "TYPE_INTEGER"},
        ]
    },
}


def _union_config(single_stream_per_report):
    config = _BASE_CONFIG.copy()
    config["custom_reports_array"] = [
        {
            "name": "union_report",
            "dimensions": ["date"],
            "metrics": [_METRIC_ON_BOTH, _METRIC_ON_SECOND_PROPERTY_ONLY],
        }
    ]
    if single_stream_per_report:
        config["single_stream_per_report"] = True
    return config


def _schema_of(stream_name, config):
    with requests_mock.Mocker() as http_mocker:
        http_mocker.post(
            "https://www.googleapis.com/oauth2/v4/token",
            json={"access_token": "access-token", "expires_in": 3600},
        )
        for property_id, metadata in _PROPERTY_METADATA.items():
            http_mocker.get(
                f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}/metadata",
                json=metadata,
            )
        streams = get_source(config).streams(config=config)
        stream = next(stream for stream in streams if stream.name == stream_name)
        return stream.get_json_schema()["properties"]


def test_schema_is_unioned_across_properties():
    """
    A consolidated stream covers every property but has exactly one schema, and a field absent
    from the schema gets no destination column and is silently dropped. So the schema has to be
    the union across properties -- building it from a single property would lose every custom
    metric defined only on the others.
    """
    properties = _schema_of("union_reportConsolidated", _union_config(single_stream_per_report=True))

    assert _METRIC_ON_BOTH in properties
    assert _METRIC_ON_SECOND_PROPERTY_ONLY in properties, (
        f"{_METRIC_ON_SECOND_PROPERTY_ONLY} exists only on property 222. Its absence means the "
        "schema was built from one property, so that metric would have no destination column "
        "and its data would be dropped for every property that does report it."
    )
    # Dimensions and the injected columns are property-independent and must survive the merge.
    assert {"date", "property_id", "startDate", "endDate"} <= set(properties)


def test_schema_per_property_when_flag_disabled():
    """
    Control for test_schema_is_unioned_across_properties. With the flag off, each stream covers
    exactly one property, so its schema is that property's metrics only -- no union, and the
    per-property streams stay distinguishable. This is the pre-existing behavior and must not
    change.
    """
    config = _union_config(single_stream_per_report=False)

    first_property = _schema_of("union_report", config)
    assert _METRIC_ON_BOTH in first_property
    assert _METRIC_ON_SECOND_PROPERTY_ONLY not in first_property

    second_property = _schema_of("union_reportProperty222", config)
    assert _METRIC_ON_BOTH in second_property
    assert _METRIC_ON_SECOND_PROPERTY_ONLY in second_property


def test_metadata_is_fetched_once_per_property_not_once_per_stream():
    """
    One schema loader per property on every report stream would be 57 x N metadata requests if
    they were not cached. The CDK forces `use_cache=True` on dynamic schema loaders and shares
    the cache by URL across streams, so the real cost stays at one request per property.
    """
    config = _union_config(single_stream_per_report=True)

    with requests_mock.Mocker() as http_mocker:
        http_mocker.post(
            "https://www.googleapis.com/oauth2/v4/token",
            json={"access_token": "access-token", "expires_in": 3600},
        )
        for property_id, metadata in _PROPERTY_METADATA.items():
            http_mocker.get(
                f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}/metadata",
                json=metadata,
            )
        streams = get_source(config).streams(config=config)
        for stream in streams:
            stream.get_json_schema()

        metadata_requests = [request.path_url for request in http_mocker.request_history if request.path_url.endswith("/metadata")]

    assert sorted(set(metadata_requests)) == [
        "/v1beta/properties/111/metadata",
        "/v1beta/properties/222/metadata",
    ]
    assert len(metadata_requests) == len(set(metadata_requests)), (
        f"expected one request per property across all {len(streams)} streams, got "
        f"{len(metadata_requests)}: schema-loader caching is not being shared across streams"
    )


def test_single_stream_per_report_reads_each_property_partition():
    config = _config(single_stream_per_report=True)
    catalog = CatalogBuilder().with_stream("first_reportConsolidated", SyncMode.full_refresh).build()
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
        for property_id in config["property_ids"]:
            # Every property's metadata is fetched, not just the first: the schema is the
            # union across properties. See test_schema_is_unioned_across_properties.
            http_mocker.get(
                f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}/metadata",
                json=metadata_response,
            )
            http_mocker.post(
                f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport",
                json=report_response,
            )

        output = read(get_source(config), config, catalog)

    report_requests = [request for request in http_mocker.request_history if request.path_url.endswith(":runReport")]
    report_requests.sort(key=lambda request: request.path_url)
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
