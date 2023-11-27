#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups util function used in pipelines."""
from __future__ import annotations

import contextlib
import datetime
import os
import re
import sys
import unicodedata
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple

import anyio
import asyncer
import click
from dagger import Client, Config, Container, ExecError, File, ImageLayerCompression, QueryError, Secret
from more_itertools import chunked

if TYPE_CHECKING:
    from pipelines.airbyte_ci.connectors.context import ConnectorContext

DAGGER_CONFIG = Config(log_output=sys.stderr)
AIRBYTE_REPO_URL = "https://github.com/airbytehq/airbyte.git"
METADATA_FILE_NAME = "metadata.yaml"
METADATA_ICON_FILE_NAME = "icon.svg"
DIFF_FILTER = "MADRT"  # Modified, Added, Deleted, Renamed, Type changed
IGNORED_FILE_EXTENSIONS = [".md"]


# This utils will probably be redundant once https://github.com/dagger/dagger/issues/3764 is implemented
async def check_path_in_workdir(container: Container, path: str) -> bool:
    """Check if a local path is mounted to the working directory of a container.

    Args:
        container (Container): The container on which we want the check the path existence.
        path (str): Directory or file path we want to check the existence in the container working directory.

    Returns:
        bool: Whether the path exists in the container working directory.
    """
    workdir = (await container.with_exec(["pwd"], skip_entrypoint=True).stdout()).strip()
    mounts = await container.mounts()
    if workdir in mounts:
        expected_file_path = Path(workdir[1:]) / path
        return expected_file_path.is_file() or expected_file_path.is_dir()
    else:
        return False


def secret_host_variable(client: Client, name: str, default: str = ""):
    """Add a host environment variable as a secret in a container.

    Example:
        container.with_(secret_host_variable(client, "MY_SECRET"))

    Args:
        client (Client): The dagger client.
        name (str): The name of the environment variable. The same name will be
            used in the container, for the secret name and for the host variable.
        default (str): The default value to use if the host variable is not set. Defaults to "".

    Returns:
        Callable[[Container], Container]: A function that can be used in a `Container.with_()` method.
    """

    def _secret_host_variable(container: Container):
        return container.with_secret_variable(name, get_secret_host_variable(client, name, default))

    return _secret_host_variable


def get_secret_host_variable(client: Client, name: str, default: str = "") -> Secret:
    """Creates a dagger.Secret from a host environment variable.

    Args:
        client (Client): The dagger client.
        name (str): The name of the environment variable. The same name will be used for the secret.
        default (str): The default value to use if the host variable is not set. Defaults to "".

    Returns:
        Secret: A dagger secret.
    """
    return client.set_secret(name, os.environ.get(name, default))


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
            # this error could come from a network issue
            raise
    return None


@contextlib.contextmanager
def catch_exec_error_group():
    try:
        yield
    except anyio.ExceptionGroup as eg:
        for e in eg.exceptions:
            if isinstance(e, ExecError):
                raise e
        raise


async def get_container_output(container: Container) -> Tuple[str, str]:
    """Retrieve both stdout and stderr of a container, concurrently.

    Args:
        container (Container): The container to execute.

    Returns:
        Tuple[str, str]: The stdout and stderr of the container, respectively.
    """
    with catch_exec_error_group():
        async with asyncer.create_task_group() as task_group:
            soon_stdout = task_group.soonify(container.stdout)()
            soon_stderr = task_group.soonify(container.stderr)()
    return soon_stdout.value, soon_stderr.value


async def get_exec_result(container: Container) -> Tuple[int, str, str]:
    """Retrieve the exit_code along with stdout and stderr of a container by handling the ExecError.

    Note: It is preferrable to not worry about the exit code value and just capture
    ExecError to handle errors. This is offered as a convenience when the exit code
    value is actually needed.

    If the container has a file at /exit_code, the exit code will be read from it.
    See hacks.never_fail_exec for more details.

    Args:
        container (Container): The container to execute.

    Returns:
        Tuple[int, str, str]: The exit_code, stdout and stderr of the container, respectively.
    """
    try:
        exit_code = 0
        in_file_exit_code = await get_file_contents(container, "/exit_code")
        if in_file_exit_code:
            exit_code = int(in_file_exit_code)
        return exit_code, *(await get_container_output(container))
    except ExecError as e:
        return e.exit_code, e.stdout, e.stderr


async def with_exit_code(container: Container) -> int:
    """Read the container exit code.

    Args:
        container (Container): The container from which you want to read the exit code.

    Returns:
        int: The exit code.
    """
    try:
        await container
    except ExecError as e:
        return e.exit_code
    return 0


async def with_stderr(container: Container) -> str:
    """Retrieve the stderr of a container even on execution error."""
    try:
        return await container.stderr()
    except ExecError as e:
        return e.stderr


async def with_stdout(container: Container) -> str:
    """Retrieve the stdout of a container even on execution error."""
    try:
        return await container.stdout()
    except ExecError as e:
        return e.stdout


def get_current_epoch_time() -> int:  # noqa D103
    return round(datetime.datetime.utcnow().timestamp())


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


def create_and_open_file(file_path: Path) -> TextIOWrapper:
    """Create a file and open it for writing.

    Args:
        file_path (Path): The path to the file to create.

    Returns:
        File: The file object.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch()
    return file_path.open("w")


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


def format_duration(time_delta: datetime.timedelta) -> str:
    total_seconds = time_delta.total_seconds()
    if total_seconds < 60:
        return "{:.2f}s".format(total_seconds)
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return "{:02d}mn{:02d}s".format(minutes, seconds)


def sh_dash_c(lines: List[str]) -> List[str]:
    """Wrap sequence of commands in shell for safe usage of dagger Container's with_exec method."""
    return ["sh", "-c", " && ".join(["set -o xtrace"] + lines)]


def transform_strs_to_paths(str_paths: List[str]) -> List[Path]:
    """Transform a list of string paths to a list of Path objects.

    Args:
        str_paths (List[str]): A list of string paths.

    Returns:
        List[Path]: A list of Path objects.
    """
    return [Path(str_path) for str_path in str_paths]


def fail_if_missing_docker_hub_creds(ctx: click.Context):
    if ctx.obj["docker_hub_username"] is None or ctx.obj["docker_hub_password"] is None:
        raise click.UsageError(
            "You need to be logged to DockerHub registry to run this command. Please set DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD environment variables."
        )
