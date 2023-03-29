import click
import anyio
import dagger
import logging

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.contexts import PipelineContext
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
    with_exit_code,
)
from rich.logging import RichHandler
import sys


logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])

logger = logging.getLogger(__name__)

async def run_metadata_lib_test_pipeline(metadata_pipeline_context):
    module_path =  "airbyte-ci/connectors/metadata_service/lib"
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        metadata_pipeline_context.dagger_client = dagger_client.pipeline(metadata_pipeline_context.pipeline_name)
        async with metadata_pipeline_context:
            metadata_lib_module = environments.with_poetry_module(dagger_client, module_path)
            exit_code = await with_exit_code(metadata_lib_module.with_exec(["poetry", "run", "pytest"]))

            # Raise an exception if the exit code is not 0
            if exit_code != 0:
                raise dagger.DaggerError(f"Metadata Service Lib Unit Test Pipeline failed with exit code {exit_code}")

@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata_service(ctx):
    pass

@metadata_service.command(help="Run unit tests for the metadata service library.")
@click.pass_context
def test_metadata_service_lib(ctx):
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
        anyio.run(run_metadata_lib_test_pipeline, metadata_pipeline_context)
    except dagger.DaggerError as e:
        click.secho(str(e), err=True, fg="red")
        return sys.exit(1)


if __name__ == "__main__":
    metadata_service()
