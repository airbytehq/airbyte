#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to create reusable environments packaged in dagger containers."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional, Tuple

from ci_connector_ops.pipelines.utils import get_file_contents
from dagger import CacheSharingMode, CacheVolume, Container, Directory, File, Secret

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorTestContext

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

CONNECTOR_TESTING_REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
    "pytest-custom_exit_code",
]

INSTALL_LOCAL_REQUIREMENTS_CMD = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
INSTALL_CONNECTOR_PACKAGE_CMD = ["python", "-m", "pip", "install", "."]
DEFAULT_PYTHON_EXCLUDE = [".venv"]
CI_CREDENTIALS_SOURCE_PATH = "tools/ci_credentials"
CI_CONNECTOR_OPS_SOURCE_PATH = "tools/ci_connector_ops"


def with_python_base(context: ConnectorTestContext, python_image_name: str = "python:3.9-slim") -> Container:
    """Builds a Python container with a cache volume for pip cache.

    Args:
        context (ConnectorTestContext): The current test context, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """
    if not python_image_name.startswith("python:3"):
        raise ValueError("You have to use a python image to build the python base environment")
    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")
    return (
        context.dagger_client.container()
        .from_(python_image_name)
        .with_mounted_cache("/root/.cache/pip", pip_cache, sharing=CacheSharingMode.SHARED)
        .with_mounted_directory("/tools", context.get_repo_dir("tools", include=["ci_credentials", "ci_common_utils"], exclude=[".venv"]))
        .with_exec(["pip", "install", "--upgrade", "pip"])
    )


def with_testing_dependencies(context: ConnectorTestContext) -> Container:
    """Builds a testing environment by installing testing dependencies on top of a python base environment.

    Args:
        context (ConnectorTestContext): The current test context, providing a dagger client and a repository directory.

    Returns:
        Container: The testing environment container.
    """
    python_environment: Container = with_python_base(context)
    pyproject_toml_file = context.get_repo_dir(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)
    return python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS).with_file(
        f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file
    )


def with_python_package(
    context: ConnectorTestContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
) -> Container:
    """Load a python package source code to a python environment container.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package source code.
    """
    if exclude:
        exclude = DEFAULT_PYTHON_EXCLUDE + exclude
    else:
        exclude = DEFAULT_PYTHON_EXCLUDE
    package_source_code_directory: Directory = context.get_repo_dir(package_source_code_path, exclude=exclude)
    container = python_environment.with_mounted_directory("/" + package_source_code_path, package_source_code_directory).with_workdir(
        "/" + package_source_code_path
    )
    return container


async def with_installed_python_package(
    context: ConnectorTestContext,
    python_environment: Container,
    package_source_code_path: str,
    additional_dependency_groups: Optional[List] = None,
    exclude: Optional[List] = None,
) -> Container:
    """Installs a python package in a python environment container.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package installed.
    """

    container = with_python_package(context, python_environment, package_source_code_path, exclude=exclude)
    if requirements_txt := await get_file_contents(container, "requirements.txt"):
        for line in requirements_txt.split("\n"):
            if line.startswith("-e ."):
                local_dependency_path = package_source_code_path + "/" + line[3:]
                container = container.with_mounted_directory(
                    "/" + local_dependency_path, context.get_repo_dir(local_dependency_path, exclude=DEFAULT_PYTHON_EXCLUDE)
                )
        container = container.with_exec(INSTALL_LOCAL_REQUIREMENTS_CMD)

    container = container.with_exec(INSTALL_CONNECTOR_PACKAGE_CMD)

    if additional_dependency_groups:
        container = container.with_exec(
            INSTALL_CONNECTOR_PACKAGE_CMD[:-1] + [INSTALL_CONNECTOR_PACKAGE_CMD[-1] + f"[{','.join(additional_dependency_groups)}]"]
        )

    return container


def with_airbyte_connector(context: ConnectorTestContext) -> Container:
    """Load an airbyte connector source code in a testing environment.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector source code).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    return with_python_package(context, testing_environment, connector_source_path, exclude=["secrets"])


async def with_installed_airbyte_connector(context: ConnectorTestContext) -> Container:
    """Installs an airbyte connector python package in a testing environment.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector installed).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    return await with_installed_python_package(
        context, testing_environment, connector_source_path, additional_dependency_groups=["dev", "tests", "main"], exclude=["secrets"]
    )


async def with_ci_credentials(context: ConnectorTestContext, gsm_secret: Secret) -> Container:
    """Installs the ci_credentials package in a python environment.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_python_package(context, python_base_environment, CI_CREDENTIALS_SOURCE_PATH)

    return ci_credentials.with_env_variable("VERSION", "dev").with_secret_variable("GCP_GSM_CREDENTIALS", gsm_secret).with_workdir("/")


async def with_ci_connector_ops(context: ConnectorTestContext) -> Container:
    """Installs the ci_connector_ops package in a Container running Python > 3.10 with git..

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the ci_connector_sources sources will be pulled.

    Returns:
        Container: A python environment container with ci_connector_ops installed.
    """
    python_base_environment: Container = with_python_base(context, "python:3-alpine")
    python_with_git = python_base_environment.with_exec(["apk", "add", "gcc", "libffi-dev", "musl-dev", "git"])
    return await with_installed_python_package(context, python_with_git, CI_CONNECTOR_OPS_SOURCE_PATH, exclude=["pipelines"])


def with_dockerd_service(
    context: ConnectorTestContext, shared_volume: Optional(Tuple[str, CacheVolume]) = None, docker_cache_volume_name: Optional[str] = None
) -> Container:
    """Create a container running dockerd, exposing its 2375 port.
    This container can be used as the docker host for docker-in-docker use cases.
    An optional shared_volume is mounted to the container to allow client and docker host to share the same files.
    The /var/lib/docker is cached to provide persistent image storing throughout runs.

    Args:
        context (ConnectorTestContext): The current connector test context.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be mounted to the dockerd container. Defaults to None.
        docker_cache_volume_name (Optional[str], optional): The name of the docker cache volume. Changing the volume name provides docker context isolation. Defaults to None.

    Returns:
        Container: The container running dockerd as a service.
    """
    dind = (
        context.dagger_client.container()
        .from_("docker:23.0.1-dind")
        .with_mounted_cache("/var/lib/docker", context.dagger_client.cache_volume("docker-lib"), sharing=CacheSharingMode.PRIVATE)
    )
    if shared_volume is not None:
        dind = dind.with_mounted_cache(*shared_volume)
    return dind.with_exposed_port(2375).with_exec(
        ["dockerd", "--log-level=error", "--host=tcp://0.0.0.0:2375", "--tls=false"], insecure_root_capabilities=True
    )


def with_bound_docker_host(
    context: ConnectorTestContext,
    container: Container,
    shared_volume: Optional(Tuple[str, CacheVolume]) = None,
    docker_cache_volume_name: Optional[str] = None,
) -> Container:
    """Bind a container to a docker host. If the docker-cli is installed in this container it will use the dockerd service as a docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        container (Container): The container to bind to the docker host.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be both mounted to the container and the dockerd container. Defaults to None.
        docker_cache_volume_name (Optional[str], optional): The name of the docker cache volume. Changing the volume name provides docker context isolation. Defaults to None.

    Returns:
        Container: The container bound to the docker host.
    """
    dockerd = with_dockerd_service(context, shared_volume, docker_cache_volume_name)
    docker_hostname = f"dockerhost-{context.connector.technical_name}"
    bound = container.with_env_variable("DOCKER_HOST", f"tcp://{docker_hostname}:2375").with_service_binding(docker_hostname, dockerd)
    if shared_volume:
        bound = bound.with_mounted_cache(*shared_volume)
    return bound


def with_docker_cli(
    context: ConnectorTestContext, shared_volume: Optional(Tuple[str, CacheVolume]) = None, docker_cache_volume_name: Optional[str] = None
) -> Container:
    """Create a container with the docker CLI installed and bound to a persistent docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be both mounted to the container and the dockerd container. Defaults to None.
        docker_cache_volume_name (Optional[str], optional): The name of the docker cache volume. Changing the volume name provides docker context isolation. Defaults to None.

    Returns:
        Container: A docker cli container bound to a docker host.
    """
    docker_cli = context.dagger_client.container().from_("docker:23.0.1-cli")
    return with_bound_docker_host(context, docker_cli, shared_volume, docker_cache_volume_name)


async def with_connector_acceptance_test(context: ConnectorTestContext, connector_under_test_image_tar: File) -> Container:
    """Create a container to run connector acceptance tests, bound to a persistent docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        connector_under_test_image_tar (File): The file containing the tar archive the image of the connector under test.
    Returns:
        Container: A container with connector acceptance tests installed.
    """

    connector_under_test_image_name = context.connector.acceptance_test_config["connector_image"]
    await load_image_to_docker_host(context, connector_under_test_image_tar, connector_under_test_image_name)

    if context.connector_acceptance_test_image.endswith(":dev"):
        cat_container = context.connector_acceptance_test_source_dir.docker_build()
    else:
        cat_container = context.dagger_client.container().from_(context.connector_acceptance_test_image)
    shared_tmp_volume = ("/tmp", context.dagger_client.cache_volume("share-tmp-cat"))

    return (
        with_bound_docker_host(context, cat_container, shared_tmp_volume)
        .with_entrypoint(["pip"])
        .with_exec(["install", "pytest-custom_exit_code"])
        .with_mounted_directory("/test_input", context.get_connector_dir(exclude=["secrets", ".venv"]))
        .with_directory("/test_input/secrets", context.secrets_dir)
        .with_workdir("/test_input")
        .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "--suppress-tests-failed-exit-code"])
        .with_exec(["--acceptance-test-config", "/test_input"])
    )


def with_gradle(
    context: ConnectorTestContext, sources_to_include: List[str] = None, docker_cache_volume_name: Optional[str] = None
) -> Container:
    """Create a container with Gradle installed and bound to a persistent docker host.
    Multiple Java projects are mounted to the container to enable connector builds.
    Args:
        context (ConnectorTestContext): The current connector test context.
        sources_to_include (List[str], optional): List of additional source path to mount to the container. Defaults to None.
        docker_cache_volume_name (Optional[str], optional): The name of the docker cache volume. Changing the volume name provides docker context isolation. Defaults to None.

    Returns:
        Container: A container with Gradle installed and Java sources from the repository.
    """
    airbyte_gradle_cache: CacheVolume = context.dagger_client.cache_volume(f"{context.connector.technical_name}_airbyte_gradle_cache")
    root_gradle_cache: CacheVolume = context.dagger_client.cache_volume(f"{context.connector.technical_name}_root_gradle_cache")

    include = [
        ".root",
        ".env",
        "build.gradle",
        "deps.toml",
        "gradle.properties",
        "gradle",
        "gradlew",
        "LICENSE_SHORT",
        "publish-repositories.gradle",
        "settings.gradle",
        "build.gradle",
        "tools/gradle",
        "spotbugs-exclude-filter-file.xml",
        "buildSrc",
        "tools/bin/build_image.sh",
        "tools/lib/lib.sh",
    ]

    if sources_to_include:
        include += sources_to_include

    shared_tmp_volume = ("/tmp", context.dagger_client.cache_volume("share-tmp-gradle"))

    openjdk_with_docker = (
        context.dagger_client.container()
        # Use openjdk image because it's based on Debian. Alpine with Gradle and Python causes filesystem crash.
        .from_("openjdk:17.0.1-jdk-slim")
        .with_exec(["apt-get", "update"])
        .with_exec(["apt-get", "install", "-y", "curl", "jq"])
        .with_env_variable("VERSION", "23.0.1")
        .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
        .with_exec(["mkdir", "/root/.gradle"])
        .with_mounted_cache("/root/.gradle", root_gradle_cache, sharing=CacheSharingMode.LOCKED)
        .with_exec(["mkdir", "/airbyte"])
        .with_mounted_directory("/airbyte", context.get_repo_dir(".", include=include))
        .with_mounted_cache("/airbyte/.gradle", airbyte_gradle_cache, sharing=CacheSharingMode.LOCKED)
        .with_workdir("/airbyte")
    )
    return with_bound_docker_host(context, openjdk_with_docker, shared_tmp_volume, docker_cache_volume_name)


async def load_image_to_docker_host(context, tar_file: File, image_tag: str):
    # Hacky way to make sure the image is always loaded
    tar_name = f"{str(uuid.uuid4())}.tar"
    docker_cli = with_docker_cli(context).with_mounted_file(tar_name, tar_file)
    image_load_output = await docker_cli.with_exec(["docker", "load", "--input", tar_name]).stdout()
    if "sha256:" in image_load_output:
        image_id = image_load_output.replace("\n", "").replace("Loaded image ID: sha256:", "")
        await docker_cli.with_exec(["docker", "tag", image_id, image_tag]).exit_code()
