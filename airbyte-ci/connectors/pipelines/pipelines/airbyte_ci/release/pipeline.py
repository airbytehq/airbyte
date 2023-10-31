import sys
import dagger
from pipelines.helpers.utils import sh_dash_c

async def run_release():
    config = dagger.Config(log_output=sys.stdout)
    directories_to_mount = [".git", "airbyte-ci"]

    async with dagger.Connection(config) as dagger_client:
        await (
                dagger_client
                .container()
                .from_("python:3.10-slim")
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
                .with_exec(["poetry",
                    "run",
                    "pyinstaller",
                    "--collect-all",
                    "pipelines",
                    "--collect-all",
                    "beartype",
                    "--collect-all",
                    "dagger",
                    "--hidden-import",
                    "strawberry",
                    "--name",
                    "airbyte_ci_debian",
                    "--onefile",
                    "pipelines/cli/airbyte_ci.py",
                ])
                .with_exec(["./dist/airbyte_ci_debian", "--version"])
                .with_exec(["ls", "-la", "dist"])
                .directory("/airbyte/airbyte-ci/connectors/pipelines/dist")
                .export(".")
        )

        await (
                dagger_client
                .container()
                .from_("python:3.10-slim")
                .with_exec(["apt-get", "update"])
                .with_exec(["apt-get", "install", "-y", "git", "binutils"])
                .with_env_variable("VERSION", "24.0.2")
                .with_exec(sh_dash_c(["curl -fsSL https://get.docker.com | sh"]))
                .with_unix_socket("/var/run/docker.sock", dagger_client.host().unix_socket("/var/run/docker.sock"))
                .with_mounted_directory(
                    "/airbyte",
                    dagger_client.host().directory(
                        ".",
                        exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"],
                        include=[".git", "airbyte-ci", "airbyte_ci_debian", "airbyte-integrations"],
                    ),
                )
                .with_workdir(f"/airbyte")
                .with_exec(["./airbyte_ci_debian", "--version"])
                .with_exec(["./airbyte_ci_debian", "connectors", "--support-level=certified", "list"])
        )

