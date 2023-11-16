#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import asyncclick as click
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.consts import DOCKER_VERSION
from pipelines.helpers.utils import sh_dash_c
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context


@click.command()
@pass_pipeline_context
@click_ignore_unused_kwargs
async def cdk_publish(pipeline_context: ClickPipelineContext):
    pipeline_name = "publish cdk"
    dagger_client = await pipeline_context.get_dagger_client(pipeline_name=pipeline_name)
    cdk_container = dagger_client.host().directory("airbyte-cdk/python/").docker_build()
    await cdk_container.publish("airbyte/source-declarative-manifest:test-build")
