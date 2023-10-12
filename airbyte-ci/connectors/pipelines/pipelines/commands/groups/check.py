from typing import Optional

from aircmd.actions.environments import with_poetry
from aircmd.models.base import PipelineContext
from aircmd.models.click_commands import ClickCommandMetadata, ClickGroup
from aircmd.models.click_utils import LazyPassDecorator, map_pyd_cmd_to_click_command
from aircmd.models.github import github_integration
from aircmd.models.plugins import DeveloperPlugin
from aircmd.models.settings import GlobalSettings
from dagger import CacheVolume, Client, Container
from prefect import flow, task

# Tasks


@task
async def build_task(client: Client, settings: GlobalSettings) -> Container:
    mypy_cache: CacheVolume = client.cache_volume("mypy_cache")
    result = with_poetry(client).with_exec(["echo", "BUILD!!!"])
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
    command_name: str = "build"
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
async def build(ctx: PipelineContext, settings: GlobalSettings, client: Optional[Client] = None) -> Container:
    build_client = await ctx.get_dagger_client(client, ctx.prefect_flow_run_context.flow_run.name)
    build_future = await build_task.submit(build_client, settings)
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
