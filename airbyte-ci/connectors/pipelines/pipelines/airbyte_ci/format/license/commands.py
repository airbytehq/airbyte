# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST

from pipelines.helpers.utils import sh_dash_c


@click.command()
@click.pass_context
async def license(ctx: click.Context):
    """Add license to python and java code via addlicense."""
    fix = ctx.obj.get("fix_formatting")
    if fix is None:
        raise click.UsageError("You must specify either --fix or --check")

    success = await format_license(fix)
    if not success:
        click.Abort()

async def format_license(fix: bool = False) -> bool:
    license_text = "LICENSE_SHORT"
    logger = logging.getLogger(f"format")


    if fix:
        addlicense_command = ["bash", "-c", f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_text} ."]
    else:
        addlicense_command = ["bash", "-c", f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {license_text} -check ."]

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        try:
            license_container = await (
                dagger_client.container()
                .from_("golang:1.17")
                .with_exec(
                    sh_dash_c(
                        [
                            "apt-get update",
                            "apt-get install -y bash tree",
                            "go get -u github.com/google/addlicense"
                        ]
                    )
                )
                .with_mounted_directory(
                    "/src",
                    dagger_client.host().directory(
                        ".",
                        include=["**/*.java", "**/*.py", "LICENSE_SHORT"],
                        exclude=DEFAULT_FORMAT_IGNORE_LIST,
                    ),
                )
                .with_workdir(f"/src")
                .with_exec(["ls", "-la"])
                .with_exec(["tree", "."])
                .with_exec(addlicense_command)
            )

            await license_container
            if fix:
                await license_container.directory("/src").export(".")
            return True
        except Exception as e:
            logger.error(f"Failed to apply license: {e}")
            return False