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
import xml.sax.saxutils
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING

import anyio
import asyncclick as click
import asyncer
from dagger import Client, Config, Container, Directory, ExecError, File, ImageLayerCompression, Platform, Secret
from more_itertools import chunked

if TYPE_CHECKING:
    from typing import Any, Callable, Generator, List, Optional, Set, Tuple

    from pipelines.airbyte_ci.connectors.context import ConnectorContext

DAGGER_CONFIG = Config(log_output=sys.stderr)
METADATA_FILE_NAME = "metadata.yaml"
MANIFEST_FILE_NAME = "manifest.yaml"
METADATA_ICON_FILE_NAME = "icon.svg"
DIFF_FILTER = "MADRT"  # Modified, Added, Deleted, Renamed, Type changed
IGNORED_FILE_EXTENSIONS: List[str] = []


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


def secret_host_variable(client: Client, name: str, default: str = "") -> Callable[[Container], Container]:
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

    def _secret_host_variable(container: Container) -> Container:
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
    dir_name, file_name = os.path.split(path)
    if file_name not in set(await container.directory(dir_name).entries()):
        return None
    return await container.file(path).contents()


@contextlib.contextmanager
def catch_exec_error_group() -> Generator:
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


def slugify(value: object, allow_unicode: bool = False) -> str:
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


async def execute_concurrently(steps: List[Callable], concurrency: int = 5) -> List[Any]:
    tasks = []
    # Asyncer does not have builtin semaphore, so control concurrency via chunks of steps
    # Anyio has semaphores but does not have the soonify method which allow access to results via the value task attribute.
    for chunk in chunked(steps, concurrency):
        async with asyncer.create_task_group() as task_group:
            tasks += [task_group.soonify(step)() for step in chunk]
    return [task.value for task in tasks]


async def export_container_to_tarball(
    context: ConnectorContext, container: Container, platform: Platform, tar_file_name: Optional[str] = None
) -> Tuple[Optional[File], Optional[Path]]:
    """Save the container image to the host filesystem as a tar archive.

    Exports a container to a tarball file.
    The tarball file is saved to the host filesystem in the directory specified by the host_image_export_dir_path attribute of the context.

    Args:
        context (ConnectorContext): The current connector context.
        container (Container) : The list of container variants to export.
        platform (Platform): The platform of the container to export.
        tar_file_name (Optional[str], optional): The name of the tar archive file. Defaults to None.

    Returns:
        Tuple[Optional[File], Optional[Path]]: A tuple with the file object holding the tar archive on the host and its path.
    """
    tar_file_name = (
        f"{slugify(context.connector.technical_name)}_{context.git_revision}_{platform.replace('/', '_')}.tar"
        if tar_file_name is None
        else tar_file_name
    )
    local_path = Path(f"{context.host_image_export_dir_path}/{tar_file_name}")
    export_success = await container.export(str(local_path), forced_compression=ImageLayerCompression.Gzip)
    if export_success:
        return context.dagger_client.host().file(str(local_path)), local_path
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


def transform_strs_to_paths(str_paths: Set[str]) -> List[Path]:
    """Transform a list of string paths to an ordered list of Path objects.

    Args:
        str_paths (Set[str]): A set of string paths.

    Returns:
        List[Path]: A list of Path objects.
    """
    return sorted([Path(str_path) for str_path in str_paths])


def fail_if_missing_docker_hub_creds(ctx: click.Context) -> None:
    if ctx.obj["docker_hub_username"] is None or ctx.obj["docker_hub_password"] is None:
        raise click.UsageError(
            "You need to be logged to DockerHub registry to run this command. Please set DOCKER_HUB_USERNAME and DOCKER_HUB_PASSWORD environment variables."
        )


def java_log_scrub_pattern(secrets_to_mask: List[str]) -> str:
    """Transforms a list of secrets into a LOG_SCRUB_PATTERN env var value for our log4j test configuration."""
    # Build a regex pattern that matches any of the secrets to mask.
    regex_pattern = "|".join(map(re.escape, secrets_to_mask))
    # Now, make this string safe to consume by the log4j configuration.
    # Its parser is XML-based so the pattern needs to be escaped again, and carefully.
    return xml.sax.saxutils.escape(
        regex_pattern,
        # Annoyingly, the log4j properties file parser is quite brittle when it comes to
        # handling log message patterns. In our case the env var is injected like this:
        #
        #     ${env:LOG_SCRUB_PATTERN:-defaultvalue}
        #
        # We must avoid confusing the parser with curly braces or colons otherwise the
        # printed log messages will just consist of `%replace`.
        {
            "\t": "&#9;",
            "'": "&apos;",
            '"': "&quot;",
            "{": "&#123;",
            "}": "&#125;",
            ":": "&#58;",
        },
    )


def dagger_directory_as_zip_file(dagger_client: Client, directory: Directory, directory_name: str) -> File:
    """Compress a directory and return a File object representing the zip file.

    Args:
        dagger_client (Client): The dagger client.
        directory (Path): The directory to compress.
        directory_name (str): The name of the directory.

    Returns:
        File: The File object representing the zip file.
    """
    return (
        dagger_client.container()
        .from_("alpine:3.19.1")
        .with_exec(sh_dash_c(["apk update", "apk add zip"]))
        .with_mounted_directory(f"/{directory_name}", directory)
        .with_exec(["zip", "-r", "/zipped.zip", f"/{directory_name}"])
        .file("/zipped.zip")
    )
