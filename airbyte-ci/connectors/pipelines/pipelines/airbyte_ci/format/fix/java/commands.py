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
async def java(dagger_client: Optional[dagger.Client], ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""

    success = await format_java(dagger_client, ctx)
    if not success:
        click.Abort()


async def format_java(dagger_client: Optional[dagger.Client], ctx: ClickPipelineContext) -> bool:
    logger = logging.getLogger("format")

    fix = ctx.params["fix"]
    if fix:
        gradle_command = ["./gradlew", "spotlessApply"]
    else:
        gradle_command = ["./gradlew", "spotlessCheck", "--scan"]

    if not dagger_client:
        dagger_client = await ctx.get_dagger_client(pipeline_name="Format Java")
    try:
        format_container = await (
            dagger_client.container()
            .from_("openjdk:17.0.1-jdk-slim")
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
                    include=[
                        "**/*.java",
                        "**/*.sql",
                        "**/*.gradle",
                        "gradlew",
                        "gradlew.bat",
                        "gradle",
                        "**/deps.toml",
                        "**/gradle.properties",
                        "**/version.properties",
                        "tools/gradle/codestyle/java-google-style.xml",
                        "tools/gradle/codestyle/sql-dbeaver.properties",
                    ],
                    exclude=DEFAULT_FORMAT_IGNORE_LIST,
                ),
            )
            .with_workdir(f"/src")
            .with_exec(gradle_command)
        )

        await format_container
        if fix:
            await format_container.directory("/src").export(".")
        return True

    except dagger.ExecError as e:
        logger.error("Format failed")
        logger.error(e.stderr)
        return False
