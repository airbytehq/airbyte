# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from typing import Any

import jsonschema
import pytest
from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import BambooHrRequestBuilder
from mock_server.response_builder import response


@pytest.mark.parametrize(
    "stream,path,record",
    [
        (
            "employees",
            "employees/1",
            {
                "id": "1",
                "workEmail": "test@example.com",
                "terminationDate": "2026-11-01",
                "lastName": "Example",
                "canUploadPhoto": False,
            },
        ),
        (
            "timesheet_entries",
            "time_tracking/timesheet_entries",
            {
                "id": 1,
                "start": "2026-11-05T09:00:00+00:00",
                "end": "2026-11-05T17:00:00+00:00",
                "createdAt": "2026-11-05T09:00:00Z",
                "updatedAt": "2026-11-05T17:00:00Z",
                "projectInfo": {"project": {"id": 1, "name": "Project"}, "task": None},
            },
        ),
        ("meta_fields_stream", "meta/fields", {"id": "1", "deprecated": False}),
        (
            "time_off_requests_stream",
            "time_off/requests/",
            {
                "id": "1",
                "created": "2026-11-05",
                "updated": "2026-11-06",
                "notes": {"employee": "Holiday", "manager": None},
                "status": {"lastChanged": "2026-11-06", "lastChangedByUserId": 1, "status": "approved"},
                "type": {"id": 1, "name": "Vacation", "icon": None},
                "amount": {"unit": "days", "amount": 1.5},
            },
        ),
    ],
)
@freeze_time("2026-11-10T00:00:00Z")
def test_emitted_fields_conform_to_discovered_schema(stream: str, path: str, record: dict[str, Any], http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().build()
    discovered = discover(get_source(config), config)
    assert discovered.errors == []
    schema = next(item.json_schema for item in discovered.catalog.catalog.streams if item.name == stream)
    request = BambooHrRequestBuilder(path)
    if stream in ("timesheet_entries", "time_off_requests_stream"):
        request.with_query_param("start", "2026-11-01").with_query_param("end", "2026-11-10")
    if stream == "employees":
        http_mocker.get(
            BambooHrRequestBuilder("employees/directory").build(),
            response({"employees": [{"id": "1"}]}),
        )
        request.with_query_param("fields", config["employee_fields"])
    http_mocker.get(request.build(), response(record if stream == "employees" else [record]))
    output = read(get_source(config), config, CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build())
    assert output.errors == []
    assert len(output.records) == 1
    emitted = output.records[0].record.data
    for field, value in record.items():
        assert field in schema["properties"], f"{stream}.{field} is emitted but undeclared"
        assert emitted[field] == value
        if isinstance(value, dict):
            for nested in value:
                assert nested in schema["properties"][field]["properties"], f"{stream}.{field}.{nested} is undeclared"
    jsonschema.validate(emitted, schema, format_checker=jsonschema.FormatChecker())
