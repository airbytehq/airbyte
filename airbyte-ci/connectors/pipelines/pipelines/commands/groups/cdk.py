

import anyio
import click

from pipelines.builds import run_cdk_build_pipeline
from pipelines.contexts import CDKContext, CDKWithModifiedFiles
from pipelines.utils import DaggerPipelineCommand


@click.group(help="Commands related to cdk development.")
def cdk():
    pass

@click.group(help="Commands related to java cdk development.")
@click.pass_context
def java(
    ctx: click.Context,
):

    ctx.ensure_object(dict)


@click.command(cls=DaggerPipelineCommand, help="Build the java cdk artifact")
@click.pass_context
def build(ctx: click.Context) -> bool:
    """Runs a build pipeline for the selected connectors."""

    cdk_context = CDKContext(
            pipeline_name="Build java cdk",
            cdk=CDKWithModifiedFiles(language="java"),
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            ci_gcs_credentials=ctx.obj["ci_gcs_credentials"],
        )
    
    anyio.run(
        
        run_cdk_build_pipeline,
        cdk_context
    )

    return True

@click.command(cls=DaggerPipelineCommand, help="run the cdk artifact tests")
def test():
    pass
@click.command(cls=DaggerPipelineCommand, help="publish the cdk artifact")
def publish():
    pass

cdk.add_command(java)
java.add_command(build)
java.add_command(test)
java.add_command(publish)
