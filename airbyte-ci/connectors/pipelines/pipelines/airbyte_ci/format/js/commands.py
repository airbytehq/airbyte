import logging
import sys

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
async def js(ctx: ClickPipelineContext):
    """Format yaml and json code via prettier."""

    success = await format_js(ctx)
    if not success:
        click.Abort()


async def format_js(ctx: ClickPipelineContext) -> bool:
    """Checks whether the repository is formatted correctly.
    Args:
        fix (bool): Whether to automatically fix any formatting issues detected.
    Returns:
        bool: True if the check/format succeeded, false otherwise
    """
    logger = logging.getLogger(f"format")

    fix = ctx.params["fix"]
    if fix:
        prettier_command = ["prettier", "--write", "."]
    else:
        prettier_command = ["prettier", "--check", "."]

    dagger_client = await ctx.get_dagger_client(pipeline_name="Format Yaml and Json")

    try:
        format_container = await (
            dagger_client.container()
            .from_("node:18.18.0-slim")
            .with_exec(
                sh_dash_c(
                    [
                        "apt-get update",
                        "apt-get install -y bash",
                    ]
                )
            )
            .with_mounted_directory(
                "/src",
                dagger_client.host().directory(
                    ".",
                    include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
                    exclude=DEFAULT_FORMAT_IGNORE_LIST,
                ),
            )
            .with_workdir(f"/src")
            .with_exec(["npm", "install", "-g", "npm@10.1.0"])
            .with_exec(["npm", "install", "-g", "prettier@2.8.1"])
            .with_exec(prettier_command)
        )

        await format_container
        if fix:
            await format_container.directory("/src").export(".")
        return True
    except Exception as e:
        logger.error(f"Failed to format code: {e}")
        return False
