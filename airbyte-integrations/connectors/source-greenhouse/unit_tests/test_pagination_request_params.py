# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from urllib.parse import quote

import pytest

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize(
    ("stream_name", "path", "partition", "cursor_field", "cursor_parameter"),
    [
        (
            "applications",
            "applications",
            {},
            "applied_at",
            "created_after",
        ),
        (
            "applications_interviews",
            "applications/123/scheduled_interviews",
            {"application_id": 123},
            "updated_at",
            "updated_after",
        ),
    ],
)
def test_incremental_pagination_request_parameters(
    manifest_path,
    components_module,
    monkeypatch,
    stream_name,
    path,
    partition,
    cursor_field,
    cursor_parameter,
):
    monkeypatch.setitem(sys.modules, "components", components_module)
    source = YamlDeclarativeSource(str(manifest_path), config={"api_key": "test"})
    stream = next(stream for stream in source.streams(config={"api_key": "test"}) if stream.name == stream_name)
    cursor_value = "1970-01-01T00:00:00.000Z"

    next_url = f"https://harvest.greenhouse.io/v1/{path}?cursor=ABC&foo=bar"
    first_request = HttpRequest(
        f"https://harvest.greenhouse.io/v1/{path}",
        query_params={
            "per_page": "100",
            cursor_parameter: cursor_value,
        },
    )
    second_request = HttpRequest(f"{next_url}&{cursor_parameter}={quote(cursor_value, safe='')}")
    parent_request = HttpRequest(
        "https://harvest.greenhouse.io/v1/applications",
        query_params={
            "per_page": "100",
            "created_after": cursor_value,
        },
    )
    with HttpMocker() as http_mocker:
        if partition:
            http_mocker.get(
                parent_request,
                HttpResponse(json.dumps([{"id": partition["application_id"], "applied_at": cursor_value}])),
            )
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
        partitions = list(stream.generate_partitions())
        assert len(partitions) == 1
        records = list(partitions[0].read())
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)
        if partition:
            http_mocker.assert_number_of_calls(parent_request, 1)

    assert [dict(record) for record in records] == [
        {"id": 1, cursor_field: cursor_value},
        {"id": 2, cursor_field: "2024-01-03T03:04:05.678Z"},
    ]
