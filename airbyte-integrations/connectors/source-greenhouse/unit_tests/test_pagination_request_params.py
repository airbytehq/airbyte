# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from contextlib import nullcontext
from unittest.mock import patch

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    ("stream_name", "path", "partition", "cursor_field", "cursor_parameter", "cursor_value"),
    [
        (
            "applications",
            "applications",
            {},
            "applied_at",
            "created_after",
            "1970-01-01T00:00:00.000Z",
        ),
        (
            "applications_interviews",
            "applications/123/scheduled_interviews",
            {"application_id": 123},
            "updated_at",
            "updated_after",
            "2024-01-02T03:04:05.678Z",
        ),
    ],
)
def test_incremental_pagination_request_parameters(
    manifest_path,
    components_module,
    stream_name,
    path,
    partition,
    cursor_field,
    cursor_parameter,
    cursor_value,
):
    sys.modules["components"] = components_module
    source = YamlDeclarativeSource(str(manifest_path), config={"api_key": "test"})
    stream = next(stream for stream in source.streams(config={"api_key": "test"}) if stream.name == stream_name)
    stream_slice = (
        next(
            iter(
                stream.stream_slices(
                    sync_mode=SyncMode.incremental,
                    cursor_field=[cursor_field],
                    stream_state={},
                )
            )
        )
        if not partition
        else StreamSlice(
            partition=partition,
            cursor_slice={
                "start_time": cursor_value,
                "end_time": "2024-01-03T03:04:05.678Z",
            },
        )
    )

    next_url = f"https://harvest.greenhouse.io/v1/{path}?cursor=ABC&foo=bar"
    first_request = HttpRequest(
        f"https://harvest.greenhouse.io/v1/{path}",
        query_params={
            "per_page": "100",
            cursor_parameter: cursor_value,
        },
    )
    second_request = HttpRequest(next_url)
    cursor_context = patch.object(stream.retriever, "cursor", None) if partition else nullcontext()
    with cursor_context:
        with HttpMocker() as http_mocker:
            http_mocker.get(
                first_request,
                HttpResponse(
                    json.dumps([{"id": 1, cursor_field: cursor_value}]),
                    headers={"Link": f'<{next_url}>; rel="next"'},
                ),
            )
            http_mocker.get(
                second_request,
                HttpResponse(json.dumps([{"id": 2, cursor_field: "2024-01-03T03:04:05.678Z"}])),
            )
            records = list(
                stream.read_records(
                    sync_mode=SyncMode.incremental,
                    stream_slice=stream_slice,
                )
            )
            http_mocker.assert_number_of_calls(first_request, 1)
            http_mocker.assert_number_of_calls(second_request, 1)

    assert [dict(record) for record in records] == [
        {"id": 1, cursor_field: cursor_value},
        {"id": 2, cursor_field: "2024-01-03T03:04:05.678Z"},
    ]
