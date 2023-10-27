import sys

import anyio
import dagger

async def run_release():
    config = dagger.Config(log_output=sys.stdout)
    directories_to_mount = [".git", "airbyte-ci"]

    async with dagger.Connection(config) as dagger_client:
        await (
                dagger_client
                .container()
                .from_("amd64/python:3.10-slim")
                .with_exec(["apt-get", "update"])
                .with_exec(["apt-get", "install", "-y", "git", "binutils"])
                .with_exec(["pip", "install", "poetry"])
                .with_mounted_directory(
                    "/airbyte",
                    dagger_client.host().directory(
                        ".",
                        exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"],
                        include=directories_to_mount,
                    ),
                )
                .with_workdir(f"/airbyte/airbyte-ci/connectors/pipelines")
                .with_exec(["poetry", "install", "--with", "dev"])
                # poetry run pyinstaller --collect-all pipelines --collect-all beartype --collect-all dagger --hidden-import strawberry --name airbyte_ci_macos --onefile pipelines/cli/airbyte_ci.py
                .with_exec(["poetry", "run", "pyinstaller", "--target-architecture", "universal2", "--collect-all", "pipelines", "--collect-all", "beartype", "--collect-all", "dagger", "--hidden-import", "strawberry", "--name", "airbyte_ci_macos", "--onefile", "pipelines/cli/airbyte_ci.py"])
                .with_exec(["./dist/airbyte_ci_macos", "--version"])
                .with_exec(["ls", "-la", "dist"])
                .directory("/airbyte/airbyte-ci/connectors/pipelines/dist")
                .export(".")
        )
