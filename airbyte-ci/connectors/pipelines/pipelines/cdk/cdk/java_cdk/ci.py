"""CI Workflow commands for Airbyte Java CDK"""

from typing import List, Optional

from aircmd.models.base import PipelineContext
from aircmd.models.click_commands import ClickCommandMetadata, ClickFlag, ClickGroup
from aircmd.models.click_params import ParameterType
from aircmd.models.click_utils import LazyPassDecorator
from dagger import Client, Container
from prefect import flow
from prefect.utilities.annotations import quote

from .settings import JavaCDKSettings
from .tasks import build_java_cdk_task, test_java_cdk_task

settings = JavaCDKSettings()
pass_pipeline_context = LazyPassDecorator(PipelineContext, global_settings=settings)
pass_global_settings = LazyPassDecorator(JavaCDKSettings)


java_group = ClickGroup(group_name="java", group_help="Commands for developing Airbyte Java CDK")


class CICommandMetadata(ClickCommandMetadata):
    command_name: str = "ci"
    command_help: str = "Runs CI for Airbyte Java CDK"
    flags: List[ClickFlag] = [ClickFlag(name="--scan", type=ParameterType.BOOL, help="Enables gradle scanning", default=False)]


class BuildCommand(ClickCommandMetadata):
    command_name: str = "build"
    command_help: str = "Builds Airbyte Java CDK"
    flags: List[ClickFlag] = [ClickFlag(name="--scan", type=ParameterType.BOOL, help="Enables gradle scanning", default=False)]


class TestCommand(ClickCommandMetadata):
    command_name: str = "test"
    command_help: str = "Tests Airbyte Java CDK"
    flags: List[ClickFlag] = [ClickFlag(name="--scan", type=ParameterType.BOOL, help="Enables gradle scanning", default=False)]


@java_group.command(BuildCommand())
@pass_pipeline_context
@pass_global_settings
@flow(validate_parameters=False, name="Java CDK Build")
async def build(
    settings: JavaCDKSettings, ctx: PipelineContext, client: Optional[Client] = None, scan: bool = False
) -> Container:
    build_client = await ctx.get_dagger_client(client, ctx.prefect_flow_run_context.flow_run.name)
    build_future = await build_java_cdk_task.submit(client=build_client, settings=settings, ctx=quote(ctx), scan=scan)
    result = await build_future.result()
    await result
    return result


@java_group.command(TestCommand())
@pass_global_settings
@pass_pipeline_context
@flow(validate_parameters=False, name="Java CDK Test")
async def test(
    settings: JavaCDKSettings, ctx: PipelineContext, client: Optional[Client] = None, scan: bool = False
) -> Container:
    test_client = client.pipeline(BuildCommand().command_name) if client else ctx.get_dagger_client().pipeline(BuildCommand().command_name)
    build_result = await build(scan=scan)
    results = await test_java_cdk_task.submit(
        build_result=build_result[0], client=test_client, settings=settings, ctx=quote(ctx), scan=scan
    )
    return [results]


@java_group.command(CICommand())
@pass_global_settings
@pass_pipeline_context
@flow(validate_parameters=False, name="Java CDK CI")
async def ci(settings: JavaCDKSettings, ctx: PipelineContext, client: Optional[Client] = None, scan: bool = False) -> None:
    ci_client = client.pipeline(BuildCommand().command_name) if client else ctx.get_dagger_client().pipeline(BuildCommand().command_name)
    test_result = await test(client=ci_client, scan=scan)
    # Something like this:
    # if settings.CI and settings.PUBLISH:
    #      await publish_java.submit(build_result=build_result[0], client=test_client, settings=settings, ctx=quote(ctx), scan=scan)

    return test_result

