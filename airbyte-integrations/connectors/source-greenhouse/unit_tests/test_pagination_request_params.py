# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


def test_incremental_pagination_request_parameters(manifest_path, components_module):
    sys.modules["components"] = components_module
    source = YamlDeclarativeSource(str(manifest_path), config={"api_key": "test"})
    applications = next(stream for stream in source.streams(config={"api_key": "test"}) if stream.name == "applications")
    stream_slice = next(
        iter(
            applications.stream_slices(
                sync_mode=SyncMode.incremental,
                cursor_field=["applied_at"],
                stream_state={},
            )
        )
    )

    next_url = "https://harvest.greenhouse.io/v1/applications?cursor=ABC&foo=bar"
    first_request = HttpRequest(
        "https://harvest.greenhouse.io/v1/applications",
        query_params={
            "per_page": "100",
            "created_after": "1970-01-01T00:00:00.000Z",
        },
    )
    second_request = HttpRequest(next_url)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            first_request,
            HttpResponse(
                '[{"id": 1, "applied_at": "1970-01-01T00:00:00.000Z"}]',
                headers={"Link": f'<{next_url}>; rel="next"'},
            ),
        )
        http_mocker.get(
            second_request,
            HttpResponse('[{"id": 2, "applied_at": "1970-01-01T00:00:01.000Z"}]'),
        )
        records = list(
            applications.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=stream_slice,
            )
        )
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    assert [dict(record) for record in records] == [
        {"id": 1, "applied_at": "1970-01-01T00:00:00.000Z"},
        {"id": 2, "applied_at": "1970-01-01T00:00:01.000Z"},
    ]
