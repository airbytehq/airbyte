import click
import anyio
import logging

from rich.logging import RichHandler

from ci_connector_ops.pipelines.pipelines.metadata import run_metadata_lib_test_pipeline, run_metadata_orchestrator_test_pipeline
from ci_connector_ops.pipelines.utils import DaggerPipelineCommand


logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger(__name__)


@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata(ctx: click.Context):
    pass


@metadata.group(help="Commands related to the metadata service.")
@click.pass_context
def test(ctx: click.Context):
    pass


@test.command(cls=DaggerPipelineCommand, help="Run tests for the metadata service library.")
@click.pass_context
def lib(ctx: click.Context):
    return anyio.run(
        run_metadata_lib_test_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )


@test.command(cls=DaggerPipelineCommand, help="Run tests for the metadata service orchestrator.")
@click.pass_context
def orchestrator(ctx: click.Context):
    return anyio.run(
        run_metadata_orchestrator_test_pipeline,
        ctx.obj["is_local"],
        ctx.obj["git_branch"],
        ctx.obj["git_revision"],
        ctx.obj.get("gha_workflow_run_url"),
        ctx.obj.get("pipeline_start_timestamp"),
        ctx.obj.get("ci_context"),
    )


if __name__ == "__main__":
    lib()
