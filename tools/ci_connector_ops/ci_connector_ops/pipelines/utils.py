#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups util function used in pipelines."""
from __future__ import annotations

import datetime
import json
import re
import sys
import unicodedata
from glob import glob
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Set, Tuple, Union

import anyio
import asyncer
import click
import git
from ci_connector_ops.utils import get_all_released_connectors, get_changed_connectors
from dagger import Config, Connection, Container, DaggerError, File, ImageLayerCompression, QueryError
from more_itertools import chunked

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorContext
    from github import PullRequest

DAGGER_CONFIG = Config(log_output=sys.stderr)
AIRBYTE_REPO_URL = "https://github.com/airbytehq/airbyte.git"
METADATA_FILE_NAME = "metadata.yaml"
METADATA_ICON_FILE_NAME = "icon.svg"
DIFF_FILTER = "MADRT"  # Modified, Added, Deleted, Renamed, Type changed


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


async def get_modified_files_in_branch_remote(
    current_git_branch: str, current_git_revision: str, diffed_branch: str = "origin/master"
) -> Set[str]:
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
            .with_exec(["diff", f"--diff-filter={DIFF_FILTER}", "--name-only", f"{diffed_branch}...{current_git_revision}"])
            .stdout()
        )
    return set(modified_files.split("\n"))


def get_modified_files_in_branch_local(current_git_revision: str, diffed_branch: str = "master") -> Set[str]:
    """Use git diff and git status to spot the modified files on the local branch."""
    airbyte_repo = git.Repo()
    modified_files = airbyte_repo.git.diff(
        f"--diff-filter={DIFF_FILTER}", "--name-only", f"{diffed_branch}...{current_git_revision}"
    ).split("\n")
    status_output = airbyte_repo.git.status("--porcelain")
    for not_committed_change in status_output.split("\n"):
        file_path = not_committed_change.strip().split(" ")[-1]
        if file_path:
            modified_files.append(file_path)
    return set(modified_files)


def get_modified_files_in_branch(current_git_branch: str, current_git_revision: str, diffed_branch: str, is_local: bool = True) -> Set[str]:
    """Retrieve the list of modified files on the branch."""
    if is_local:
        return get_modified_files_in_branch_local(current_git_revision, diffed_branch)
    else:
        return anyio.run(get_modified_files_in_branch_remote, current_git_branch, current_git_revision, diffed_branch)


async def get_modified_files_in_commit_remote(current_git_branch: str, current_git_revision: str) -> Set[str]:
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
                    current_git_branch,
                    "origin",
                    AIRBYTE_REPO_URL,
                ]
            )
            .with_exec(["checkout", "-t", f"origin/{current_git_branch}"])
            .with_exec(["diff-tree", "--no-commit-id", "--name-only", current_git_revision, "-r"])
            .stdout()
        )
    return set(modified_files.split("\n"))


def get_modified_files_in_commit_local(current_git_revision: str) -> Set[str]:
    airbyte_repo = git.Repo()
    modified_files = airbyte_repo.git.diff_tree("--no-commit-id", "--name-only", current_git_revision, "-r").split("\n")
    return set(modified_files)


def get_modified_files_in_commit(current_git_branch: str, current_git_revision: str, is_local: bool = True) -> Set[str]:
    if is_local:
        return get_modified_files_in_commit_local(current_git_revision)
    else:
        return anyio.run(get_modified_files_in_commit_remote, current_git_branch, current_git_revision)


def get_modified_files_in_pull_request(pull_request: PullRequest) -> List[str]:
    """Retrieve the list of modified files in a pull request."""
    return [f.filename for f in pull_request.get_files()]


def get_modified_connectors(modified_files: Set[Union[str, Path]]) -> dict:
    """Create a mapping of modified connectors (key) and modified files (value).
    As we call connector.get_local_dependencies_paths() any modification to a dependency will trigger connector pipeline for all connectors that depend on it.
    The get_local_dependencies_paths function currently computes dependencies for Java connectors only.
    It's especially useful to trigger tests of strict-encrypt variant when a change is made to the base connector.
    Or to tests all jdbc connectors when a change is made to source-jdbc or base-java.
    We'll consider extending the dependency resolution to Python connectors once we confirm that it's needed and feasible in term of scale.
    """
    modified_connectors = {}
    all_connector_dependencies = [(connector, connector.get_local_dependencies_paths()) for connector in get_all_released_connectors()]
    for modified_file in modified_files:
        for connector, connector_dependencies in all_connector_dependencies:
            for connector_dependency in connector_dependencies:
                connector_dependency_parts = connector_dependency.parts
                modified_file_parts = Path(modified_file).parts
                # The modified file is a dependency of the connector if the modified file path starts with the connector dependency path.
                if modified_file_parts[: len(connector_dependency_parts)] == connector_dependency_parts:
                    modified_connectors.setdefault(connector, []).append(modified_file)
    return modified_connectors


def get_modified_metadata_files(modified_files: Set[Union[str, Path]]) -> Set[Path]:
    return {
        Path(str(f))
        for f in modified_files
        if str(f).endswith(METADATA_FILE_NAME) and str(f).startswith("airbyte-integrations/connectors") and "-scaffold-" not in str(f)
    }


def get_expected_metadata_files(modified_files: Set[Union[str, Path]]) -> Set[Path]:
    changed_connectors = get_changed_connectors(modified_files=modified_files)
    return {changed_connector.metadata_file_path for changed_connector in changed_connectors}


def get_all_metadata_files() -> Set[Path]:
    return {
        Path(metadata_file)
        for metadata_file in glob("airbyte-integrations/connectors/**/metadata.yaml", recursive=True)
        if "-scaffold-" not in metadata_file
    }


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
        click.secho(f"Running Dagger Command {command_name}...")
        click.secho(
            "If you're running this command for the first time the Dagger engine image will be pulled, it can take a short minute..."
        )
        try:
            pipeline_success = super().invoke(ctx)
            if not pipeline_success:
                raise DaggerError(f"Dagger Command {command_name} failed.")
        except DaggerError as e:
            click.secho(str(e), err=True, fg="red")
            sys.exit(1)


async def execute_concurrently(steps: List[Callable], concurrency=5):
    tasks = []
    # Asyncer does not have builtin semaphore, so control concurrency via chunks of steps
    # Anyio has semaphores but does not have the soonify method which allow access to results via the value task attribute.
    for chunk in chunked(steps, concurrency):
        async with asyncer.create_task_group() as task_group:
            tasks += [task_group.soonify(step)() for step in chunk]
    return [task.value for task in tasks]


async def export_container_to_tarball(
    context: ConnectorContext, container: Container, tar_file_name: Optional[str] = None
) -> Tuple[Optional[File], Optional[Path]]:
    """Save the container image to the host filesystem as a tar archive.

    Exporting a container image as a tar archive allows user to have a dagger built container image available on their host filesystem.
    They can load this tar file to their main docker host with 'docker load'.
    This mechanism is also used to share dagger built containers with other steps like AcceptanceTest that have their own dockerd service.
    We 'docker load' this tar file to AcceptanceTest's docker host to make sure the container under test image is available for testing.

    Returns:
        Tuple[Optional[File], Optional[Path]]: A tuple with the file object holding the tar archive on the host and its path.
    """
    if tar_file_name is None:
        tar_file_name = f"{context.connector.technical_name}_{context.git_revision}.tar"
    tar_file_name = slugify(tar_file_name)
    local_path = Path(f"{context.host_image_export_dir_path}/{tar_file_name}")
    export_success = await container.export(str(local_path), forced_compression=ImageLayerCompression.Gzip)
    if export_success:
        exported_file = (
            context.dagger_client.host().directory(context.host_image_export_dir_path, include=[tar_file_name]).file(tar_file_name)
        )
        return exported_file, local_path
    else:
        return None, None


def sanitize_gcs_credentials(raw_value: Optional[str]) -> Optional[str]:
    """Try to parse the raw string input that should contain a json object with the GCS credentials.
    It will raise an exception if the parsing fails and help us to fail fast on invalid credentials input.

    Args:
        raw_value (str): A string representing a json object with the GCS credentials.

    Returns:
        str: The raw value string if it was successfully parsed.
    """
    if raw_value is None:
        return None
    return json.dumps(json.loads(raw_value))
