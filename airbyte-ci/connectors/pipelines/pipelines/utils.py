#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module groups util function used in pipelines."""
from __future__ import annotations

import contextlib
import datetime
import json
import os
import re
import sys
import unicodedata
from glob import glob
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, FrozenSet, List, Optional, Set, Tuple, Union

import anyio
import asyncer
import click
import git
from connector_ops.utils import get_changed_connectors
from dagger import Client, Config, Connection, Container, DaggerError, ExecError, File, ImageLayerCompression, QueryError, Secret
from google.cloud import storage
from google.oauth2 import service_account
from more_itertools import chunked
from pipelines import consts, main_logger, sentry_utils
from pipelines.consts import GCS_PUBLIC_DOMAIN

if TYPE_CHECKING:
    from connector_ops.utils import Connector
    from github import PullRequest
    from pipelines.contexts import ConnectorContext

DAGGER_CONFIG = Config(log_output=sys.stderr)
AIRBYTE_REPO_URL = "https://github.com/airbytehq/airbyte.git"
METADATA_FILE_NAME = "metadata.yaml"
METADATA_ICON_FILE_NAME = "icon.svg"
DIFF_FILTER = "MADRT"  # Modified, Added, Deleted, Renamed, Type changed
IGNORED_FILE_EXTENSIONS = [".md"]
STATIC_REPORT_PREFIX = "airbyte-ci"


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


def get_last_commit_message() -> str:
    """Retrieve the last commit message."""
    return git.Repo().head.commit.message


def _is_ignored_file(file_path: Union[str, Path]) -> bool:
    """Check if the provided file has an ignored extension."""
    return Path(file_path).suffix in IGNORED_FILE_EXTENSIONS


def _find_modified_connectors(
    file_path: Union[str, Path], all_connectors: Set[Connector], dependency_scanning: bool = True
) -> Set[Connector]:
    """Find all connectors impacted by the file change."""
    modified_connectors = set()

    for connector in all_connectors:
        if Path(file_path).is_relative_to(Path(connector.code_directory)):
            main_logger.info(f"Adding connector '{connector}' due to connector file modification: {file_path}.")
            modified_connectors.add(connector)

        if dependency_scanning:
            for connector_dependency in connector.get_local_dependency_paths():
                if Path(file_path).is_relative_to(Path(connector_dependency)):
                    # Add the connector to the modified connectors
                    modified_connectors.add(connector)
                    main_logger.info(f"Adding connector '{connector}' due to dependency modification: '{file_path}'.")
    return modified_connectors


def get_modified_connectors(modified_files: Set[Path], all_connectors: Set[Connector], dependency_scanning: bool) -> Set[Connector]:
    """Create a mapping of modified connectors (key) and modified files (value).
    If dependency scanning is enabled any modification to a dependency will trigger connector pipeline for all connectors that depend on it.
    It currently works only for Java connectors .
    It's especially useful to trigger tests of strict-encrypt variant when a change is made to the base connector.
    Or to tests all jdbc connectors when a change is made to source-jdbc or base-java.
    We'll consider extending the dependency resolution to Python connectors once we confirm that it's needed and feasible in term of scale.
    """
    # Ignore files with certain extensions
    modified_connectors = set()
    for modified_file in modified_files:
        if not _is_ignored_file(modified_file):
            modified_connectors.update(_find_modified_connectors(modified_file, all_connectors, dependency_scanning))
    return modified_connectors


def get_connector_modified_files(connector: Connector, all_modified_files: Set[Path]) -> FrozenSet[Path]:
    connector_modified_files = set()
    for modified_file in all_modified_files:
        modified_file_path = Path(modified_file)
        if modified_file_path.is_relative_to(connector.code_directory):
            connector_modified_files.add(modified_file)
    return frozenset(connector_modified_files)


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


class DaggerPipelineCommand(click.Command):
    @sentry_utils.with_command_context
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
        main_logger.info(f"Running Dagger Command {command_name}...")
        main_logger.info(
            "If you're running this command for the first time the Dagger engine image will be pulled, it can take a short minute..."
        )
        ctx.obj["report_output_prefix"] = self.render_report_output_prefix(ctx)
        dagger_logs_gcs_key = f"{ctx.obj['report_output_prefix']}/dagger-logs.txt"
        try:
            if not ctx.obj["show_dagger_logs"]:
                dagger_log_dir = Path(f"{consts.LOCAL_REPORTS_PATH_ROOT}/{ctx.obj['report_output_prefix']}")
                dagger_log_path = Path(f"{dagger_log_dir}/dagger.log").resolve()
                ctx.obj["dagger_logs_path"] = dagger_log_path
                main_logger.info(f"Saving dagger logs to: {dagger_log_path}")
                if ctx.obj["is_ci"]:
                    ctx.obj["dagger_logs_url"] = f"{GCS_PUBLIC_DOMAIN}/{ctx.obj['ci_report_bucket_name']}/{dagger_logs_gcs_key}"
                else:
                    ctx.obj["dagger_logs_url"] = None
            else:
                ctx.obj["dagger_logs_path"] = None
            pipeline_success = super().invoke(ctx)
            if not pipeline_success:
                raise DaggerError(f"Dagger Command {command_name} failed.")
        except DaggerError as e:
            main_logger.error(f"Dagger Command {command_name} failed", exc_info=e)
            sys.exit(1)
        finally:
            if ctx.obj.get("dagger_logs_path"):
                if ctx.obj["is_local"]:
                    main_logger.info(f"Dagger logs saved to {ctx.obj['dagger_logs_path']}")
                if ctx.obj["is_ci"]:
                    gcs_uri, public_url = upload_to_gcs(
                        ctx.obj["dagger_logs_path"], ctx.obj["ci_report_bucket_name"], dagger_logs_gcs_key, ctx.obj["ci_gcs_credentials"]
                    )
                    main_logger.info(f"Dagger logs saved to {gcs_uri}. Public URL: {public_url}")

    @staticmethod
    def render_report_output_prefix(ctx: click.Context) -> str:
        """Render the report output prefix for any command in the Connector CLI.

        The goal is to standardize the output of all logs and reports generated by the CLI
        related to a specific command, and to a specific CI context.

        Note: We cannot hoist this higher in the command hierarchy because only one level of
        subcommands are available at the time the context is created.
        """

        git_branch = ctx.obj["git_branch"]
        git_revision = ctx.obj["git_revision"]
        pipeline_start_timestamp = ctx.obj["pipeline_start_timestamp"]
        ci_context = ctx.obj["ci_context"]
        ci_job_key = ctx.obj["ci_job_key"] if ctx.obj.get("ci_job_key") else ci_context

        sanitized_branch = slugify(git_branch.replace("/", "_"))

        # get the command name for the current context, if a group then prepend the parent command name
        if ctx.command_path:
            cmd_components = ctx.command_path.split(" ")
            cmd_components[0] = STATIC_REPORT_PREFIX
            cmd = "/".join(cmd_components)
        else:
            cmd = None

        path_values = [
            cmd,
            ci_job_key,
            sanitized_branch,
            pipeline_start_timestamp,
            git_revision,
        ]

        # check all values are defined
        if None in path_values:
            raise ValueError(f"Missing value required to render the report output prefix: {path_values}")

        # join all values with a slash, and convert all values to string
        return "/".join(map(str, path_values))


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


def format_duration(time_delta: datetime.timedelta) -> str:
    total_seconds = time_delta.total_seconds()
    if total_seconds < 60:
        return "{:.2f}s".format(total_seconds)
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    return "{:02d}mn{:02d}s".format(minutes, seconds)


def upload_to_gcs(file_path: Path, bucket_name: str, object_name: str, credentials: str) -> Tuple[str, str]:
    """Upload a file to a GCS bucket.

    Args:
        file_path (Path): The path to the file to upload.
        bucket_name (str): The name of the GCS bucket.
        object_name (str): The name of the object in the GCS bucket.
        credentials (str): The GCS credentials as a JSON string.
    """
    # Exit early if file does not exist
    if not file_path.exists():
        main_logger.warning(f"File {file_path} does not exist. Skipping upload to GCS.")
        return "", ""

    credentials = service_account.Credentials.from_service_account_info(json.loads(credentials))
    client = storage.Client(credentials=credentials)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(str(file_path))
    gcs_uri = f"gs://{bucket_name}/{object_name}"
    public_url = f"{GCS_PUBLIC_DOMAIN}/{bucket_name}/{object_name}"
    return gcs_uri, public_url


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
