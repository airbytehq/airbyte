import glob
from typing import Optional

from aircmd.actions.environments import with_debian_packages, with_pip_packages
from aircmd.models.base import PipelineContext
from aircmd.models.click_commands import ClickCommandMetadata, ClickGroup
from aircmd.models.click_utils import LazyPassDecorator, map_pyd_cmd_to_click_command
from aircmd.models.github import github_integration
from aircmd.models.plugins import DeveloperPlugin
from aircmd.models.settings import GlobalSettings
from dagger import CacheSharingMode, CacheVolume, Client, Container
from prefect import flow, task

# Tasks


@task
async def format_check_task(client: Client, settings: GlobalSettings) -> Container:
    mypy_cache: CacheVolume = client.cache_volume("mypy_cache")
    result = (with_poetry(client)
              .with_directory("/src", client.host().directory(".", include=["**/*.py", "pyproject.toml", "poetry.lock"], exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**/build"]))
              .with_workdir("/src")
              .with_exec(["ls"])
              .with_exec(["poetry", "install", "--no-dev"])
              .with_exec(["poetry", "run", 'black', "--config", "pyproject.toml", '--check', "."])
    )

    await result.sync()
    return result


@task
async def test_task(client: Client, settings: GlobalSettings, build_result: Container) -> Container:
    mypy_cache: CacheVolume = client.cache_volume("mypy_cache")
    result = with_poetry(client).with_exec(["echo", "BUILD!!!"])
    await result.sync()
    return result


# Commands

settings = GlobalSettings()
pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(PipelineContext, global_settings=settings)
pass_global_settings: LazyPassDecorator = LazyPassDecorator(GlobalSettings)


core_group = ClickGroup(group_name="core", group_help="Commands for developing on aircmd")


class BuildCommand(ClickCommandMetadata):
    command_name: str = "format_check"
    command_help: str = "Builds aircmd"


class TestCommand(ClickCommandMetadata):
    command_name: str = "test"
    command_help: str = "Tests aircmd"


class CICommand(ClickCommandMetadata):
    command_name: str = "ci"
    command_help: str = "Run CI for aircmd"


@core_group.command(BuildCommand())
@pass_pipeline_context
@pass_global_settings
@flow(validate_parameters=False, name="Aircmd Core Build")
@github_integration
async def format_check(ctx: PipelineContext, settings: GlobalSettings, client: Optional[Client] = None) -> Container:
    build_client = await ctx.get_dagger_client(client, ctx.prefect_flow_run_context.flow_run.name)
    build_future = await format_check_task.submit(build_client, settings)
    result = await build_future.result()
    return result


@core_group.command(TestCommand())
@pass_pipeline_context
@pass_global_settings
@flow(validate_parameters=False, name="Aircmd Core Test")
@github_integration
async def test(ctx: PipelineContext, settings: GlobalSettings, client: Optional[Client] = None) -> Container:
    test_client = await ctx.get_dagger_client(client, ctx.prefect_flow_run_context.flow_run.name)
    build_result = await build()
    test_future = await test_task.submit(test_client, settings, build_result)
    result = await test_future.result()
    return result


@core_group.command(CICommand())
@pass_pipeline_context
@pass_global_settings
@flow(validate_parameters=False, name="Aircmd Core CI")
@github_integration
async def ci(ctx: PipelineContext, settings: GlobalSettings, client: Optional[Client] = None) -> Container:
    await ctx.get_dagger_client(client, ctx.prefect_flow_run_context.flow_run.name)
    test_result: Container = await test()
    return test_result


# Hacky wiring


# check_ci = map_pyd_cmd_to_click_command(ci)


# core_ci_plugin = DeveloperPlugin(name = "core_ci", base_dirs = ["aircmd"])
# core_ci_plugin.add_group(core_group)


# Environments

# Edited
PYTHON_IMAGE = "python:3.10-slim"

# Non-edited
def with_poetry(client: Client) -> Container:
    """Install poetry in a python environment.

    Args:
        context (Pipeline): The current test pipeline, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with poetry installed.
    """
    python_base_environment: Container = with_python_base(client, PYTHON_IMAGE)
    python_with_git = with_debian_packages(python_base_environment, ["git"])
    python_with_poetry = with_pip_packages(python_with_git, ["poetry"])

    poetry_cache: CacheVolume = client.cache_volume("poetry_cache")
    python_with_poetry_cache = python_with_poetry.with_mounted_cache("/root/.cache/pypoetry", poetry_cache, sharing=CacheSharingMode.SHARED)

    return python_with_poetry_cache

def with_python_base(client: Client, python_image_name: str = PYTHON_IMAGE) -> Container:
    """Build a Python container with a cache volume for pip cache.
    
    Args:
        context (Pipeline): The current test pipeline, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.11-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """
    
    if not python_image_name.startswith("python:3"):
        raise ValueError("You have to use a python image to build the python base environment")
    pip_cache: CacheVolume = client.cache_volume("pip_cache")

    base_container = (
        client.container()
        .from_(python_image_name)
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(["pip", "install", "--upgrade", "pip"])
    )

    return base_container