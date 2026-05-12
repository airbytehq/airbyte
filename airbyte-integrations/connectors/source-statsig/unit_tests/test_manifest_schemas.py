# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


@pytest.fixture(scope="module")
def schemas():
    return yaml.safe_load(MANIFEST_PATH.read_text())["schemas"]


@pytest.mark.parametrize(
    ("stream_name", "expected_fields"),
    [
        pytest.param(
            "events",
            {"timestamp", "name", "source", "value", "userID"},
            id="events",
        ),
        pytest.param(
            "events_metrics",
            {
                "id",
                "name",
                "directionality",
                "type",
                "tags",
                "createdTime",
                "lastModifiedTime",
                "lineage",
                "permalink",
            },
            id="events_metrics",
        ),
        pytest.param(
            "ingestion_status",
            {
                "ds",
                "ingestion_dataset",
                "ingestion_source",
                "source_name",
                "message",
                "error_message",
                "status",
                "rowCount",
                "metricCount",
                "timestamp",
            },
            id="ingestion_status",
        ),
        pytest.param(
            "ingestion_runs",
            {
                "runID",
                "latestStatus",
                "lastUpdatedAt",
                "createdAt",
                "trigger",
                "sources",
                "dateStamps",
                "runHistory",
                "granularHistory",
            },
            id="ingestion_runs",
        ),
        pytest.param(
            "metrics_values",
            {
                "value",
                "unitType",
                "numerator",
                "denominator",
                "inputRows",
                "metricName",
                "metricType",
                "displayName",
            },
            id="metrics_values",
        ),
    ],
)
def test_statsig_stream_schemas_include_documented_fields(schemas, stream_name, expected_fields):
    properties = schemas[stream_name]["properties"]

    assert properties
    assert expected_fields <= properties.keys()
