# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Test source-linear relationship flattening transformations."""

from __future__ import annotations

from typing import Any, Mapping

import pytest
from test_substreams import CONFIG, MANIFEST_PATH, _connection_response, _request, _request_body

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        pytest.param(
            {
                "id": "initiative-1",
                "creator": {"id": "user-1"},
                "owner": {"id": "user-2"},
                "parentInitiative": {"id": "parent-1"},
            },
            {"creatorId": "user-1", "ownerId": "user-2", "parentInitiativeId": "parent-1"},
            id="relationships-present",
        ),
        pytest.param(
            {"id": "initiative-2", "creator": None, "owner": None, "parentInitiative": None},
            {"creatorId": None, "ownerId": None, "parentInitiativeId": None},
            id="relationships-null",
        ),
    ],
)
def test_initiatives_flatten_nullable_relationships(
    response: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    source = YamlDeclarativeSource(path_to_yaml=MANIFEST_PATH, config=CONFIG)
    stream = {stream.name: stream for stream in source.streams(config=CONFIG)}["initiatives"]
    request = _request(_request_body(stream))

    with HttpMocker() as http_mocker:
        http_mocker.post(request, _connection_response("initiatives", [response]))

        output = read(
            source,
            config=CONFIG,
            catalog=CatalogBuilder().with_stream("initiatives", SyncMode.full_refresh).build(),
        )

    assert len(output.records) == 1
    record = output.records[0].record.data
    assert {field: record.get(field) for field in expected} == expected
