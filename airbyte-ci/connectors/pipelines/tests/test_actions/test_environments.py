#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python import common
from pipelines.helpers.connectors.modifed import ConnectorWithModifiedFiles

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def connector_context(dagger_client):
    context = ConnectorContext(
        pipeline_name="test",
        connector=ConnectorWithModifiedFiles("source-faker", modified_files={}),
        git_branch="test",
        git_revision="test",
        diffed_branch="test",
        git_repo_url="test",
        report_output_prefix="test",
        is_local=True,
    )
    context.dagger_client = dagger_client
    return context


@pytest.mark.parametrize("use_local_cdk", [True, False])
async def test_apply_python_development_overrides(connector_context, use_local_cdk):
    connector_context.use_local_cdk = use_local_cdk
    fake_connector_container = connector_context.dagger_client.container().from_("airbyte/python-connector-base:2.0.0")
    before_override_pip_freeze = await fake_connector_container.with_exec(["pip", "freeze"]).stdout()

    assert "airbyte-cdk" not in before_override_pip_freeze.splitlines(), "The base image should not have the airbyte-cdk installed."
    connector_with_overrides = await common.apply_python_development_overrides(connector_context, fake_connector_container)

    after_override_pip_freeze = await connector_with_overrides.with_exec(["pip", "freeze"]).stdout()
    if use_local_cdk:
        assert "airbyte-cdk" not in after_override_pip_freeze.splitlines(), "The override should not install the airbyte-cdk package."
    else:
        assert "airbyte-cdk" not in after_override_pip_freeze.splitlines(), "The override should install the airbyte-cdk package."
