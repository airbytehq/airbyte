#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to create reusable environments packaged in dagger containers."""

from __future__ import annotations

import importlib.util
import json
import re
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

import toml
from dagger import CacheVolume, Client, Container, Directory, File, Platform, Secret
from dagger.engine._version import CLI_VERSION as dagger_engine_version
from pipelines import consts
from pipelines.consts import (
    AMAZONCORRETTO_IMAGE,
    CONNECTOR_TESTING_REQUIREMENTS,
    DOCKER_HOST_NAME,
    DOCKER_HOST_PORT,
    DOCKER_TMP_VOLUME_NAME,
    LICENSE_SHORT_FILE_PATH,
    PYPROJECT_TOML_FILE_PATH,
)
from pipelines.tools.internal import INTERNAL_TOOL_PATHS
from pipelines.utils import check_path_in_workdir, get_file_contents, sh_dash_c

if TYPE_CHECKING:
    from pipelines.contexts import ConnectorContext, PipelineContext


def with_python_base(context: PipelineContext, python_version: str = "3.10") -> Container:
    """Build a Python container with a cache volume for pip cache.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    base_container = (
        context.dagger_client.container()
        .from_(f"python:{python_version}-slim")
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(
            sh_dash_c(
                [
                    "apt-get update",
                    "apt-get install -y build-essential cmake g++ libffi-dev libstdc++6 git",
                    "pip install pip==23.1.2",
                ]
            )
        )
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
    license_short_file = context.get_repo_dir(".", include=[LICENSE_SHORT_FILE_PATH]).file(LICENSE_SHORT_FILE_PATH)

    return (
        python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS)
        .with_file(f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file)
        .with_file(f"/{LICENSE_SHORT_FILE_PATH}", license_short_file)
    )


def with_git(dagger_client, ci_git_user: str = "octavia") -> Container:
    return (
        dagger_client.container()
        .from_("alpine:latest")
        .with_exec(
            sh_dash_c(
                [
                    "apk update",
                    "apk add git tar wget",
                    f"git config --global user.email {ci_git_user}@users.noreply.github.com",
                    f"git config --global user.name {ci_git_user}",
                    "git config --global --add --bool push.autoSetupRemote true",
                ]
            )
        )
        .with_workdir("/ghcli")
        .with_exec(
            sh_dash_c(
                [
                    "wget https://github.com/cli/cli/releases/download/v2.30.0/gh_2.30.0_linux_amd64.tar.gz -O ghcli.tar.gz",
                    "tar --strip-components=1 -xf ghcli.tar.gz",
                    "rm ghcli.tar.gz",
                    "cp bin/gh /usr/local/bin/gh",
                ]
            )
        )
    )


async def with_installed_pipx_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
) -> Container:
    """Install a python package in a python environment container using pipx.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package installed.
    """
    pipx_python_environment = with_pipx(python_environment)
    container = with_python_package(context, pipx_python_environment, package_source_code_path, exclude=exclude)

    local_dependencies = await find_local_dependencies_in_pyproject_toml(context, container, package_source_code_path, exclude=exclude)
    for dependency_directory in local_dependencies:
        container = container.with_mounted_directory("/" + dependency_directory, context.get_repo_dir(dependency_directory))

    container = container.with_exec(["pipx", "install", f"/{package_source_code_path}"])

    return container


def with_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
    include: Optional[List] = None,
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
    package_source_code_directory: Directory = context.get_repo_dir(package_source_code_path, exclude=exclude, include=include)
    work_dir_path = f"/{package_source_code_path}"
    container = python_environment.with_mounted_directory(work_dir_path, package_source_code_directory).with_workdir(work_dir_path)
    return container


async def find_local_python_dependencies(
    context: PipelineContext,
    package_source_code_path: str,
    search_dependencies_in_setup_py: bool = True,
    search_dependencies_in_requirements_txt: bool = True,
) -> List[str]:
    """Find local python dependencies of a python package. The dependencies are found in the setup.py and requirements.txt files.

    Args:
        context (PipelineContext): The current pipeline context, providing a dagger client and a repository directory.
        package_source_code_path (str): The local path to the python package source code.
        search_dependencies_in_setup_py (bool, optional): Whether to search for local dependencies in the setup.py file. Defaults to True.
        search_dependencies_in_requirements_txt (bool, optional): Whether to search for local dependencies in the requirements.txt file. Defaults to True.

    Returns:
        List[str]: Paths to the local dependencies relative to the airbyte repo.
    """
    python_environment = with_python_base(context)
    container = with_python_package(context, python_environment, package_source_code_path)

    local_dependency_paths = []
    if search_dependencies_in_setup_py:
        local_dependency_paths += await find_local_dependencies_in_setup_py(container)
    if search_dependencies_in_requirements_txt:
        local_dependency_paths += await find_local_dependencies_in_requirements_txt(container, package_source_code_path)

    transitive_dependency_paths = []
    for local_dependency_path in local_dependency_paths:
        # Transitive local dependencies installation is achieved by calling their setup.py file, not their requirements.txt file.
        transitive_dependency_paths += await find_local_python_dependencies(context, local_dependency_path, True, False)

    all_dependency_paths = local_dependency_paths + transitive_dependency_paths
    if all_dependency_paths:
        context.logger.debug(f"Found local dependencies for {package_source_code_path}: {all_dependency_paths}")
    return all_dependency_paths


async def find_local_dependencies_in_setup_py(python_package: Container) -> List[str]:
    """Find local dependencies of a python package in its setup.py file.

    Args:
        python_package (Container): A python package container.

    Returns:
        List[str]: Paths to the local dependencies relative to the airbyte repo.
    """
    setup_file_content = await get_file_contents(python_package, "setup.py")
    if not setup_file_content:
        return []

    local_setup_dependency_paths = []
    with_egg_info = python_package.with_exec(["python", "setup.py", "egg_info"])
    egg_info_output = await with_egg_info.stdout()
    dependency_in_requires_txt = []
    for line in egg_info_output.split("\n"):
        if line.startswith("writing requirements to"):
            # Find the path to the requirements.txt file that was generated by calling egg_info
            requires_txt_path = line.replace("writing requirements to", "").strip()
            requirements_txt_content = await with_egg_info.file(requires_txt_path).contents()
            dependency_in_requires_txt = requirements_txt_content.split("\n")

    for dependency_line in dependency_in_requires_txt:
        if "file://" in dependency_line:
            match = re.search(r"file:///(.+)", dependency_line)
            if match:
                local_setup_dependency_paths.append([match.group(1)][0])
    return local_setup_dependency_paths


async def find_local_dependencies_in_requirements_txt(python_package: Container, package_source_code_path: str) -> List[str]:
    """Find local dependencies of a python package in a requirements.txt file.

    Args:
        python_package (Container): A python environment container with the python package source code.
        package_source_code_path (str): The local path to the python package source code.

    Returns:
        List[str]: Paths to the local dependencies relative to the airbyte repo.
    """
    requirements_txt_content = await get_file_contents(python_package, "requirements.txt")
    if not requirements_txt_content:
        return []

    local_requirements_dependency_paths = []
    for line in requirements_txt_content.split("\n"):
        # Some package declare themselves as a requirement in requirements.txt,
        # #Without line != "-e ." the package will be considered a dependency of itself which can cause an infinite loop
        if line.startswith("-e .") and line != "-e .":
            local_dependency_path = Path(line[3:])
            package_source_code_path = Path(package_source_code_path)
            local_dependency_path = str((package_source_code_path / local_dependency_path).resolve().relative_to(Path.cwd()))
            local_requirements_dependency_paths.append(local_dependency_path)
    return local_requirements_dependency_paths


async def find_local_dependencies_in_pyproject_toml(
    context: PipelineContext,
    base_container: Container,
    pyproject_file_path: str,
    exclude: Optional[List] = None,
) -> list:
    """Find local dependencies of a python package in a pyproject.toml file.

    Args:
        python_package (Container): A python environment container with the python package source code.
        pyproject_file_path (str): The path to the pyproject.toml file.

    Returns:
        list: Paths to the local dependencies relative to the current directory.
    """
    python_package = with_python_package(context, base_container, pyproject_file_path)
    pyproject_content_raw = await get_file_contents(python_package, "pyproject.toml")
    if not pyproject_content_raw:
        return []

    pyproject_content = toml.loads(pyproject_content_raw)
    local_dependency_paths = []
    for dep, value in pyproject_content["tool"]["poetry"]["dependencies"].items():
        if isinstance(value, dict) and "path" in value:
            local_dependency_path = Path(value["path"])
            pyproject_file_path = Path(pyproject_file_path)
            local_dependency_path = str((pyproject_file_path / local_dependency_path).resolve().relative_to(Path.cwd()))
            local_dependency_paths.append(local_dependency_path)

            # Ensure we parse the child dependencies
            # TODO handle more than pyproject.toml
            child_local_dependencies = await find_local_dependencies_in_pyproject_toml(
                context, base_container, local_dependency_path, exclude=exclude
            )
            local_dependency_paths += child_local_dependencies

    return local_dependency_paths


def _install_python_dependencies_from_setup_py(
    container: Container,
    additional_dependency_groups: Optional[List] = None,
) -> Container:
    install_connector_package_cmd = ["pip", "install", "."]
    container = container.with_exec(install_connector_package_cmd)

    if additional_dependency_groups:
        # e.g. .[dev,tests]
        group_string = f".[{','.join(additional_dependency_groups)}]"
        group_install_cmd = ["pip", "install", group_string]

        container = container.with_exec(group_install_cmd)

    return container


def _install_python_dependencies_from_requirements_txt(container: Container) -> Container:
    install_requirements_cmd = ["pip", "install", "-r", "requirements.txt"]
    return container.with_exec(install_requirements_cmd)


def _install_python_dependencies_from_poetry(
    container: Container,
    additional_dependency_groups: Optional[List] = None,
) -> Container:
    pip_install_poetry_cmd = ["pip", "install", "poetry"]
    poetry_disable_virtual_env_cmd = ["poetry", "config", "virtualenvs.create", "false"]
    poetry_install_no_venv_cmd = ["poetry", "install"]
    if additional_dependency_groups:
        for group in additional_dependency_groups:
            poetry_install_no_venv_cmd += ["--with", group]

    return container.with_exec(pip_install_poetry_cmd).with_exec(poetry_disable_virtual_env_cmd).with_exec(poetry_install_no_venv_cmd)


async def with_installed_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    additional_dependency_groups: Optional[List] = None,
    exclude: Optional[List] = None,
    include: Optional[List] = None,
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
    container = with_python_package(context, python_environment, package_source_code_path, exclude=exclude, include=include)

    local_dependencies = await find_local_python_dependencies(context, package_source_code_path)

    for dependency_directory in local_dependencies:
        container = container.with_mounted_directory("/" + dependency_directory, context.get_repo_dir(dependency_directory))

    has_setup_py = await check_path_in_workdir(container, "setup.py")
    has_requirements_txt = await check_path_in_workdir(container, "requirements.txt")
    has_pyproject_toml = await check_path_in_workdir(container, "pyproject.toml")

    if has_pyproject_toml:
        container = _install_python_dependencies_from_poetry(container, additional_dependency_groups)
    elif has_setup_py:
        container = _install_python_dependencies_from_setup_py(container, additional_dependency_groups)
    elif has_requirements_txt:
        container = _install_python_dependencies_from_requirements_txt(container)

    return container


def with_python_connector_source(context: ConnectorContext) -> Container:
    """Load an airbyte connector source code in a testing environment.

    Args:
        context (ConnectorContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector source code).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)

    return with_python_package(context, testing_environment, connector_source_path)


async def apply_python_development_overrides(context: ConnectorContext, connector_container: Container) -> Container:
    # Run the connector using the local cdk if flag is set
    if context.use_local_cdk:
        context.logger.info("Using local CDK")
        # mount the local cdk
        path_to_cdk = "airbyte-cdk/python/"
        directory_to_mount = context.get_repo_dir(path_to_cdk)

        context.logger.info(f"Mounting CDK from {directory_to_mount}")

        # Install the airbyte-cdk package from the local directory
        # We use --no-deps to avoid conflicts with the airbyte-cdk version required by the connector
        connector_container = connector_container.with_mounted_directory(f"/{path_to_cdk}", directory_to_mount).with_exec(
            ["pip", "install", "--no-deps", f"/{path_to_cdk}"], skip_entrypoint=True
        )

    return connector_container


async def with_python_connector_installed(
    context: PipelineContext,
    python_container: Container,
    connector_source_path: str,
    additional_dependency_groups: Optional[List] = None,
    exclude: Optional[List] = None,
    include: Optional[List] = None,
) -> Container:
    """Install an airbyte python connectors  dependencies."""
    container = await with_installed_python_package(
        context,
        python_container,
        connector_source_path,
        additional_dependency_groups=additional_dependency_groups,
        exclude=exclude,
        include=include,
    )

    container = await apply_python_development_overrides(context, container)

    return container


async def with_ci_credentials(context: PipelineContext, gsm_secret: Secret) -> Container:
    """Install the ci_credentials package in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_pipx_package(context, python_base_environment, INTERNAL_TOOL_PATHS.CI_CREDENTIALS.value)
    ci_credentials = ci_credentials.with_env_variable("VERSION", "dagger_ci")
    return ci_credentials.with_secret_variable("GCP_GSM_CREDENTIALS", gsm_secret).with_workdir("/")


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


async def with_connector_ops(context: PipelineContext) -> Container:
    """Installs the connector_ops package in a Container running Python > 3.10 with git..

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_connector_sources sources will be pulled.

    Returns:
        Container: A python environment container with connector_ops installed.
    """
    python_base_environment: Container = with_python_base(context)

    return await with_installed_pipx_package(context, python_base_environment, INTERNAL_TOOL_PATHS.CONNECTOR_OPS.value)


def with_global_dockerd_service(dagger_client: Client) -> Container:
    """Create a container with a docker daemon running.
    We expose its 2375 port to use it as a docker host for docker-in-docker use cases.
    Args:
        dagger_client (Client): The dagger client used to create the container.
    Returns:
        Container: The container running dockerd as a service
    """
    return (
        dagger_client.container().from_(consts.DOCKER_DIND_IMAGE)
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
        .with_mounted_cache("/tmp", dagger_client.cache_volume(DOCKER_TMP_VOLUME_NAME))
        # Run the docker daemon and bind it to the exposed TCP port.
        .with_exec(
            ["dockerd", "--log-level=error", f"--host=tcp://0.0.0.0:{DOCKER_HOST_PORT}", "--tls=false"], insecure_root_capabilities=True
        )
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


def with_pipx(base_python_container: Container) -> Container:
    """Installs pipx in a python container.

    Args:
       base_python_container (Container): The container to install pipx on.

    Returns:
        Container: A python environment with pipx installed.
    """
    python_with_pipx = with_pip_packages(base_python_container, ["pipx"]).with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")

    return python_with_pipx


def with_poetry(context: PipelineContext) -> Container:
    """Install poetry in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with poetry installed.
    """
    python_base_environment: Container = with_python_base(context)
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


def with_integration_base_java(context: PipelineContext, build_platform: Platform) -> Container:
    integration_base = with_integration_base(context, build_platform)
    yum_packages_to_install = [
        "tar",  # required to untar java connector binary distributions.
        "openssl",  # required because we need to ssh and scp sometimes.
        "findutils",  # required for xargs, which is shipped as part of findutils.
    ]
    return (
        context.dagger_client.container(platform=build_platform)
        # Use a linux+jdk base image with long-term support, such as amazoncorretto.
        .from_(AMAZONCORRETTO_IMAGE)
        # Install a bunch of packages as early as possible.
        .with_exec(
            sh_dash_c(
                [
                    # Update first, but in the same .with_exec step as the package installation.
                    # Otherwise, we risk caching stale package URLs.
                    "yum update -y",
                    #
                    f"yum install -y {' '.join(yum_packages_to_install)}",
                    # Remove any dangly bits.
                    "yum clean all",
                ]
            )
        )
        # Add what files we need to the /airbyte directory.
        # Copy base.sh from the airbyte/integration-base image.
        .with_directory("/airbyte", integration_base.directory("/airbyte"))
        .with_workdir("/airbyte")
        # Download a utility jar from the internet.
        .with_file("dd-java-agent.jar", context.dagger_client.http("https://dtdg.co/latest-java-tracer"))
        # Copy javabase.sh from the git repo.
        .with_file("javabase.sh", context.get_repo_dir("airbyte-integrations/bases/base-java", include=["javabase.sh"]).file("javabase.sh"))
        # Set a bunch of env variables used by base.sh.
        .with_env_variable("AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
        .with_env_variable("AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
        .with_env_variable("AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
        .with_env_variable("AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
        .with_env_variable("AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        # Set image labels.
        .with_label("io.airbyte.version", "0.1.2")
        .with_label("io.airbyte.name", "airbyte/integration-base-java")
    )


BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION = {
    "destination-clickhouse": {
        "dockerfile": "clickhouse.Dockerfile",
        "dbt_adapter": "dbt-clickhouse>=1.4.0",
        "integration_name": "clickhouse",
        "normalization_image": "airbyte/normalization-clickhouse:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-duckdb": {
        "dockerfile": "duckdb.Dockerfile",
        "dbt_adapter": "dbt-duckdb==1.0.1",
        "integration_name": "duckdb",
        "normalization_image": "airbyte/normalization-duckdb:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-mssql": {
        "dockerfile": "mssql.Dockerfile",
        "dbt_adapter": "dbt-sqlserver==1.0.0",
        "integration_name": "mssql",
        "normalization_image": "airbyte/normalization-mssql:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-mysql": {
        "dockerfile": "mysql.Dockerfile",
        "dbt_adapter": "dbt-mysql==1.0.0",
        "integration_name": "mysql",
        "normalization_image": "airbyte/normalization-mysql:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-oracle": {
        "dockerfile": "oracle.Dockerfile",
        "dbt_adapter": "dbt-oracle==0.4.3",
        "integration_name": "oracle",
        "normalization_image": "airbyte/normalization-oracle:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-postgres": {
        "dockerfile": "Dockerfile",
        "dbt_adapter": "dbt-postgres==1.0.0",
        "integration_name": "postgres",
        "normalization_image": "airbyte/normalization:0.4.3",
        "supports_in_connector_normalization": False,
        "yum_packages": [],
    },
    "destination-redshift": {
        "dockerfile": "redshift.Dockerfile",
        "dbt_adapter": "dbt-redshift==1.0.0",
        "integration_name": "redshift",
        "normalization_image": "airbyte/normalization-redshift:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
    "destination-tidb": {
        "dockerfile": "tidb.Dockerfile",
        "dbt_adapter": "dbt-tidb==1.0.1",
        "integration_name": "tidb",
        "normalization_image": "airbyte/normalization-tidb:0.4.3",
        "supports_in_connector_normalization": True,
        "yum_packages": [],
    },
}

DESTINATION_NORMALIZATION_BUILD_CONFIGURATION = {
    **BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION,
    **{f"{k}-strict-encrypt": v for k, v in BASE_DESTINATION_NORMALIZATION_BUILD_CONFIGURATION.items()},
}


def with_normalization(context: ConnectorContext, build_platform: Platform) -> Container:
    return context.dagger_client.container(platform=build_platform).from_(
        DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["normalization_image"]
    )


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
        .with_exec(
            sh_dash_c(
                [
                    "yum update -y",
                    f"yum install -y {' '.join(yum_packages_to_install)}",
                    "yum clean all",
                    "alternatives --install /usr/bin/python python /usr/bin/python3 60",
                ]
            )
        )
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(
            sh_dash_c(
                [
                    "python -m ensurepip --upgrade",
                    # Workaround for https://github.com/yaml/pyyaml/issues/601
                    "pip3 install 'Cython<3.0' 'pyyaml~=5.4' --no-build-isolation",
                    # Required for dbt https://github.com/dbt-labs/dbt-core/issues/7075
                    "pip3 install 'pytz~=2023.3'",
                    f"pip3 install {dbt_adapter_package}",
                    # amazon linux 2 isn't compatible with urllib3 2.x, so force 1.x
                    "pip3 install 'urllib3<2'",
                ]
            )
        )
        .with_directory("airbyte_normalization", with_normalization(context, build_platform).directory("/airbyte"))
        .with_workdir("airbyte_normalization")
        .with_exec(sh_dash_c(["mv * .."]))
        .with_workdir("/airbyte")
        .with_exec(["rm", "-rf", "airbyte_normalization"])
        .with_workdir("/airbyte/normalization_code")
        .with_exec(["pip3", "install", "."])
        .with_workdir("/airbyte/normalization_code/dbt-template/")
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
        .with_exec(
            sh_dash_c(
                [
                    f"tar xf {application}.tar --strip-components=1",
                    f"rm -rf {application}.tar",
                ]
            )
        )
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
        .with_mounted_directory("built_artifacts", build_stage.directory("/airbyte"))
        .with_exec(sh_dash_c(["mv built_artifacts/* ."]))
        .with_label("io.airbyte.version", context.metadata["dockerImageTag"])
        .with_label("io.airbyte.name", context.metadata["dockerRepository"])
        .with_entrypoint(entrypoint)
    )
    return await finalize_build(context, connector_container)


async def finalize_build(context: ConnectorContext, connector_container: Container) -> Container:
    """Finalize build by adding dagger engine version label and running finalize_build.sh or finalize_build.py if present in the connector directory."""
    connector_container = connector_container.with_label("io.dagger.engine_version", dagger_engine_version)
    connector_dir_with_finalize_script = await context.get_connector_dir(include=["finalize_build.sh", "finalize_build.py"])
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


async def mounted_connector_secrets(context: PipelineContext, secret_directory_path: str) -> Callable[[Container], Container]:
    # By default, mount the secrets properly as dagger secret files.
    #
    # This will cause the contents of these files to be scrubbed from the logs. This scrubbing comes at the cost of
    # unavoidable latency in the log output, see next paragraph for details as to why. This is fine in a CI environment
    # however this becomes a nuisance locally: the developer wants the logs to be displayed to them in an as timely
    # manner as possible. Since the secrets aren't really secret in that case anyway, we mount them in the container as
    # regular files instead.
    #
    # The buffering behavior that comes into play when logs are scrubbed is both unavoidable and not configurable.
    # It's fundamentally unavoidable because dagger needs to match a bunch of regexes (one per secret) and therefore
    # needs to buffer at least as many bytes as the longest of all possible matches. Still, this isn't that long in
    # practice in our case. The real problem is that the buffering is not configurable: dagger relies on a golang
    # library called transform [1] to perform the regexp matching on a stream and this library hard-codes a buffer
    # size of 4096 bytes for each regex [2].
    #
    # Remove the special local case whenever dagger implements scrubbing differently [3,4].
    #
    # [1] https://golang.org/x/text/transform
    # [2] https://cs.opensource.google/go/x/text/+/refs/tags/v0.13.0:transform/transform.go;l=130
    # [3] https://github.com/dagger/dagger/blob/v0.6.4/cmd/shim/main.go#L294
    # [4] https://github.com/airbytehq/airbyte/issues/30394
    #
    if context.is_local:
        # Special case for local development.
        # Query dagger for the contents of the secrets and mount these strings as files in the container.
        contents = {}
        for secret_file_name, secret in context.connector_secrets.items():
            contents[secret_file_name] = await secret.plaintext()

        def with_secrets_mounted_as_regular_files(container: Container) -> Container:
            container = container.with_exec(["mkdir", "-p", secret_directory_path], skip_entrypoint=True)
            for secret_file_name, secret_content_str in contents.items():
                container = container.with_new_file(f"{secret_directory_path}/{secret_file_name}", secret_content_str, permissions=0o600)
            return container

        return with_secrets_mounted_as_regular_files

    def with_secrets_mounted_as_dagger_secrets(container: Container) -> Container:
        container = container.with_exec(["mkdir", "-p", secret_directory_path], skip_entrypoint=True)
        for secret_file_name, secret in context.connector_secrets.items():
            container = container.with_mounted_secret(f"{secret_directory_path}/{secret_file_name}", secret)
        return container

    return with_secrets_mounted_as_dagger_secrets
