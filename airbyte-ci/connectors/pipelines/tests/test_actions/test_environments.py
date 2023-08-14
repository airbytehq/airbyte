#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import uuid

import pytest
from pipelines import bases
from pipelines.actions import environments
from pipelines.contexts import ConnectorContext

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def python_connector() -> bases.ConnectorWithModifiedFiles:
    return bases.ConnectorWithModifiedFiles("source-faker", frozenset())


@pytest.fixture
async def context(dagger_client, tmpdir):
    context = ConnectorContext(
        connector=bases.ConnectorWithModifiedFiles("source-faker", frozenset()),
        report_output_prefix=str(tmpdir),
        pipeline_name="test",
        is_local=True,
        git_branch="test",
        git_revision="test",
    )
    context.dagger_client = dagger_client
    context.dockerd_service_name = f"{uuid.uuid4()}-test-docker-host"
    context.dockerd_service = await environments.with_dockerd_service(context)
    return context


async def test_with_installed_python_package(context, python_connector):
    python_environment = context.dagger_client.container().from_("python:3.9")
    installed_connector_package = await environments.with_installed_python_package(
        context,
        python_environment,
        str(python_connector.code_directory),
    )
    await installed_connector_package.with_exec(["python", "main.py", "spec"])


async def test_with_docker_cli(context):
    """
    This test the service binding behavior between a container (docker cli) and a service (dockerd).
    We ensure dockerd persistency works per service binding by pulling an image in a docker cli instance and checking that the image is available in another docker cli instance bound to the same docker host.
    """

    # Check that a new docker cli instance has no images
    first_docker_cli = await environments.with_docker_cli(context)
    assert await first_docker_cli.env_variable("DOCKER_HOST") == f"tcp://{context.dockerd_service_name}:2375"
    images = (await first_docker_cli.with_exec(["docker", "images"]).stdout()).splitlines()[1:]
    assert len(images) == 0

    await first_docker_cli.with_exec(["docker", "pull", "hello-world"])

    # Check that a new docker cli instance bound to the same docker host has access to the pulled image which is stored in a volume cache
    second_docker_cli = await environments.with_docker_cli(context)
    images = (await second_docker_cli.with_exec(["docker", "images"]).stdout()).splitlines()[1:]
    assert len(images) == 1


@pytest.fixture
async def docker_image_tar_file(dagger_client, tmpdir):

    await dagger_client.container().from_("hello-world").export(str(tmpdir / "image.tar"))
    return dagger_client.host().directory(str(tmpdir), include=["image.tar"]).file("image.tar")


async def test_load_image_to_docker_host(context, docker_image_tar_file):
    image_tag = "test:dev"
    for _ in range(10):
        image_sha = await environments.load_image_to_docker_host(context, docker_image_tar_file, image_tag)
        assert image_sha is not None
