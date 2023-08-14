#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# from uuid import uuid4

import pytest
from connector_ops.utils import Connector
from pipelines.actions import environments
from pipelines.contexts import PipelineContext

pytestmark = [
    pytest.mark.anyio,
]


@pytest.fixture
def python_connector() -> Connector:
    return Connector("source-openweather")


@pytest.fixture
def context(dagger_client):
    context = PipelineContext(
        pipeline_name="test",
        is_local=True,
        git_branch="test",
        git_revision="test",
    )
    context.dagger_client = dagger_client
    context.dockerd_service = environments.with_dockerd_service(dagger_client, "global-docker-host")
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
    global_docker_host_binding = environments.bound_docker_host(context)
    first_docker_cli = environments.with_docker_cli(context, global_docker_host_binding)
    assert await first_docker_cli.env_variable("DOCKER_HOST") == "tcp://global-docker-host:2375"
    images = (await first_docker_cli.with_exec(["docker", "images"]).stdout()).splitlines()[1:]
    assert len(images) == 0

    await first_docker_cli.with_exec(["docker", "pull", "hello-world"])

    # Check that a new docker cli instance bound to the same docker host has access to the pulled image which is stored in a volume cache
    second_docker_cli = environments.with_docker_cli(context, global_docker_host_binding)
    images = (await second_docker_cli.with_exec(["docker", "images"]).stdout()).splitlines()[1:]
    assert len(images) == 1

    # Check that a new docker cli with a different docker host binding does not have access to previously the pulled image
    third_docker_cli = environments.with_docker_cli(context)
    assert await third_docker_cli.env_variable("DOCKER_HOST") == "tcp://custom-docker-host:2375"
    images = (await third_docker_cli.with_exec(["docker", "images"]).stdout()).splitlines()[1:]
    assert len(images) == 0
    await third_docker_cli.with_exec(["docker", "pull", "hello-world"])

    # Check that a new docker cli instance bound to the same docker host has access to the pulled image which is stored in a volume cache
    fourth_docker_cli = environments.with_docker_cli(context)
    images = (await fourth_docker_cli.with_exec(["docker", "images"]).stdout()).splitlines()[1:]
    assert len(images) == 1


@pytest.fixture
async def docker_image_tar_file(dagger_client, tmpdir):

    # await dagger_client.host().directory(str(Connector("source-openweather").code_directory)).docker_build().with_exec(["spec"]).export(str(tmpdir / "image.tar"))
    await dagger_client.container().from_("hello-world").export(str(tmpdir / "image.tar"))
    return dagger_client.host().directory(str(tmpdir), include=["image.tar"]).file("image.tar")


# async def test_load_image_to_docker_host(context, docker_image_tar_file):

#     docker_host_binding = environments.bound_docker_host(context, f"{uuid4()}-test-docker-host")

#     image_tag = "test:dev"
#     for _ in range(10):
#         image_sha = await environments.load_image_to_docker_host(context, docker_image_tar_file, image_tag, docker_host_binding)
#         assert image_sha is not None
