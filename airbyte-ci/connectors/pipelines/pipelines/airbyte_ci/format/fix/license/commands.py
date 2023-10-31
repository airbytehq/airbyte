# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.cli.click_decorators import LazyPassDecorator, click_ignore_unused_kwargs
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext

pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)


@click.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def license(ctx: ClickPipelineContext, dagger_client: Optional[dagger.Client] = None):
    """Add license to python and java code via addlicense."""
    success = await format_license(ctx, dagger_client)
    if not success:
        click.Abort()


async def format_license(ctx: ClickPipelineContext, dagger_client: Optional[dagger.Client] = None) -> bool:
    license_text = "LICENSE_SHORT"
    logger = logging.getLogger(f"format")

    dagger_client = ctx.params["dagger_client"]
    try:
        license_container = await (
            dagger_client.container()
            .from_("golang:1.17")
            .with_exec(sh_dash_c(["apt-get update", "apt-get install -y bash tree", "go get -u github.com/google/addlicense"]))
            .with_mounted_directory(
                "/src",
                dagger_client.host().directory(
                    ".",
                    include=["**/*.java", "**/*.py", "LICENSE_SHORT"],
                    exclude=DEFAULT_FORMAT_IGNORE_LIST,
                ),
            )
            .with_workdir("/src")
            .with_exec(["addlicense", "-c", "Airbyte, Inc.", "-l", "apache", "-v", "-f", license_text, "."])
        )

        await license_container
        await license_container.directory("/src").export(".")
        return True

    except Exception as e:
        logger.error(f"Failed to apply license: {e}")
        return False
