#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to create reusable environments packaged in dagger containers."""

from typing import List, Optional

from ci_connector_ops.pipelines.contexts import PipelineContext, ConnectorTestContext
from ci_connector_ops.pipelines.utils import get_file_contents
from dagger import CacheSharingMode, CacheVolume, Container, Directory, Secret

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

DEFAULT_PYTHON_EXCLUDE = ["**/.venv", "**/__pycache__"]
CI_CREDENTIALS_SOURCE_PATH = "tools/ci_credentials"
CI_CONNECTOR_OPS_SOURCE_PATH = "tools/ci_connector_ops"


def with_python_base(context: PipelineContext, python_image_name: str = "python:3.9-slim") -> Container:
    """Builds a Python container with a cache volume for pip cache.

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
        .with_mounted_cache("/root/.cache/pip", pip_cache, sharing=CacheSharingMode.LOCKED)
        .with_mounted_directory("/tools", context.get_repo_dir("tools", include=["ci_credentials", "ci_common_utils"], exclude=[".venv"]))
        .with_exec(["pip", "install", "--upgrade", "pip"])
    )

    return base_container


def with_testing_dependencies(context: PipelineContext) -> Container:
    """Builds a testing environment by installing testing dependencies on top of a python base environment.

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


async def with_installed_local_python_package(
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
    return await with_installed_local_python_package(
        context, testing_environment, connector_source_path, additional_dependency_groups=["dev", "tests", "main"], exclude=["secrets"]
    )


async def with_ci_credentials(context: PipelineContext, gsm_secret: Secret) -> Container:
    """Installs the ci_credentials package in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_local_python_package(context, python_base_environment, CI_CREDENTIALS_SOURCE_PATH)

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
    package_install_command = ["python", "-m", "pip", "install"]
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
    return await with_installed_local_python_package(context, python_with_git, CI_CONNECTOR_OPS_SOURCE_PATH, exclude=["pipelines"])


def with_poetry(context: PipelineContext) -> Container:
    """Installs poetry in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.

    Returns:
        Container: A python environment with poetry installed.
    """
    python_base_environment: Container = with_python_base(context, "python:3.9")
    python_with_git = with_debian_packages(python_base_environment, ["git"])
    python_with_poetry = with_pip_packages(python_with_git, ["poetry"])

    poetry_cache: CacheVolume = context.dagger_client.cache_volume("poetry_cache")
    poetry_with_cache = python_with_poetry.with_mounted_cache("/root/.cache/pypoetry", poetry_cache, sharing=CacheSharingMode.PRIVATE)

    return poetry_with_cache


def with_pipx(base_python_container: Container) -> Container:
    """Installs pipx in a python container.

    Args:
       base_python_container (Container): The container to install pipx on.

    Returns:
        Container: A python environment with pipx installed.
    """
    python_with_pipx = with_pip_packages(base_python_container, ["pipx"]).with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")

    return python_with_pipx


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
    )


def with_pipx_module(context: PipelineContext, parent_dir_path: str, module_path: str, include: List[str]) -> Container:
    """Installs a pipx module

    Args:
        context (PipelineContext): The current pipeline context
    Returns:
        Container: A python environment with dependencies installed using pipx.
    """
    pipx_include = [module_path] + include
    pipx_install_dependencies_cmd = ["pipx", "install", module_path]
    src = context.get_repo_dir(parent_dir_path, exclude=DEFAULT_PYTHON_EXCLUDE, include=pipx_include)

    python_base_environment = with_python_base(context, "python:3.9")
    python_with_pipx = with_pipx(python_base_environment)

    return python_with_pipx.with_mounted_directory("/src", src).with_workdir("/src").with_exec(pipx_install_dependencies_cmd)
