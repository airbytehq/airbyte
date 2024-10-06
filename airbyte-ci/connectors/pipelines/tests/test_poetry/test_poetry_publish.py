#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import requests
from dagger import Client, Platform
from pipelines.airbyte_ci.connectors.publish import pipeline as publish_pipeline
from pipelines.dagger.actions.python.poetry import with_poetry
from pipelines.models.contexts.python_registry_publish import PythonPackageMetadata, PythonRegistryPublishContext
from pipelines.models.secrets import InMemorySecretStore, Secret
from pipelines.models.steps import StepStatus

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def context(dagger_client: Client):
    in_memory_secret_store = InMemorySecretStore()
    in_memory_secret_store.add_secret("python_registry_token", "test")

    context = PythonRegistryPublishContext(
        package_path="test",
        version="0.2.0",
        python_registry_token=Secret("python_registry_token", in_memory_secret_store),
        package_name="test",
        registry_check_url="http://local_registry:8080/",
        registry="http://local_registry:8080/",
        is_local=True,
        git_branch="test",
        git_revision="test",
        diffed_branch="test",
        git_repo_url="test",
        report_output_prefix="test",
        ci_report_bucket="test",
    )
    context.dagger_client = dagger_client
    return context


@pytest.mark.parametrize(
    "package_path, package_name, expected_asset",
    [
        pytest.param(
            "airbyte-integrations/connectors/source-apify-dataset",
            "airbyte-source-apify-dataset",
            "airbyte_source_apify_dataset-0.2.0-py3-none-any.whl",
            id="setup.py project",
        ),
        pytest.param(
            "airbyte-integrations/connectors/destination-duckdb",
            "destination-duckdb",
            "destination_duckdb-0.2.0-py3-none-any.whl",
            id="poetry project",
        ),
    ],
)
async def test_run_poetry_publish(context: PythonRegistryPublishContext, package_path: str, package_name: str, expected_asset: str):
    context.package_metadata = PythonPackageMetadata(package_name, "0.2.0")
    context.package_path = package_path
    pypi_registry = (
        # need to use linux/amd64 because the pypiserver image is only available for that platform
        context.dagger_client.container(platform=Platform("linux/amd64"))
        .from_("pypiserver/pypiserver:v2.0.1")
        .with_exec(["run", "-P", ".", "-a", "."])
        .with_exposed_port(8080)
        .as_service()
    )

    base_container = with_poetry(context).with_service_binding("local_registry", pypi_registry)
    step = publish_pipeline.PublishToPythonRegistry(context)
    step._get_base_container = MagicMock(return_value=base_container)
    step_result = await step.run()
    assert step_result.status == StepStatus.SUCCESS

    # Query the registry to check that the package was published
    tunnel = await context.dagger_client.host().tunnel(pypi_registry).start()
    endpoint = await tunnel.endpoint(scheme="http")
    list_url = f"{endpoint}/simple/"
    list_response = requests.get(list_url)
    assert list_response.status_code == 200
    assert package_name in list_response.text
    url = f"{endpoint}/simple/{package_name}"
    response = requests.get(url)
    assert response.status_code == 200
    assert expected_asset in response.text
