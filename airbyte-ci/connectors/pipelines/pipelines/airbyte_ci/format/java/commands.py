import logging
import sys

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.helpers.utils import sh_dash_c


@click.command()
@click.pass_context
async def java(ctx: click.Context):
    """Format java, groovy, and sql code via spotless."""
    fix = ctx.obj.get("fix_formatting")
    if fix is None:
        raise click.UsageError("You must specify either --fix or --check")

    success = await format_java(fix)
    if not success:
        click.Abort()


async def format_java(fix: bool) -> bool:
    logger = logging.getLogger("format")
    if fix:
        gradle_command = ["./gradlew", "spotlessApply"]
    else:
        gradle_command = ["./gradlew", "spotlessCheck", "--scan"]

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
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
                .with_exec(["ls", "-la"])
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
