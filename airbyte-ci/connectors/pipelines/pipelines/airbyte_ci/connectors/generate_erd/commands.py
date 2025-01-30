#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List

import asyncclick as click

from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.generate_erd.pipeline import run_connector_generate_erd_pipeline
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.cli.dagger_pipeline_command import DaggerPipelineCommand
from pipelines.cli.secrets import wrap_in_secret
from pipelines.helpers.connectors.command import run_connector_pipeline


@click.command(
    cls=DaggerPipelineCommand,
    short_help="Generate ERD",
)
@click.option(
    "--dbdocs-token",
    help="The token to use with dbdocs CLI.",
    type=click.STRING,
    required=False,
    envvar="DBDOCS_TOKEN",
    callback=wrap_in_secret,
)
@click.option(
    "--genai-api-key",
    help="The API key to interact with GENAI.",
    type=click.STRING,
    required=False,
    envvar="GENAI_API_KEY",
    callback=wrap_in_secret,
)
@click.option(
    "--skip-step",
    "-x",
    "skip_steps",
    multiple=True,
    type=click.Choice([step_id.value for step_id in [CONNECTOR_TEST_STEP_ID.LLM_RELATIONSHIPS, CONNECTOR_TEST_STEP_ID.PUBLISH_ERD]]),
    help="Skip a step by name. Can be used multiple times to skip multiple steps.",
)
@click_merge_args_into_context_obj
@click.pass_context
@click_ignore_unused_kwargs
async def generate_erd(ctx: click.Context, skip_steps: List[str]) -> bool:
    """
    dbdocs_token and genai_api_key and unused because they are set as part of the context in the helpers
    """
    return await run_connector_pipeline(
        ctx,
        "Generate ERD schema",
        False,
        run_connector_generate_erd_pipeline,
        skip_steps,
    )
