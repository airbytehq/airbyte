# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
import sys
from typing import Optional

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.check.utils import check
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.cli.click_decorators import click_ignore_unused_kwargs
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def java(ctx: ClickPipelineContext):
    """Format java, groovy, and sql code via spotless."""

    success = await check(
        ctx,
        base_image="openjdk:17.0.1-jdk-slim",
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
        install_commands=[],
        check_commands=["./gradlew spotlessCheck --scan"],
    )
    if not success:
        sys.exit(1)
