#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_asana.source import SourceAsana

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


def test_oauth_connector_input_specification_includes_default_scope():
    source = SourceAsana(catalog=None, config=None, state=None)

    spec = source.spec(None)
    oauth_spec = spec.advanced_auth.oauth_config_specification.oauth_connector_input_specification

    assert oauth_spec.scopes == [{"scope": "default"}]


def test_task_query_result_limit_error_message(requests_mock, config):
    catalog = CatalogBuilder().with_stream("tasks", SyncMode.full_refresh).build()
    source = SourceAsana(catalog=catalog, config=config, state={})
    limit_error_message = (
        "There is currently an upper limit on the number of results returned for this query. "
        "Please see docs at https://developers.asana.com/docs/api-limits. "
        "We apologize for any inconvenience this has caused."
    )

    requests_mock.get(
        "https://app.asana.com/api/1.0/workspaces",
        json={"data": [{"gid": "workspace_gid", "name": "workspace", "resource_type": "workspace"}]},
    )
    requests_mock.get(
        "https://app.asana.com/api/1.0/projects",
        json={"data": [{"gid": "project_gid", "name": "project", "resource_type": "project"}]},
    )
    requests_mock.get(
        "https://app.asana.com/api/1.0/tasks",
        status_code=400,
        json={"errors": [{"message": limit_error_message}]},
    )

    output = read(source, config, catalog, {}, expecting_exception=True)
    user_facing_error = output.errors[0].trace.error.message

    assert output.errors[0].trace.error.failure_type == FailureType.system_error
    assert user_facing_error == "Asana task query exceeded the API result limit."
    assert "https://developers.asana.com" not in user_facing_error
