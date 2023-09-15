import uuid
import toml
from pathlib import Path
from pipelines.actions.environments.os.debian import with_debian_packages
from pipelines.actions.environments.python.common import with_pip_packages, with_python_base, with_python_package
from pipelines.contexts import PipelineContext


from dagger import Container, Directory


from typing import List, Optional

from pipelines.utils import get_file_contents


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


def with_pipx(base_python_container: Container) -> Container:
    """Installs pipx in a python container.

    Args:
       base_python_container (Container): The container to install pipx on.

    Returns:
        Container: A python environment with pipx installed.
    """
    python_with_pipx = with_pip_packages(base_python_container, ["pipx"]).with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")

    return python_with_pipx


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
