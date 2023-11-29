#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import uuid
from typing import Callable, Optional

from dagger import Client, Container, File, Secret
from pipelines import consts
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.consts import DOCKER_HOST_NAME, DOCKER_HOST_PORT, DOCKER_TMP_VOLUME_NAME, DOCKER_VAR_LIB_VOLUME_NAME
from pipelines.helpers.utils import sh_dash_c


def with_global_dockerd_service(
    dagger_client: Client, docker_hub_username_secret: Optional[Secret] = None, docker_hub_password_secret: Optional[Secret] = None
) -> Container:
    """Create a container with a docker daemon running.
    We expose its 2375 port to use it as a docker host for docker-in-docker use cases.
    Args:
        dagger_client (Client): The dagger client used to create the container.
        docker_hub_username_secret (Optional[Secret]): The DockerHub username secret.
        docker_hub_password_secret (Optional[Secret]): The DockerHub password secret.
    Returns:
        Container: The container running dockerd as a service
    """
    dockerd_container = (
        dagger_client.container()
        .from_(consts.DOCKER_DIND_IMAGE)
        # We set this env var because we need to use a non-default zombie reaper setting.
        # The reason for this is that by default it will want to set its parent process ID to 1 when reaping.
        # This won't be possible because of container-ception: dind is running inside the dagger engine.
        # See https://github.com/krallin/tini#subreaping for details.
        .with_env_variable("TINI_SUBREAPER", "")
        # Similarly, because of container-ception, we have to use the fuse-overlayfs storage engine.
        .with_exec(
            sh_dash_c(
                [
                    # Update package metadata.
                    "apk update",
                    # Install the storage driver package.
                    "apk add fuse-overlayfs",
                    # Update daemon config with storage driver.
                    "mkdir /etc/docker",
                    '(echo {\\"storage-driver\\": \\"fuse-overlayfs\\"} > /etc/docker/daemon.json)',
                ]
            )
        )
        # Expose the docker host port.
        .with_exposed_port(DOCKER_HOST_PORT)
        # Mount the docker cache volumes.
        .with_mounted_cache("/var/lib/docker", dagger_client.cache_volume(DOCKER_VAR_LIB_VOLUME_NAME))
        .with_mounted_cache("/tmp", dagger_client.cache_volume(DOCKER_TMP_VOLUME_NAME))
    )
    if docker_hub_username_secret and docker_hub_password_secret:
        dockerd_container = (
            dockerd_container
            # We use a cache buster here to guarantee the docker login is always executed.
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_secret_variable("DOCKER_HUB_USERNAME", docker_hub_username_secret)
            .with_secret_variable("DOCKER_HUB_PASSWORD", docker_hub_password_secret)
            .with_exec(sh_dash_c(["docker login -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD"]), skip_entrypoint=True)
        )
    return dockerd_container.with_exec(
        ["dockerd", "--log-level=error", f"--host=tcp://0.0.0.0:{DOCKER_HOST_PORT}", "--tls=false"], insecure_root_capabilities=True
    )


def with_bound_docker_host(
    context: ConnectorContext,
    container: Container,
) -> Container:
    """Bind a container to a docker host. It will use the dockerd service as a docker host.

    Args:
        context (ConnectorContext): The current connector context.
        container (Container): The container to bind to the docker host.
    Returns:
        Container: The container bound to the docker host.
    """
    return (
        container.with_env_variable("DOCKER_HOST", f"tcp://{DOCKER_HOST_NAME}:{DOCKER_HOST_PORT}")
        .with_service_binding(DOCKER_HOST_NAME, context.dockerd_service)
        .with_mounted_cache("/tmp", context.dagger_client.cache_volume(DOCKER_TMP_VOLUME_NAME))
    )


def bound_docker_host(context: ConnectorContext) -> Callable[[Container], Container]:
    def bound_docker_host_inner(container: Container) -> Container:
        return with_bound_docker_host(context, container)

    return bound_docker_host_inner


def with_docker_cli(context: ConnectorContext) -> Container:
    """Create a container with the docker CLI installed and bound to a persistent docker host.

    Args:
        context (ConnectorContext): The current connector context.

    Returns:
        Container: A docker cli container bound to a docker host.
    """
    docker_cli = context.dagger_client.container().from_(consts.DOCKER_CLI_IMAGE)
    return with_bound_docker_host(context, docker_cli)


async def load_image_to_docker_host(context: ConnectorContext, tar_file: File, image_tag: str):
    """Load a docker image tar archive to the docker host.

    Args:
        context (ConnectorContext): The current connector context.
        tar_file (File): The file object holding the docker image tar archive.
        image_tag (str): The tag to create on the image if it has no tag.
    """
    # Hacky way to make sure the image is always loaded
    tar_name = f"{str(uuid.uuid4())}.tar"
    docker_cli = with_docker_cli(context).with_mounted_file(tar_name, tar_file)

    image_load_output = await docker_cli.with_exec(["docker", "load", "--input", tar_name]).stdout()
    # Not tagged images only have a sha256 id the load output shares.
    if "sha256:" in image_load_output:
        image_id = image_load_output.replace("\n", "").replace("Loaded image ID: sha256:", "")
        await docker_cli.with_exec(["docker", "tag", image_id, image_tag])
    image_sha = json.loads(await docker_cli.with_exec(["docker", "inspect", image_tag]).stdout())[0].get("Id")
    return image_sha


def with_crane(
    context: PipelineContext,
) -> Container:
    """Crane is a tool to analyze and manipulate container images.
    We can use it to extract the image manifest and the list of layers or list the existing tags on an image repository.
    https://github.com/google/go-containerregistry/tree/main/cmd/crane
    """

    # We use the debug image as it contains a shell which we need to properly use environment variables
    # https://github.com/google/go-containerregistry/tree/main/cmd/crane#images
    base_container = context.dagger_client.container().from_("gcr.io/go-containerregistry/crane/debug:v0.15.1")

    if context.docker_hub_username_secret and context.docker_hub_password_secret:
        base_container = (
            base_container.with_secret_variable("DOCKER_HUB_USERNAME", context.docker_hub_username_secret).with_secret_variable(
                "DOCKER_HUB_PASSWORD", context.docker_hub_password_secret
            )
            # We need to use skip_entrypoint=True to avoid the entrypoint to be overridden by the crane command
            # We use sh -c to be able to use environment variables in the command
            # This is a workaround as the default crane entrypoint doesn't support environment variables
            .with_exec(
                sh_dash_c(["crane auth login index.docker.io -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD"]), skip_entrypoint=True
            )
        )

    return base_container
