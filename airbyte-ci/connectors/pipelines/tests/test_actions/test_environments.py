#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from click import UsageError

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


@pytest.mark.parametrize("use_local_cdk, local_cdk_is_available", [(True, True), (True, False), (False, None)])
async def test_apply_python_development_overrides(
    dagger_client, mocker, tmp_path, connector_context, use_local_cdk, local_cdk_is_available
):
    local_cdk_path = tmp_path / "airbyte-python-cdk"
    mocker.patch.object(common, "PATH_TO_LOCAL_CDK", local_cdk_path)
    if local_cdk_is_available:
        local_cdk_path.mkdir()
        await (
            dagger_client.git("https://github.com/airbytehq/airbyte-python-cdk", keep_git_dir=False)
            .branch("main")
            .tree()
            .export(str(local_cdk_path))
        )
    connector_context.use_local_cdk = use_local_cdk
    fake_connector_container = connector_context.dagger_client.container().from_("airbyte/python-connector-base:3.0.0")
    before_override_pip_freeze = await fake_connector_container.with_exec(["pip", "freeze"], use_entrypoint=True).stdout()
    assert "airbyte-cdk" not in before_override_pip_freeze.splitlines(), "The base image should not have the airbyte-cdk installed."
    if use_local_cdk and not local_cdk_is_available:
        # We assume the local cdk is not available so a UsageError should be raised.
        with pytest.raises(UsageError):
            await common.apply_python_development_overrides(connector_context, fake_connector_container, "airbyte")
    else:
        overriden_container = await common.apply_python_development_overrides(connector_context, fake_connector_container, "airbyte")
        after_override_pip_freeze = await overriden_container.with_exec(["pip", "freeze"], use_entrypoint=True).stdout()

        if use_local_cdk and local_cdk_is_available:
            assert (
                "airbyte-cdk @ file:///airbyte-cdk/python" in after_override_pip_freeze.splitlines()
            ), "The override should install the airbyte-cdk package."
            ls_ld_output = await overriden_container.with_exec(["ls", "-ld", "/airbyte-cdk/python"]).stdout()
            airbyte_cdk_owner_user, airbyte_cdk_owner_group = ls_ld_output.split()[2], ls_ld_output.split()[3]
            assert (
                airbyte_cdk_owner_user == "airbyte" and airbyte_cdk_owner_group == "airbyte"
            ), "The airbyte-cdk directory should be owned by the airbyte user."
        else:
            assert after_override_pip_freeze == before_override_pip_freeze, "The override should not change the pip freeze output."
