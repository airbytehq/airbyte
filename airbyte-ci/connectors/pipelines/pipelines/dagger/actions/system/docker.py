#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import uuid
from typing import Callable, Dict, List, Optional, Union

from dagger import Client, Container, File
from dagger import Secret as DaggerSecret
from dagger import Service
from pipelines import consts
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.consts import (
    DOCKER_HOST_NAME,
    DOCKER_HOST_PORT,
    DOCKER_REGISTRY_ADDRESS,
    DOCKER_REGISTRY_MIRROR_URL,
    DOCKER_TMP_VOLUME_NAME,
    DOCKER_VAR_LIB_VOLUME_NAME,
    STORAGE_DRIVER,
)
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.secrets import Secret


def get_base_dockerd_container(dagger_client: Client) -> Container:
    """Provision a container to run a docker daemon.
    It will be used as a docker host for docker-in-docker use cases.

    Args:
        dagger_client (Client): The dagger client used to create the container.
    Returns:
        Container: The container to run dockerd as a service
    """
    apk_packages_to_install = [
        STORAGE_DRIVER,
        # Curl is only used for debugging purposes.
        "curl",
    ]
    base_container = (
        dagger_client.container()
        .from_(consts.DOCKER_DIND_IMAGE)
        # We set this env var because we need to use a non-default zombie reaper setting.
        # The reason for this is that by default it will want to set its parent process ID to 1 when reaping.
        # This won't be possible because of container-ception: dind is running inside the dagger engine.
        # See https://github.com/krallin/tini#subreaping for details.
        .with_env_variable("TINI_SUBREAPER", "")
        .with_exec(
            sh_dash_c(
                [
                    "apk update",
                    f"apk add {' '.join(apk_packages_to_install)}",
                    "mkdir /etc/docker",
                ]
            )
        )
        # Expose the docker host port.
        .with_exposed_port(DOCKER_HOST_PORT)
        # We cache /tmp for file sharing between client and daemon.
        .with_mounted_cache("/tmp", dagger_client.cache_volume(DOCKER_TMP_VOLUME_NAME))
    )

    # We cache /var/lib/docker to avoid downloading images and layers multiple times.
    base_container = base_container.with_mounted_cache("/var/lib/docker", dagger_client.cache_volume(DOCKER_VAR_LIB_VOLUME_NAME))
    return base_container


def get_daemon_config_json(registry_mirror_url: Optional[str] = None) -> str:
    """Get the json representation of the docker daemon config.

    Args:
        registry_mirror_url (Optional[str]): The registry mirror url to use.

    Returns:
        str: The json representation of the docker daemon config.
    """
    daemon_config: Dict[str, Union[List[str], str]] = {
        "storage-driver": STORAGE_DRIVER,
    }
    if registry_mirror_url:
        daemon_config["registry-mirrors"] = ["http://" + registry_mirror_url]
        daemon_config["insecure-registries"] = [registry_mirror_url]
    return json.dumps(daemon_config)


def docker_login(
    dockerd_container: Container,
    docker_registry_username: DaggerSecret,
    docker_registry_password: DaggerSecret,
) -> Container:
    """Login to a docker registry if the username and password secrets are provided.

    Args:
        dockerd_container (Container): The dockerd_container container to login to the registry.
        docker_registry_username_secret (Secret): The docker registry username secret.
        docker_registry_password_secret (Secret): The docker registry password secret.
        docker_registry_address (Optional[str]): The docker registry address to login to. Defaults to "docker.io" (DockerHub).
    Returns:
        Container: The container with the docker login command executed if the username and password secrets are provided. Noop otherwise.
    """
    if docker_registry_username and docker_registry_username:
        return (
            dockerd_container
            # We use a cache buster here to guarantee the docker login is always executed.
            .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
            .with_secret_variable("DOCKER_REGISTRY_USERNAME", docker_registry_username)
            .with_secret_variable("DOCKER_REGISTRY_PASSWORD", docker_registry_password)
            .with_exec(sh_dash_c([f"docker login -u $DOCKER_REGISTRY_USERNAME -p $DOCKER_REGISTRY_PASSWORD {DOCKER_REGISTRY_ADDRESS}"]))
        )
    else:
        return dockerd_container


def with_global_dockerd_service(
    dagger_client: Client,
    docker_hub_username: Optional[Secret] = None,
    docker_hub_password: Optional[Secret] = None,
) -> Service:
    """Create a container with a docker daemon running.
    We expose its 2375 port to use it as a docker host for docker-in-docker use cases.
    It is optionally connected to a DockerHub mirror if the DOCKER_REGISTRY_MIRROR_URL env var is set.
    Args:
        dagger_client (Client): The dagger client used to create the container.
        docker_hub_username (Optional[Secret]): The DockerHub username secret.
        docker_hub_password (Optional[Secret]): The DockerHub password secret.
    Returns:
        Container: The container running dockerd as a service
    """

    dockerd_container = get_base_dockerd_container(dagger_client)
    if DOCKER_REGISTRY_MIRROR_URL is not None:
        # Ping the registry mirror host to make sure it's reachable through VPN
        # We set a cache buster here to guarantee the curl command is always executed.
        dockerd_container = dockerd_container.with_env_variable("CACHEBUSTER", str(uuid.uuid4())).with_exec(
            ["curl", "-vvv", f"http://{DOCKER_REGISTRY_MIRROR_URL}/v2/"]
        )
        daemon_config_json = get_daemon_config_json(DOCKER_REGISTRY_MIRROR_URL)
    else:
        daemon_config_json = get_daemon_config_json()

    dockerd_container = dockerd_container.with_new_file("/etc/docker/daemon.json", contents=daemon_config_json)
    if docker_hub_username and docker_hub_password:
        # Docker login happens late because there's a cache buster in the docker login command.
        dockerd_container = docker_login(
            dockerd_container, docker_hub_username.as_dagger_secret(dagger_client), docker_hub_password.as_dagger_secret(dagger_client)
        )
    return dockerd_container.with_exec(
        ["dockerd", "--log-level=error", f"--host=tcp://0.0.0.0:{DOCKER_HOST_PORT}", "--tls=false"],
        insecure_root_capabilities=True,
        use_entrypoint=True,
    ).as_service()


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
    assert context.dockerd_service is not None
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


async def load_image_to_docker_host(context: ConnectorContext, tar_file: File, image_tag: str) -> str:
    """Load a docker image tar archive to the docker host.

    Args:
        context (ConnectorContext): The current connector context.
        tar_file (File): The file object holding the docker image tar archive.
        image_tag (str): The tag to create on the image if it has no tag.
    """
    # Hacky way to make sure the image is always loaded
    tar_name = f"{str(uuid.uuid4())}.tar"
    docker_cli = with_docker_cli(context).with_mounted_file(tar_name, tar_file)

    image_load_output = await docker_cli.with_exec(["docker", "load", "--input", tar_name], use_entrypoint=True).stdout()
    # Not tagged images only have a sha256 id the load output shares.
    if "sha256:" in image_load_output:
        image_id = image_load_output.replace("\n", "").replace("Loaded image ID: sha256:", "")
        await docker_cli.with_exec(["docker", "tag", image_id, image_tag], use_entrypoint=True)
    image_sha = json.loads(await docker_cli.with_exec(["docker", "inspect", image_tag], use_entrypoint=True).stdout())[0].get("Id")
    return image_sha


def with_crane(
    context: ConnectorContext,
) -> Container:
    """Crane is a tool to analyze and manipulate container images.
    We can use it to extract the image manifest and the list of layers or list the existing tags on an image repository.
    https://github.com/google/go-containerregistry/tree/main/cmd/crane
    """

    # We use the debug image as it contains a shell which we need to properly use environment variables
    # https://github.com/google/go-containerregistry/tree/main/cmd/crane#images
    base_container = context.dagger_client.container().from_("gcr.io/go-containerregistry/crane/debug:v0.15.1")

    if context.docker_hub_username and context.docker_hub_password:
        base_container = (
            base_container.with_secret_variable(
                "DOCKER_HUB_USERNAME", context.docker_hub_username.as_dagger_secret(context.dagger_client)
            ).with_secret_variable("DOCKER_HUB_PASSWORD", context.docker_hub_password.as_dagger_secret(context.dagger_client))
            # We use sh -c to be able to use environment variables in the command
            # This is a workaround as the default crane entrypoint doesn't support environment variables
            .with_exec(sh_dash_c(["crane auth login index.docker.io -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD"]))
        )

    return base_container
