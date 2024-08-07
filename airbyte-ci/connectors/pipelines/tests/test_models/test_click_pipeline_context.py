# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unittest.mock import patch

import asyncclick as click
import dagger
import pytest
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext


@pytest.mark.anyio
async def test_get_dagger_client_singleton(dagger_connection):
    @click.command()
    def cli():
        pass

    ctx = click.Context(cli)
    ctx.obj = {"foo": "bar"}
    ctx.params = {"baz": "qux"}

    async with ctx.scope():
        click_pipeline_context = ClickPipelineContext()
        with patch("pipelines.models.contexts.click_pipeline_context.dagger.Connection", lambda _x: dagger_connection):
            client1 = await click_pipeline_context.get_dagger_client()
            client2 = await click_pipeline_context.get_dagger_client()
            client3 = await click_pipeline_context.get_dagger_client(pipeline_name="pipeline_name")
            assert isinstance(client1, dagger.Client)
            assert isinstance(client2, dagger.Client)
            assert isinstance(client3, dagger.Client)

            assert client1 == client2
            assert client1 != client3


@pytest.mark.anyio
async def test_get_dagger_client_click_params(dagger_connection):
    @click.command()
    def cli():
        pass

    given_click_obj = {"foo": "bar"}
    given_click_params = {"baz": "qux"}

    ctx = click.Context(cli, obj=given_click_obj)
    ctx.params = given_click_params

    async with ctx.scope():
        click_pipeline_context = ClickPipelineContext()
        with patch("pipelines.models.contexts.click_pipeline_context.dagger.Connection", lambda _x: dagger_connection):
            pipeline_context_params = click_pipeline_context.params
            assert pipeline_context_params == {**given_click_obj, **given_click_params}


@pytest.mark.anyio
async def test_get_dagger_client_click_params_duplicate(dagger_connection):
    @click.command()
    def cli():
        pass

    given_click_obj = {"foo": "bar"}
    given_click_params = {"foo": "qux"}

    ctx = click.Context(cli, obj=given_click_obj)
    ctx.params = given_click_params
    ctx.command.params = [click.Option(["--foo"])]

    async with ctx.scope():
        click_pipeline_context = ClickPipelineContext()
        with patch("pipelines.models.contexts.click_pipeline_context.dagger.Connection", lambda _x: dagger_connection):
            with pytest.raises(ValueError):
                click_pipeline_context.params
