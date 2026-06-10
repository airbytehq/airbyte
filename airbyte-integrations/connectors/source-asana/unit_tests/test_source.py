#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

from source_asana.source import SourceAsana

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


BASE_URL = "https://app.asana.com/api/1.0"
PAT_CONFIG = {"credentials": {"option_title": "PAT Credentials", "personal_access_token": "test-token"}}


def _response(*records: dict) -> HttpResponse:
    return HttpResponse(json.dumps({"data": list(records), "next_page": None}))


def test_oauth_connector_input_specification_includes_default_scope():
    source = SourceAsana(catalog=None, config=None, state=None)

    spec = source.spec(None)
    oauth_spec = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification

    assert oauth_spec.scopes == [{"scope": "default"}]


def test_tasks_stream_reads_tasks_by_section():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/workspaces", query_params=ANY_QUERY_PARAMS),
            _response({"gid": "workspace-1", "name": "Workspace 1"}),
        )
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/projects", query_params=ANY_QUERY_PARAMS),
            _response({"gid": "project-1", "name": "Project 1"}),
        )
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/projects/project-1/sections", query_params=ANY_QUERY_PARAMS),
            _response(
                {"gid": "section-1", "name": "Section 1"},
                {"gid": "section-2", "name": "Section 2"},
            ),
        )
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/sections/section-1/tasks", query_params=ANY_QUERY_PARAMS),
            _response({"gid": "task-1", "name": "Task 1"}),
        )
        http_mocker.get(
            HttpRequest(f"{BASE_URL}/sections/section-2/tasks", query_params=ANY_QUERY_PARAMS),
            _response({"gid": "task-2", "name": "Task 2"}),
        )

        catalog = CatalogBuilder().with_stream("tasks", SyncMode.full_refresh).build()
        output = read(SourceAsana(catalog=None, config=PAT_CONFIG, state=None), config=PAT_CONFIG, catalog=catalog)

    assert {record.record.data["gid"] for record in output.records} == {"task-1", "task-2"}
    assert not output.errors
