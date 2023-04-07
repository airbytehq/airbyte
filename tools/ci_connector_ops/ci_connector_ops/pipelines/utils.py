#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups util function used in pipelines."""

import datetime
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Callable, List, Optional, Set

import anyio
import asyncer
import click
import git
from ci_connector_ops.utils import DESTINATION_CONNECTOR_PATH_PREFIX, SOURCE_CONNECTOR_PATH_PREFIX, Connector, get_connector_name_from_path
from dagger import Config, Connection, Container, DaggerError, File, QueryError

DAGGER_CONFIG = Config(log_output=sys.stderr)
AIRBYTE_REPO_URL = "https://github.com/airbytehq/airbyte.git"


# This utils will probably be redundant once https://github.com/dagger/dagger/issues/3764 is implemented
async def check_path_in_workdir(container: Container, path: str) -> bool:
    """Check if a local path is mounted to the working directory of a container.

    Args:
        container (Container): The container on which we want the check the path existence.
        path (str): Directory or file path we want to check the existence in the container working directory.

    Returns:
        bool: Whether the path exists in the container working directory.
    """
    workdir = (await container.with_exec(["pwd"]).stdout()).strip()
    mounts = await container.mounts()
    if workdir in mounts:
        expected_file_path = Path(workdir[1:]) / path
        return expected_file_path.is_file() or expected_file_path.is_dir()
    else:
        return False


# This utils will probably be redundant once https://github.com/dagger/dagger/issues/3764 is implemented
async def get_file_contents(container: Container, path: str) -> Optional[str]:
    """Retrieve a container file contents.

    Args:
        container (Container): The container hosting the file you want to read.
        path (str): Path, in the container, to the file you want to read.

    Returns:
        Optional[str]: The file content if the file exists in the container, None otherwise.
    """
    try:
        return await container.file(path).contents()
    except QueryError as e:
        if "no such file or directory" not in str(e):
            # this is the hicky bit of the stopgap because
            # this error could come from a network issue
            raise
    return None


# This is a stop-gap solution to capture non 0 exit code on Containers
# The original issue is tracked here https://github.com/dagger/dagger/issues/3192
async def with_exit_code(container: Container) -> int:
    """Read the container exit code.

    If the exit code is not 0 a QueryError is raised. We extract the non-zero exit code from the QueryError message.

    Args:
        container (Container): The container from which you want to read the exit code.

    Returns:
        int: The exit code.
    """
    try:
        await container.exit_code()
    except QueryError as e:
        error_message = str(e)
        if "exit code: " in error_message:
            exit_code = re.search(r"exit code: (\d+)", error_message)
            if exit_code:
                return int(exit_code.group(1))
            else:
                return 1
        raise
    return 0


# This is a stop-gap solution to capture non 0 exit code on Containers
# The original issue is tracked here https://github.com/dagger/dagger/issues/3192
async def with_stderr(container: Container) -> str:
    """Retrieve the stderr of a container and handle unexpected errors."""
    try:
        return await container.stderr()
    except QueryError as e:
        return str(e)


# This is a stop-gap solution to capture non 0 exit code on Containers
# The original issue is tracked here https://github.com/dagger/dagger/issues/3192
async def with_stdout(container: Container) -> str:
    """Retrieve the stdout of a container and handle unexpected errors."""
    try:
        return await container.stdout()
    except QueryError as e:
        return str(e)


def get_current_git_branch() -> str:  # noqa D103
    return git.Repo().active_branch.name


def get_current_git_revision() -> str:  # noqa D103
    return git.Repo().head.object.hexsha


def get_current_epoch_time() -> int:  # noqa D103
    return round(datetime.datetime.utcnow().timestamp())


async def get_modified_files_remote(current_git_branch: str, current_git_revision: str, diffed_branch: str = "origin/master") -> Set[str]:
    """Use git diff to spot the modified files on the remote branch."""
    async with Connection(DAGGER_CONFIG) as dagger_client:
        modified_files = await (
            dagger_client.container()
            .from_("alpine/git:latest")
            .with_workdir("/repo")
            .with_exec(["init"])
            .with_env_variable("CACHEBUSTER", current_git_revision)
            .with_exec(
                [
                    "remote",
                    "add",
                    "--fetch",
                    "--track",
                    diffed_branch.split("/")[-1],
                    "--track",
                    current_git_branch,
                    "origin",
                    AIRBYTE_REPO_URL,
                ]
            )
            .with_exec(["checkout", "-t", f"origin/{current_git_branch}"])
            .with_exec(["diff", "--diff-filter=MA", "--name-only", f"{diffed_branch}...{current_git_revision}"])
            .stdout()
        )
    return set(modified_files.split("\n"))


def get_modified_files_local(current_git_revision: str, diffed_branch: str = "master") -> Set[str]:
    """Use git diff to spot the modified files on the local branch."""
    airbyte_repo = git.Repo()
    modified_files = airbyte_repo.git.diff("--diff-filter=MA", "--name-only", f"{diffed_branch}...{current_git_revision}").split("\n")
    return set(modified_files)


def get_modified_files(current_git_branch: str, current_git_revision: str, diffed_branch: str, is_local: bool = True) -> Set[str]:
    """Retrieve the list of modified files on the branch."""
    if is_local:
        return get_modified_files_local(current_git_revision, diffed_branch)
    else:
        return anyio.run(get_modified_files_remote, current_git_branch, current_git_revision, diffed_branch)


def get_modified_connectors(modified_files: Set[str]) -> Set[Connector]:
    """Create a set of modified connectors according to the modified files on the branch."""
    modified_connectors = []
    for file_path in modified_files:
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX) or file_path.startswith(DESTINATION_CONNECTOR_PATH_PREFIX):
            modified_connectors.append(Connector(get_connector_name_from_path(file_path)))
    return set(modified_connectors)


def slugify(value: Any, allow_unicode: bool = False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py.

    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def key_value_text_to_dict(text: str) -> dict:
    kv = {}
    for line in text.split("\n"):
        if "=" in line:
            try:
                k, v = line.split("=")
            except ValueError:
                continue
            kv[k] = v
    return kv


async def key_value_file_to_dict(file: File) -> dict:
    return key_value_text_to_dict(await file.contents())


async def get_dockerfile_labels(dockerfile: File) -> dict:
    return {k.replace("LABEL ", ""): v for k, v in (await key_value_file_to_dict(dockerfile)).items() if k.startswith("LABEL")}


async def get_version_from_dockerfile(dockerfile: File) -> str:
    dockerfile_labels = await get_dockerfile_labels(dockerfile)
    try:
        return dockerfile_labels["io.airbyte.version"]
    except KeyError:
        raise Exception("Could not get the version from the Dockerfile labels.")


async def should_enable_sentry(dockerfile: File) -> bool:
    for line in await dockerfile.contents():
        if "ENV ENABLE_SENTRY true" in line:
            return True
    return False


class DaggerPipelineCommand(click.Command):
    def invoke(self, ctx: click.Context) -> Any:
        """Wrap parent invoke in a try catch suited to handle pipeline failures.
        Args:
            ctx (click.Context): The invocation context.
        Raises:
            e: Raise whatever exception that was caught.
        Returns:
            Any: The invocation return value.
        """
        command_name = self.name
        click.secho(f"Running {command_name}...")
        try:
            pipeline_success = super().invoke(ctx)
            if not pipeline_success:
                raise DaggerError(f"{command_name} failed.")
        except DaggerError as e:
            click.secho(str(e), err=True, fg="red")
            return sys.exit(1)


async def execute_concurrently(steps: List[Callable], concurrency: int = 5):
    semaphore = anyio.Semaphore(concurrency)
    async with semaphore:
        async with asyncer.create_task_group() as task_group:
            tasks = [task_group.soonify(step)() for step in steps]

        return [task.value for task in tasks]
