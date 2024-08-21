#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime

import asyncclick as click
import pytest
import requests
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python import common

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture(scope="module")
def latest_cdk_version():
    cdk_pypi_url = "https://pypi.org/pypi/airbyte-cdk/json"
    response = requests.get(cdk_pypi_url)
    response.raise_for_status()
    package_info = response.json()
    return package_info["info"]["version"]


@pytest.fixture(scope="module")
def python_connector_with_setup_not_latest_cdk(all_connectors):
    for connector in all_connectors:
        if (
            connector.metadata.get("connectorBuildOptions", False)
            # We want to select a connector with a base image version >= 2.0.0 to use Python 3.10
            and not connector.metadata.get("connectorBuildOptions", {})
            .get("baseImage", "")
            .startswith("docker.io/airbyte/python-connector-base:1.")
            and connector.language == "python"
            and connector.code_directory.joinpath("setup.py").exists()
        ):
            return connector
    pytest.skip("No python connector with setup.py and not latest cdk version found")


@pytest.fixture(scope="module")
def context_with_setup(dagger_client, python_connector_with_setup_not_latest_cdk):
    context = ConnectorContext(
        pipeline_name="test python common",
        connector=python_connector_with_setup_not_latest_cdk,
        git_branch="test",
        git_revision="test",
        diffed_branch="test",
        git_repo_url="test",
        report_output_prefix="test",
        is_local=True,
        pipeline_start_timestamp=datetime.datetime.now().isoformat(),
    )
    context.dagger_client = dagger_client
    return context


@pytest.fixture(scope="module")
def python_connector_base_image_address(python_connector_with_setup_not_latest_cdk):
    return python_connector_with_setup_not_latest_cdk.metadata["connectorBuildOptions"]["baseImage"]


async def test_with_python_connector_installed_from_setup(context_with_setup, python_connector_base_image_address, latest_cdk_version):

    python_container = context_with_setup.dagger_client.container().from_(python_connector_base_image_address)

    container = await common.with_python_connector_installed(
        context_with_setup, python_container, str(context_with_setup.connector.code_directory)
    )
    # Uninstall and reinstall the latest cdk version
    cdk_install_latest_output = (
        await container.with_env_variable("CACHEBUSTER", datetime.datetime.now().isoformat())
        # .with_exec(["pip", "install", f"airbyte-cdk=={latest_cdk_version}"], skip_entrypoint=True)
        .with_exec(["pip", "uninstall", "-y", f"airbyte-cdk=={latest_cdk_version}"], skip_entrypoint=True)
        .with_exec(["pip", "install", f"airbyte-cdk=={latest_cdk_version}"], skip_entrypoint=True)
        .stdout()
    )
    # Assert that the latest cdk version is installed from cache
    assert f"Using cached airbyte_cdk-{latest_cdk_version}-py3-none-any.whl" in cdk_install_latest_output
    # Assert that the connector is installed
    pip_freeze_output = await container.with_exec(["pip", "freeze"], skip_entrypoint=True).stdout()
    assert context_with_setup.connector.technical_name in pip_freeze_output
