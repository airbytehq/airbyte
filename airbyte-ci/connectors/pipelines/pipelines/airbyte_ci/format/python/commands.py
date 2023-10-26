import logging
import sys

import asyncclick as click
import dagger
from pipelines.airbyte_ci.format.consts import DEFAULT_FORMAT_IGNORE_LIST
from pipelines.helpers.utils import sh_dash_c


@click.command()
@click.pass_context
async def python(ctx: click.Context):
    """Format python code via black and isort."""
    fix = ctx.obj.get("fix_formatting")
    if fix is None:
        raise click.UsageError("You must specify either --fix or --check")

    success = await format_python(fix)
    if not success:
        click.Abort()


async def format_python(fix: bool) -> bool:
    """Checks whether the repository is formatted correctly.
    Args:
        fix (bool): Whether to automatically fix any formatting issues detected.
    Returns:
        bool: True if the check/format succeeded, false otherwise
    """
    logger = logging.getLogger(f"format")
    isort_command = ["poetry", "run", "isort", "--settings-file", "pyproject.toml", "--check-only", "."]
    black_command = ["poetry", "run", "black", "--config", "pyproject.toml", "--check", "."]
    if fix:
        isort_command.remove("--check-only")
        black_command.remove("--check")

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        try:
            format_container = await (
                dagger_client.container()
                .from_("python:3.10.13-slim")
                .with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")
                .with_exec(
                    sh_dash_c(
                        [
                            "apt-get update",
                            "apt-get install -y bash git curl",
                            "pip install pipx",
                            "pipx ensurepath",
                            "pipx install poetry",
                        ]
                    )
                )
                .with_mounted_directory(
                    "/src",
                    dagger_client.host().directory(
                        ".", include=["**/*.py", "pyproject.toml", "poetry.lock"], exclude=DEFAULT_FORMAT_IGNORE_LIST
                    ),
                )
                .with_workdir(f"/src")
                .with_exec(["poetry", "install"])
                .with_exec(isort_command)
                .with_exec(black_command)
            )

            await format_container
            if fix:
                await format_container.directory("/src").export(".")
            return True
        except dagger.ExecError as e:
            logger.error("Format failed")
            logger.error(e.stderr)
            sys.exit(1)
