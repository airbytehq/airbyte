#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
from pipelines.airbyte_ci.release.pipeline import run_release


@click.command()
@click.pass_context
async def release(ctx: click.Context):

    """Run airbyte-ci release pipeline"""
    ci_gcs_credentials = ctx.obj["ci_gcs_credentials"]
    ci_artifact_bucket_name = ctx.obj["ci_artifact_bucket_name"]

    if not ci_gcs_credentials:
        click.echo("GCS credentials are required to run the release pipeline.")
        click.Abort()

    if not ci_artifact_bucket_name:
        click.echo("GCS bucket name is required to run the release pipeline.")
        click.Abort()

    success = await run_release(ci_artifact_bucket_name, ci_gcs_credentials)
    if not success:
        click.Abort()
