#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import asyncclick as click
import pytest
from asyncclick.testing import CliRunner

from pipelines.cli.click_decorators import click_append_to_context_object, click_ignore_unused_kwargs, click_merge_args_into_context_obj


@pytest.mark.anyio
async def test_click_append_to_context_object():
    runner = CliRunner()

    def get_value(ctx):
        return "got"

    async def get_async_value(ctx):
        return "async_got"

    @click.command(name="test-command")
    @click_append_to_context_object("get", get_value)
    @click_append_to_context_object("async_get", get_async_value)
    @click_append_to_context_object("foo", "bar")
    @click_append_to_context_object("baz", lambda _ctx: "qux")
    @click_append_to_context_object("foo2", lambda ctx: ctx.obj.get("foo") + "2")
    async def test_command():
        ctx = click.get_current_context()
        assert ctx.obj["foo"] == "bar"
        assert ctx.obj["baz"] == "qux"
        assert ctx.obj["foo2"] == "bar2"
        assert ctx.obj["get"] == "got"
        assert ctx.obj["async_get"] == "async_got"

    @click.command(name="test-command")
    @click_append_to_context_object("get", get_value)
    @click_append_to_context_object("async_get", get_async_value)
    @click_append_to_context_object("foo", "bar")
    @click_append_to_context_object("baz", lambda _ctx: "qux")
    @click_append_to_context_object("foo2", lambda ctx: ctx.obj.get("foo") + "2")
    async def test_command_async():
        ctx = click.get_current_context()
        assert ctx.obj["foo"] == "bar"
        assert ctx.obj["baz"] == "qux"
        assert ctx.obj["foo2"] == "bar2"
        assert ctx.obj["get"] == "got"
        assert ctx.obj["async_get"] == "async_got"

    result = await runner.invoke(test_command)
    assert result.exit_code == 0

    result_async = await runner.invoke(test_command_async)
    assert result_async.exit_code == 0


@pytest.mark.anyio
async def test_click_ignore_unused_kwargs():
    @click_ignore_unused_kwargs
    def decorated_function(a, b):
        return a + b

    # Test that the decorated function works as expected with matching kwargs
    assert decorated_function(a=1, b=2) == 3

    # Test that the decorated function ignores unmatched kwargs
    assert decorated_function(a=1, b=2, c=3) == 3


@pytest.mark.anyio
async def test_click_merge_args_into_context_obj():
    runner = CliRunner()

    @click.command(name="test-command")
    @click.option("--foo", help="foo option")
    @click.option("--bar", help="bar option")
    @click_merge_args_into_context_obj
    @click_ignore_unused_kwargs
    async def test_command(foo, bar):
        ctx = click.get_current_context()
        assert ctx.obj["foo"] == foo
        assert ctx.obj["bar"] == bar

    result = await runner.invoke(test_command, ["--foo", "hello", "--bar", "world"])
    assert result.exit_code == 0
