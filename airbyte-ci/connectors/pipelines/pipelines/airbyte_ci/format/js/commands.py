import logging
import sys
import asyncclick as click
import dagger

from pipelines.helpers.utils import sh_dash_c


@click.command()
@click.pass_context
async def js(ctx: click.Context):
    """Format yaml and json code via prettier."""
    fix = ctx.obj.get("fix_formatting")
    if fix is None:
        raise click.UsageError("You must specify either --fix or --check")

    success = await format_js(fix)
    if not success:
        click.Abort()

async def format_js(fix: bool) -> bool:
    """Checks whether the repository is formatted correctly.
    Args:
        fix (bool): Whether to automatically fix any formatting issues detected.
    Returns:
        bool: True if the check/format succeeded, false otherwise
    """
    logger = logging.getLogger(f"format")

    if fix:
        prettier_command = ["prettier", "--write", "."]
    else:
        prettier_command = ["prettier", "--check", "."]

    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as dagger_client:
        try:
            format_container = await (
                dagger_client.container()
                .from_("node:18.18.0")  # Use specified Node.js version
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
                        include=["**/*.yaml", "**/*.yml", "**.*/json", "package.json", "package-lock.json"],
                        exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**/build", ".git", "node_modules"]
                    ),
                )
                .with_workdir(f"/src")
                .with_exec(["npm", "install", "-g", "npm@10.1.0"])
                .with_exec(["npm", "install", "-g", "prettier@2.8.1"])
                .with_exec(prettier_command)
            )

            await format_container
            if fix:
                await format_container.directory("/src").export(".")
            return True
        except Exception as e:
            logger.error(f"Failed to format code: {e}")
            return False

        except dagger.ExecError as e:
            logger.error("Format failed")
            logger.error(e.stderr)
            sys.exit(1)
