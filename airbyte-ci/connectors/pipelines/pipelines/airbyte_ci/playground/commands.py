#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import click
from pipelines.cli.click_decorators import click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext
from pipelines.cli.click_decorators import LazyPassDecorator


pass_pipeline_context: LazyPassDecorator = LazyPassDecorator(ClickPipelineContext)

@click.command()
@click.argument("hold")
@click.option("--opt", default="default_value")
@pass_pipeline_context
@click_ignore_unused_kwargs
def playground(
    ctx: ClickPipelineContext,
):
    """
    TODO
    1. Make async
    1. Call a dagger pipeline

    Blockers:
    1. Need asyncio to run dagger pipeline
    """

    # dagger_client = await ctx.get_dagger_client(pipeline_name="format_ci")
    # pytest_container = await (
    #     dagger_client.container()
    #     .from_("python:3.10.12")
    #     .with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")
    #     .with_exec(
    #         sh_dash_c(
    #             [
    #                 "apt-get update",
    #                 "apt-get install -y bash git curl",
    #                 "pip install pipx",
    #                 "pipx ensurepath",
    #                 "pipx install poetry",
    #             ]
    #         )
    #     )
    #     .with_env_variable("VERSION", DOCKER_VERSION)
    #     .with_exec(sh_dash_c(["curl -fsSL https://get.docker.com | sh"]))
    #     .with_mounted_directory(
    #         "/airbyte",
    #         dagger_client.host().directory(
    #             ".",
    #             exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"],
    #             include=directories_to_mount,
    #         ),
    #     )
    #     .with_workdir(f"/airbyte/{poetry_package_path}")
    #     .with_exec(["poetry", "install"])
    #     .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
    #     .with_exec(["poetry", "run", "pytest", test_directory])
    # )

    # await pytest_container
    # return True



    print(f"params: {ctx.params}")


