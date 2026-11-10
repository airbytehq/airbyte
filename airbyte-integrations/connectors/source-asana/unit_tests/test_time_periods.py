# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import jsonschema
import requests_cache
from source_asana.source import SourceAsana

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_dates_and_parent_relationship(requests_mock, monkeypatch):
    monkeypatch.delenv("REQUEST_CACHE_PATH", raising=False)
    requests_cache.SQLiteCache("file::memory:?cache=shared").clear()
    config = {"credentials": {"option_title": "PAT Credentials", "personal_access_token": "token"}, "enable_goal_streams": True}
    requests_mock.get("https://app.asana.com/api/1.0/workspaces", json={"data": [{"gid": "w1"}]})
    endpoint = requests_mock.get(
        "https://app.asana.com/api/1.0/time_periods",
        json={
            "data": [
                {
                    "gid": "t1",
                    "resource_type": "time_period",
                    "period": "Q1",
                    "display_name": "Q1 FY26",
                    "start_on": "2026-01-01",
                    "end_on": "2026-03-31",
                    "parent": {"gid": "fy26", "period": "FY", "display_name": "FY26"},
                },
                {"gid": "fy26", "start_on": None, "end_on": None, "parent": None},
            ],
            "next_page": None,
        },
    )
    source = SourceAsana(config=config, catalog=None, state=None)
    output = read(source, config, CatalogBuilder().with_stream("time_periods", SyncMode.full_refresh).build())
    assert len(output.records) == 2
    schema = next(s for s in source.streams(config) if s.name == "time_periods").get_json_schema()
    for record in output.records:
        data = record.record.data
        assert data["workspace_gid"] == "w1"
        assert set(data) <= set(schema["properties"])
        jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())
    fields = set(endpoint.last_request.qs["opt_fields"][0].split(","))
    assert {"start_on", "end_on", "parent.gid", "display_name"} <= fields
    assert "start_on" not in endpoint.last_request.qs
    assert "end_on" not in endpoint.last_request.qs
