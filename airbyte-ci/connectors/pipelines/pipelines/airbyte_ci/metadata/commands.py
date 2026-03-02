#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click

from pipelines.cli.click_decorators import click_ci_requirements_option

# MAIN GROUP


@click.group(help="Commands related to the metadata service.")
@click_ci_requirements_option()
@click.pass_context
def metadata(ctx: click.Context) -> None:
    pass
