#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List

import asyncclick as click
import dagger

from pipelines import main_logger
from pipelines.airbyte_ci.connectors.build_image.steps import run_connector_build_pipeline
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.pipeline import run_connectors_pipelines
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.consts import BUILD_PLATFORMS, LOCAL_BUILD_PLATFORM


@click.command(cls=DaggerPipelineCommand, help="Build all images for the selected connectors.")
@click.option(
    "--use-host-gradle-dist-tar",
    is_flag=True,
    help="Use gradle distTar output from host for java connectors.",
    default=False,
    type=bool,
)
@click.option(
    "-a",
    "--architecture",
    "build_architectures",
    help="Architecture for which to build the connector image. If not specified, the image will be built for the local architecture.",
    multiple=True,
    default=[LOCAL_BUILD_PLATFORM],
    type=click.Choice(BUILD_PLATFORMS, case_sensitive=True),
)
@click.option(
    "-t",
    "--tag",
    help="The tag to use for the built image.",
    default="dev",
    type=str,
)
@click.pass_context
async def build(ctx: click.Context, use_host_gradle_dist_tar: bool, build_architectures: List[str], tag: str) -> bool:
    """Runs a build pipeline for the selected connectors."""
    build_platforms = [dagger.Platform(architecture) for architecture in build_architectures]
    main_logger.info(f"Building connectors for {build_platforms}, use --architecture to change this.")
    connectors_contexts = [
        ConnectorContext(
            pipeline_name=f"Build connector {connector.technical_name}",
            connector=connector,
            is_local=ctx.obj["is_local"],
            git_branch=ctx.obj["git_branch"],
            git_revision=ctx.obj["git_revision"],
            diffed_branch=ctx.obj["diffed_branch"],
            git_repo_url=ctx.obj["git_repo_url"],
            ci_report_bucket=ctx.obj["ci_report_bucket_name"],
            report_output_prefix=ctx.obj["report_output_prefix"],
            gha_workflow_run_url=ctx.obj.get("gha_workflow_run_url"),
            dagger_logs_url=ctx.obj.get("dagger_logs_url"),
            pipeline_start_timestamp=ctx.obj.get("pipeline_start_timestamp"),
            ci_context=ctx.obj.get("ci_context"),
            ci_gcp_credentials=ctx.obj["ci_gcp_credentials"],
            use_local_cdk=ctx.obj.get("use_local_cdk"),
            use_cdk_ref=ctx.obj.get("use_cdk_ref"),
            enable_report_auto_open=ctx.obj.get("enable_report_auto_open"),
            use_host_gradle_dist_tar=use_host_gradle_dist_tar,
            s3_build_cache_access_key_id=ctx.obj.get("s3_build_cache_access_key_id"),
            s3_build_cache_secret_key=ctx.obj.get("s3_build_cache_secret_key"),
            targeted_platforms=build_platforms,
        )
        for connector in ctx.obj["selected_connectors_with_modified_files"]
    ]
    if use_host_gradle_dist_tar and not ctx.obj["is_local"]:
        raise Exception("flag --use-host-gradle-dist-tar requires --is-local")
    await run_connectors_pipelines(
        connectors_contexts,
        run_connector_build_pipeline,
        "Build Pipeline",
        ctx.obj["concurrency"],
        ctx.obj["dagger_logs_path"],
        ctx.obj["execute_timeout"],
        tag,
    )

    return True
