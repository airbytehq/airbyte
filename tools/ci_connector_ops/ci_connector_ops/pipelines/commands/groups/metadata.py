import sys
import click
import anyio
import dagger
import logging

from ci_connector_ops.pipelines.bases import Step, StepStatus, TestReport
from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
)
from rich.logging import RichHandler


logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger(__name__)

METADATA_LIB_MODULE_PATH = "airbyte-ci/connectors/metadata_service/lib"


class MetadataLibRunTest(Step):
    title = "Run Metadata Service Lib Unit Tests"

    async def _run(self) -> StepStatus:
        metadata_lib_module = environments.with_poetry_module(self.context, METADATA_LIB_MODULE_PATH)
        run_test = metadata_lib_module.with_exec(["poetry", "run", "pytest"])
        return await self.get_step_result(run_test)

async def run_metadata_lib_test_pipeline(metadata_pipeline_context: PipelineContext) -> bool:
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            result = await MetadataLibRunTest(metadata_pipeline_context).run()
            metadata_pipeline_context.test_report = TestReport(pipeline_context=metadata_pipeline_context, steps_results=[result])

    return metadata_pipeline_context.test_report.success


@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata(ctx: click.Context):
    pass

@metadata.group(help="Commands related to the metadata service.")
@click.pass_context
def test(ctx: click.Context):
    pass


@test.command(help="Run unit tests for the metadata service library.")
@click.pass_context
def lib(ctx: click.Context):
    logger.info("Running metadata service lib unit tests...")
    metadata_pipeline_context = PipelineContext(
        pipeline_name="Metadata Service Lib Unit Test Pipeline",
        is_local=ctx.obj["is_local"],
        git_branch=ctx.obj["git_branch"],
        git_revision=ctx.obj["git_revision"],
        gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
        pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
        ci_context=ctx.obj.get("ci_context"),
    )
    try:
        pipeline_success = anyio.run(run_metadata_lib_test_pipeline, metadata_pipeline_context)
        if not pipeline_success:
            raise dagger.DaggerError("Metadata Service Lib Unit Test Pipeline failed.")

    except dagger.DaggerError as e:
        click.secho(str(e), err=True, fg="red")
        return sys.exit(1)


if __name__ == "__main__":
    lib()
