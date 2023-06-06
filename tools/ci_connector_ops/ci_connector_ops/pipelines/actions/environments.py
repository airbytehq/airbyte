#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to create reusable environments packaged in dagger containers."""

from __future__ import annotations

import importlib.util
import uuid
from typing import TYPE_CHECKING, List, Optional, Tuple

from ci_connector_ops.pipelines import consts
from ci_connector_ops.pipelines.consts import (
    CI_CONNECTOR_OPS_SOURCE_PATH,
    CI_CREDENTIALS_SOURCE_PATH,
    CONNECTOR_TESTING_REQUIREMENTS,
    DEFAULT_PYTHON_EXCLUDE,
    PYPROJECT_TOML_FILE_PATH,
)
from ci_connector_ops.pipelines.utils import get_file_contents, slugify, with_exit_code
from dagger import CacheSharingMode, CacheVolume, Container, Directory, File, Platform, Secret
from dagger.engine._version import CLI_VERSION as dagger_engine_version

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorContext, PipelineContext


def with_python_base(context: PipelineContext, python_image_name: str = "python:3.9-slim") -> Container:
    """Build a Python container with a cache volume for pip cache.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """
    if not python_image_name.startswith("python:3"):
        raise ValueError("You have to use a python image to build the python base environment")
    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    base_container = (
        context.dagger_client.container()
        .from_(python_image_name)
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_mounted_directory("/tools", context.get_repo_dir("tools", include=["ci_credentials", "ci_common_utils"]))
        .with_exec(["pip", "install", "--upgrade", "pip"])
    )

    return base_container


def with_testing_dependencies(context: PipelineContext) -> Container:
    """Build a testing environment by installing testing dependencies on top of a python base environment.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.

    Returns:
        Container: The testing environment container.
    """
    python_environment: Container = with_python_base(context)
    pyproject_toml_file = context.get_repo_dir(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)
    return python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS).with_file(
        f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file
    )


def with_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
) -> Container:
    """Load a python package source code to a python environment container.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
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
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    additional_dependency_groups: Optional[List] = None,
    exclude: Optional[List] = None,
) -> Container:
    """Install a python package in a python environment container.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package installed.
    """
    install_local_requirements_cmd = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
    install_connector_package_cmd = ["python", "-m", "pip", "install", "."]

    container = with_python_package(context, python_environment, package_source_code_path, exclude=exclude)
    if requirements_txt := await get_file_contents(container, "requirements.txt"):
        for line in requirements_txt.split("\n"):
            if line.startswith("-e ."):
                local_dependency_path = package_source_code_path + "/" + line[3:]
                container = container.with_mounted_directory(
                    "/" + local_dependency_path, context.get_repo_dir(local_dependency_path, exclude=DEFAULT_PYTHON_EXCLUDE)
                )
        container = container.with_exec(install_local_requirements_cmd)

    container = container.with_exec(install_connector_package_cmd)

    if additional_dependency_groups:
        container = container.with_exec(
            install_connector_package_cmd[:-1] + [install_connector_package_cmd[-1] + f"[{','.join(additional_dependency_groups)}]"]
        )

    return container


def with_python_connector_installed(context: ConnectorContext) -> Container:
    """Load an airbyte connector source code in a testing environment.

    Args:
        context (ConnectorContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector source code).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    return with_python_package(context, testing_environment, connector_source_path, exclude=["secrets"])


async def with_installed_airbyte_connector(context: ConnectorContext) -> Container:
    """Install an airbyte connector python package in a testing environment.

    Args:
        context (ConnectorContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector installed).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    return await with_installed_python_package(
        context, testing_environment, connector_source_path, additional_dependency_groups=["dev", "tests", "main"], exclude=["secrets"]
    )


async def with_ci_credentials(context: PipelineContext, gsm_secret: Secret) -> Container:
    """Install the ci_credentials package in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_python_package(context, python_base_environment, CI_CREDENTIALS_SOURCE_PATH)

    return ci_credentials.with_env_variable("VERSION", "dev").with_secret_variable("GCP_GSM_CREDENTIALS", gsm_secret).with_workdir("/")


def with_alpine_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using apk-get.
    Args:
        context (Container): A alpine based container.

    Returns:
        Container: A container with the packages installed.

    """
    package_install_command = ["apk", "add"]
    return base_container.with_exec(package_install_command + packages_to_install)


def with_debian_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using apt-get.
    Args:
        context (Container): A alpine based container.

    Returns:
        Container: A container with the packages installed.

    """
    update_packages_command = ["apt-get", "update"]
    package_install_command = ["apt-get", "install", "-y"]
    return base_container.with_exec(update_packages_command).with_exec(package_install_command + packages_to_install)


def with_pip_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using pip
    Args:
        context (Container): A container with python installed

    Returns:
        Container: A container with the pip packages installed.

    """
    package_install_command = ["pip", "install"]
    return base_container.with_exec(package_install_command + packages_to_install)


async def with_ci_connector_ops(context: PipelineContext) -> Container:
    """Installs the ci_connector_ops package in a Container running Python > 3.10 with git..

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_connector_sources sources will be pulled.

    Returns:
        Container: A python environment container with ci_connector_ops installed.
    """
    python_base_environment: Container = with_python_base(context, "python:3-alpine")
    python_with_git = with_alpine_packages(python_base_environment, ["gcc", "libffi-dev", "musl-dev", "git"])
    return await with_installed_python_package(context, python_with_git, CI_CONNECTOR_OPS_SOURCE_PATH, exclude=["pipelines"])


def with_dockerd_service(
    context: ConnectorContext, shared_volume: Optional(Tuple[str, CacheVolume]) = None, docker_service_name: Optional[str] = None
) -> Container:
    """Create a container running dockerd, exposing its 2375 port, can be used as the docker host for docker-in-docker use cases.

    Args:
        context (ConnectorContext): The current connector context.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be mounted to the dockerd container. Defaults to None.
        docker_service_name (Optional[str], optional): The name of the docker service, appended to volume name, useful context isolation. Defaults to None.

    Returns:
        Container: The container running dockerd as a service.
    """
    docker_lib_volume_name = f"{slugify(context.connector.technical_name)}-docker-lib"
    if docker_service_name:
        docker_lib_volume_name = f"{docker_lib_volume_name}-{slugify(docker_service_name)}"
    dind = (
        context.dagger_client.container()
        .from_(consts.DOCKER_DIND_IMAGE)
        .with_mounted_cache(
            "/var/lib/docker",
            context.dagger_client.cache_volume(docker_lib_volume_name),
            sharing=CacheSharingMode.SHARED,
        )
    )
    if shared_volume is not None:
        dind = dind.with_mounted_cache(*shared_volume)
    return dind.with_exposed_port(2375).with_exec(
        ["dockerd", "--log-level=error", "--host=tcp://0.0.0.0:2375", "--tls=false"], insecure_root_capabilities=True
    )


def with_bound_docker_host(
    context: ConnectorContext,
    container: Container,
    shared_volume: Optional(Tuple[str, CacheVolume]) = None,
    docker_service_name: Optional[str] = None,
) -> Container:
    """Bind a container to a docker host. It will use the dockerd service as a docker host.

    Args:
        context (ConnectorContext): The current connector context.
        container (Container): The container to bind to the docker host.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be both mounted to the container and the dockerd container. Defaults to None.
        docker_service_name (Optional[str], optional): The name of the docker service, useful context isolation. Defaults to None.

    Returns:
        Container: The container bound to the docker host.
    """
    dockerd = with_dockerd_service(context, shared_volume, docker_service_name)
    docker_hostname = f"dockerhost-{slugify(context.connector.technical_name)}"
    if docker_service_name:
        docker_hostname = f"{docker_hostname}-{slugify(docker_service_name)}"
    bound = container.with_env_variable("DOCKER_HOST", f"tcp://{docker_hostname}:2375").with_service_binding(docker_hostname, dockerd)
    if shared_volume:
        bound = bound.with_mounted_cache(*shared_volume)
    return bound


def with_docker_cli(
    context: ConnectorContext, shared_volume: Optional(Tuple[str, CacheVolume]) = None, docker_service_name: Optional[str] = None
) -> Container:
    """Create a container with the docker CLI installed and bound to a persistent docker host.

    Args:
        context (ConnectorContext): The current connector context.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be both mounted to the container and the dockerd container. Defaults to None.
        docker_service_name (Optional[str], optional): The name of the docker service, useful context isolation. Defaults to None.

    Returns:
        Container: A docker cli container bound to a docker host.
    """
    docker_cli = context.dagger_client.container().from_(consts.DOCKER_CLI_IMAGE)
    return with_bound_docker_host(context, docker_cli, shared_volume, docker_service_name)


async def with_connector_acceptance_test(context: ConnectorContext, connector_under_test_image_tar: File) -> Container:
    """Create a container to run connector acceptance tests, bound to a persistent docker host.

    Args:
        context (ConnectorContext): The current connector context.
        connector_under_test_image_tar (File): The file containing the tar archive the image of the connector under test.
    Returns:
        Container: A container with connector acceptance tests installed.
    """
    connector_under_test_image_name = context.connector.acceptance_test_config["connector_image"]
    await load_image_to_docker_host(context, connector_under_test_image_tar, connector_under_test_image_name, docker_service_name="cat")

    if context.connector_acceptance_test_image.endswith(":dev"):
        cat_container = context.connector_acceptance_test_source_dir.docker_build()
    else:
        cat_container = context.dagger_client.container().from_(context.connector_acceptance_test_image)
    shared_tmp_volume = ("/tmp", context.dagger_client.cache_volume("share-tmp-cat"))

    return (
        with_bound_docker_host(context, cat_container, shared_tmp_volume, docker_service_name="cat")
        .with_entrypoint([])
        .with_exec(["pip", "install", "pytest-custom_exit_code"])
        .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
        .with_mounted_directory("/test_input", context.get_connector_dir(exclude=["secrets", ".venv"]))
        .with_directory("/test_input/secrets", context.secrets_dir)
        .with_workdir("/test_input")
        .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "--suppress-tests-failed-exit-code"])
        .with_exec(["--acceptance-test-config", "/test_input"])
    )


def with_gradle(
    context: ConnectorContext,
    sources_to_include: List[str] = None,
    bind_to_docker_host: bool = True,
    docker_service_name: Optional[str] = "gradle",
) -> Container:
    """Create a container with Gradle installed and bound to a persistent docker host.

    Args:
        context (ConnectorContext): The current connector context.
        sources_to_include (List[str], optional): List of additional source path to mount to the container. Defaults to None.
        bind_to_docker_host (bool): Whether to bind the gradle container to a docker host.
        docker_service_name (Optional[str], optional): The name of the docker service, useful context isolation. Defaults to "gradle".

    Returns:
        Container: A container with Gradle installed and Java sources from the repository.
    """

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

    gradle_dependency_cache: CacheVolume = context.dagger_client.cache_volume("gradle-dependencies-caching")
    gradle_build_cache: CacheVolume = context.dagger_client.cache_volume(f"{context.connector.technical_name}-gradle-build-cache")

    shared_tmp_volume = ("/tmp", context.dagger_client.cache_volume("share-tmp-gradle"))

    openjdk_with_docker = (
        context.dagger_client.container()
        .from_("openjdk:17.0.1-jdk-slim")
        .with_exec(["apt-get", "update"])
        .with_exec(["apt-get", "install", "-y", "curl", "jq", "rsync"])
        .with_env_variable("VERSION", consts.DOCKER_VERSION)
        .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
        .with_env_variable("GRADLE_HOME", "/root/.gradle")
        .with_exec(["mkdir", "/airbyte"])
        .with_workdir("/airbyte")
        .with_mounted_directory("/airbyte", context.get_repo_dir(".", include=include))
        .with_exec(["mkdir", "-p", consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH])
        .with_mounted_cache(consts.GRADLE_BUILD_CACHE_PATH, gradle_build_cache, sharing=CacheSharingMode.LOCKED)
        .with_mounted_cache(consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH, gradle_dependency_cache)
        .with_env_variable("GRADLE_RO_DEP_CACHE", consts.GRADLE_READ_ONLY_DEPENDENCY_CACHE_PATH)
    )

    if bind_to_docker_host:
        return with_bound_docker_host(context, openjdk_with_docker, shared_tmp_volume, docker_service_name=docker_service_name)
    else:
        return openjdk_with_docker


async def load_image_to_docker_host(context: ConnectorContext, tar_file: File, image_tag: str, docker_service_name: Optional[str] = None):
    """Load a docker image tar archive to the docker host.

    Args:
        context (ConnectorContext): The current connector context.
        tar_file (File): The file object holding the docker image tar archive.
        image_tag (str): The tag to create on the image if it has no tag.
        docker_service_name (str): Name of the docker service, useful for context isolation.
    """
    # Hacky way to make sure the image is always loaded
    tar_name = f"{str(uuid.uuid4())}.tar"
    docker_cli = with_docker_cli(context, docker_service_name=docker_service_name).with_mounted_file(tar_name, tar_file)

    # Remove a previously existing image with the same tag if any.
    docker_image_rm_exit_code = await with_exit_code(
        docker_cli.with_env_variable("CACHEBUSTER", tar_name).with_exec(["docker", "image", "rm", image_tag])
    )
    if docker_image_rm_exit_code == 0:
        context.logger.info(f"Removed an existing image tagged {image_tag}")
    image_load_output = await docker_cli.with_exec(["docker", "load", "--input", tar_name]).stdout()
    context.logger.info(image_load_output)
    # Not tagged images only have a sha256 id the load output shares.
    if "sha256:" in image_load_output:
        image_id = image_load_output.replace("\n", "").replace("Loaded image ID: sha256:", "")
        docker_tag_output = await docker_cli.with_exec(["docker", "tag", image_id, image_tag]).stdout()
        context.logger.info(docker_tag_output)


def with_poetry(context: PipelineContext) -> Container:
    """Install poetry in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with poetry installed.
    """
    python_base_environment: Container = with_python_base(context, "python:3.9")
    python_with_git = with_debian_packages(python_base_environment, ["git"])
    python_with_poetry = with_pip_packages(python_with_git, ["poetry"])

    # poetry_cache: CacheVolume = context.dagger_client.cache_volume("poetry_cache")
    # poetry_with_cache = python_with_poetry.with_mounted_cache("/root/.cache/pypoetry", poetry_cache, sharing=CacheSharingMode.SHARED)

    return python_with_poetry


def with_poetry_module(context: PipelineContext, parent_dir: Directory, module_path: str) -> Container:
    """Sets up a Poetry module.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with dependencies installed using poetry.
    """
    poetry_install_dependencies_cmd = ["poetry", "install"]

    python_with_poetry = with_poetry(context)
    return (
        python_with_poetry.with_mounted_directory("/src", parent_dir)
        .with_workdir(f"/src/{module_path}")
        .with_exec(poetry_install_dependencies_cmd)
        .with_env_variable("CACHEBUSTER", str(uuid.uuid4()))
    )


def with_integration_base(context: PipelineContext, build_platform: Platform) -> Container:
    return (
        context.dagger_client.container(platform=build_platform)
        .from_("amazonlinux:2022.0.20220831.1")
        .with_workdir("/airbyte")
        .with_file("base.sh", context.get_repo_dir("airbyte-integrations/bases/base", include=["base.sh"]).file("base.sh"))
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        .with_label("io.airbyte.version", "0.1.0")
        .with_label("io.airbyte.name", "airbyte/integration-base")
    )


def with_integration_base_java(context: PipelineContext, build_platform: Platform, jdk_version: str = "17.0.4") -> Container:
    integration_base = with_integration_base(context, build_platform)
    return (
        context.dagger_client.container(platform=build_platform)
        .from_(f"amazoncorretto:{jdk_version}")
        .with_directory("/airbyte", integration_base.directory("/airbyte"))
        .with_exec(["yum", "install", "-y", "tar", "openssl"])
        .with_exec(["yum", "clean", "all"])
        .with_workdir("/airbyte")
        .with_file("dd-java-agent.jar", context.dagger_client.http("https://dtdg.co/latest-java-tracer"))
        .with_file("javabase.sh", context.get_repo_dir("airbyte-integrations/bases/base-java", include=["javabase.sh"]).file("javabase.sh"))
        .with_env_variable("AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
        .with_env_variable("AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
        .with_env_variable("AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
        .with_env_variable("AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
        .with_env_variable("AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        .with_label("io.airbyte.version", "0.1.2")
        .with_label("io.airbyte.name", "airbyte/integration-base-java")
    )


BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION = {
    "destination-bigquery": {
        "dockerfile": "Dockerfile",
        "dbt_adapter": "dbt-bigquery==1.0.0",
        "integration_name": "bigquery",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-clickhouse": {
        "dockerfile": "clickhouse.Dockerfile",
        "dbt_adapter": "dbt-clickhouse>=1.4.0",
        "integration_name": "clickhouse",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-duckdb": {
        "dockerfile": "duckdb.Dockerfile",
        "dbt_adapter": "dbt-duckdb==1.0.1",
        "integration_name": "duckdb",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-mssql": {
        "dockerfile": "mssql.Dockerfile",
        "dbt_adapter": "dbt-sqlserver==1.0.0",
        "integration_name": "mssql",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-mysql": {
        "dockerfile": "mysql.Dockerfile",
        "dbt_adapter": "dbt-mysql==1.0.0",
        "integration_name": "mysql",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-oracle": {
        "dockerfile": "oracle.Dockerfile",
        "dbt_adapter": "dbt-oracle==0.4.3",
        "integration_name": "oracle",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-postgres": {
        "dockerfile": "Dockerfile",
        "dbt_adapter": "dbt-postgres==1.0.0",
        "integration_name": "postgres",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-redshift": {
        "dockerfile": "redshift.Dockerfile",
        "dbt_adapter": "dbt-redshift==1.0.0",
        "integration_name": "redshift",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-snowflake": {
        "dockerfile": "snowflake.Dockerfile",
        "dbt_adapter": "dbt-snowflake==1.0.0",
        "integration_name": "snowflake",
        "supports_in_connector_normalization": True,
        "yum_packages": ["gcc-c++"],
    },
    "destination-tidb": {
        "dockerfile": "tidb.Dockerfile",
        "dbt_adapter": "dbt-tidb==1.0.1",
        "integration_name": "tidb",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
}

DESTINATION_NORMALIZATION_BUILD_CONFIGURATION = {
    **BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION,
    **{f"{k}-strict-encrypt": v for k, v in BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION.items()},
}


def with_normalization(context: ConnectorContext) -> Container:
    normalization_directory = context.get_repo_dir("airbyte-integrations/bases/base-normalization")
    sshtunneling_file = context.get_repo_dir(
        "airbyte-connector-test-harnesses/acceptance-test-harness/src/main/resources", include="sshtunneling.sh"
    ).file("sshtunneling.sh")
    normalization_directory_with_build = normalization_directory.with_new_directory("build")
    normalization_directory_with_sshtunneling = normalization_directory_with_build.with_file("build/sshtunneling.sh", sshtunneling_file)
    normalization_dockerfile_name = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["dockerfile"]
    return normalization_directory_with_sshtunneling.docker_build(normalization_dockerfile_name)


def with_integration_base_java_and_normalization(context: PipelineContext, build_platform: Platform) -> Container:
    yum_packages_to_install = [
        "python3",
        "python3-devel",
        "jq",
        "sshpass",
        "git",
    ]

    additional_yum_packages = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["yum_packages"]
    yum_packages_to_install += additional_yum_packages

    dbt_adapter_package = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["dbt_adapter"]
    normalization_integration_name = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["integration_name"]

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    return (
        with_integration_base_java(context, build_platform)
        .with_exec(["yum", "install", "-y"] + yum_packages_to_install)
        .with_exec(["alternatives", "--install", "/usr/bin/python", "python", "/usr/bin/python3", "60"])
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(["python", "-m", "ensurepip", "--upgrade"])
        .with_exec(["pip3", "install", dbt_adapter_package])
        .with_directory("airbyte_normalization", with_normalization(context).directory("/airbyte"))
        .with_workdir("airbyte_normalization")
        .with_exec(["sh", "-c", "mv * .."])
        .with_workdir("/airbyte")
        .with_exec(["rm", "-rf", "airbyte_normalization"])
        .with_workdir("/airbyte/base_python_structs")
        .with_exec(["pip3", "install", "."])
        .with_workdir("/airbyte/normalization_code")
        .with_exec(["pip3", "install", "."])
        .with_workdir("/airbyte/normalization_code/dbt-template/")
        # amazon linux 2 isn't compatible with urllib3 2.x, so force 1.x
        .with_exec(["pip3", "install", "urllib3<2"])
        .with_exec(["dbt", "deps"])
        .with_workdir("/airbyte")
        .with_file(
            "run_with_normalization.sh",
            context.get_repo_dir("airbyte-integrations/bases/base-java", include=["run_with_normalization.sh"]).file(
                "run_with_normalization.sh"
            ),
        )
        .with_env_variable("AIRBYTE_NORMALIZATION_INTEGRATION", normalization_integration_name)
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/run_with_normalization.sh")
    )


async def with_airbyte_java_connector(context: ConnectorContext, connector_java_tar_file: File, build_platform: Platform) -> Container:
    application = context.connector.technical_name

    build_stage = (
        with_integration_base_java(context, build_platform)
        .with_workdir("/airbyte")
        .with_env_variable("APPLICATION", context.connector.technical_name)
        .with_file(f"{application}.tar", connector_java_tar_file)
        .with_exec(["tar", "xf", f"{application}.tar", "--strip-components=1"])
        .with_exec(["rm", "-rf", f"{application}.tar"])
    )

    if (
        context.connector.supports_normalization
        and DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["supports_in_connector_normalization"]
    ):
        base = with_integration_base_java_and_normalization(context, build_platform)
        entrypoint = ["/airbyte/run_with_normalization.sh"]
    else:
        base = with_integration_base_java(context, build_platform)
        entrypoint = ["/airbyte/base.sh"]

    connector_container = (
        base.with_workdir("/airbyte")
        .with_env_variable("APPLICATION", application)
        .with_mounted_directory("builts_artifacts", build_stage.directory("/airbyte"))
        .with_exec(["sh", "-c", "mv builts_artifacts/* ."])
        .with_label("io.airbyte.version", context.metadata["dockerImageTag"])
        .with_label("io.airbyte.name", context.metadata["dockerRepository"])
        .with_entrypoint(entrypoint)
    )
    return await finalize_build(context, connector_container)


async def get_cdk_version_from_python_connector(python_connector: Container) -> Optional[str]:
    pip_freeze_stdout = await python_connector.with_entrypoint("pip").with_exec(["freeze"]).stdout()
    pip_dependencies = [dep.split("==") for dep in pip_freeze_stdout.split("\n")]
    for package_name, package_version in pip_dependencies:
        if package_name == "airbyte-cdk":
            return package_version
    return None


async def with_airbyte_python_connector(context: ConnectorContext, build_platform: Platform) -> Container:
    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")
    connector_container = (
        context.dagger_client.container(platform=build_platform)
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .build(context.get_connector_dir())
        .with_label("io.airbyte.version", context.metadata["dockerImageTag"])
        .with_label("io.airbyte.name", context.metadata["dockerRepository"])
    )
    cdk_version = await get_cdk_version_from_python_connector(connector_container)
    if cdk_version:
        connector_container = connector_container.with_label("io.airbyte.cdk_version", cdk_version)
        context.cdk_version = cdk_version
    return await finalize_build(context, connector_container)


async def finalize_build(context: ConnectorContext, connector_container: Container) -> Container:
    """Finalize build by adding dagger engine version label and running finalize_build.sh or finalize_build.py if present in the connector directory."""
    connector_container = connector_container.with_label("io.dagger.engine_version", dagger_engine_version)
    connector_dir_with_finalize_script = context.get_connector_dir(include=["finalize_build.sh", "finalize_build.py"])
    finalize_scripts = await connector_dir_with_finalize_script.entries()
    if not finalize_scripts:
        return connector_container

    # We don't want finalize scripts to override the entrypoint so we keep it in memory to reset it after finalization
    original_entrypoint = await connector_container.entrypoint()

    has_finalize_bash_script = "finalize_build.sh" in finalize_scripts
    has_finalize_python_script = "finalize_build.py" in finalize_scripts
    if has_finalize_python_script and has_finalize_bash_script:
        raise Exception("Connector has both finalize_build.sh and finalize_build.py, please remove one of them")

    if has_finalize_python_script:
        context.logger.info(f"{context.connector.technical_name} has a finalize_build.py script, running it to finalize build...")
        module_path = context.connector.code_directory / "finalize_build.py"
        connector_finalize_module_spec = importlib.util.spec_from_file_location(
            f"{context.connector.code_directory.name}_finalize", module_path
        )
        connector_finalize_module = importlib.util.module_from_spec(connector_finalize_module_spec)
        connector_finalize_module_spec.loader.exec_module(connector_finalize_module)
        try:
            connector_container = await connector_finalize_module.finalize_build(context, connector_container)
        except AttributeError:
            raise Exception("Connector has a finalize_build.py script but it doesn't have a finalize_build function.")

    if has_finalize_bash_script:
        context.logger.info(f"{context.connector.technical_name} has finalize_build.sh script, running it to finalize build...")
        connector_container = (
            connector_container.with_file("/tmp/finalize_build.sh", connector_dir_with_finalize_script.file("finalize_build.sh"))
            .with_entrypoint("sh")
            .with_exec(["/tmp/finalize_build.sh"])
        )

    return connector_container.with_entrypoint(original_entrypoint)


# This function is not used at the moment as we decided to use Python connectors dockerfile instead of building it with dagger.
# Some python connectors use alpine base image, other use debian... We should unify this.
def with_airbyte_python_connector_full_dagger(context: ConnectorContext, build_platform: Platform) -> Container:
    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")
    base = context.dagger_client.container(platform=build_platform).from_("python:3.9.11-alpine3.15")
    snake_case_name = context.connector.technical_name.replace("-", "_")
    entrypoint = ["python", "/airbyte/integration_code/main.py"]
    builder = (
        base.with_workdir("/airbyte/integration_code")
        .with_exec(["apk", "--no-cache", "upgrade"])
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(["pip", "install", "--upgrade", "pip"])
        .with_exec(["apk", "--no-cache", "add", "tzdata", "build-base"])
        .with_file("setup.py", context.get_connector_dir(include="setup.py").file("setup.py"))
        .with_exec(["pip", "install", "--prefix=/install", "."])
    )
    return (
        base.with_workdir("/airbyte/integration_code")
        .with_directory("/usr/local", builder.directory("/install"))
        .with_file("/usr/localtime", builder.file("/usr/share/zoneinfo/Etc/UTC"))
        .with_new_file("/etc/timezone", "Etc/UTC")
        .with_exec(["apk", "--no-cache", "add", "bash"])
        .with_file("main.py", context.get_connector_dir(include="main.py").file("main.py"))
        .with_directory(snake_case_name, context.get_connector_dir(include=snake_case_name).directory(snake_case_name))
        .with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(entrypoint))
        .with_entrypoint(entrypoint)
        .with_label("io.airbyte.version", context.metadata["dockerImageTag"])
        .with_label("io.airbyte.name", context.metadata["dockerRepository"])
    )


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
                ["sh", "-c", "crane auth login index.docker.io -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD"], skip_entrypoint=True
            )
        )

    return base_container
