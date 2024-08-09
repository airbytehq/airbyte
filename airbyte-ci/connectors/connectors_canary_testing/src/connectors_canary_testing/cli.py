# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import contextlib
import datetime
import os
import subprocess
import sys
import time
import typing
from pathlib import Path

import click
import requests
import yaml
from connectors_canary_testing import ARTIFACTS_BUCKET_NAME, collectors, errors, logger, proxy, runners
from connectors_canary_testing.utils import get_gcs_client

if typing.TYPE_CHECKING:
    from typing import Tuple

TARGET_VERSION_VENV_PATH = "/tmp/target_version"
CONTROL_VERSION_VENV_PATH = "/tmp/control_version"


def get_metadata() -> dict:
    with open(os.environ["PATH_TO_METADATA"], "r") as metadata_file:
        return yaml.safe_load(metadata_file)


def get_current_version(metadata: dict):
    return metadata["data"]["dockerImageTag"]


def get_pipy_package_name(metadata: dict):
    pypi = metadata["data"].get("remoteRegistries").get("pypi")
    if not pypi:
        return None
    if not pypi["enabled"]:
        return None
    return pypi["packageName"]


def find_latest_version(package_name: str, current_version: str) -> str:
    response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    version_release_dates = [
        (k, datetime.datetime.strptime(v[0]["upload_time"], "%Y-%m-%dT%H:%M:%S")) for k, v in response.json()["releases"].items()
    ]
    sorted_versions = sorted(version_release_dates, key=lambda x: x[1], reverse=True)
    highest_version = sorted_versions[0][0]
    if highest_version == current_version:
        raise errors.NoTargetVersionError(f"No next version found for {package_name}")
    return highest_version


@contextlib.contextmanager
def virtualenv(venv_path: str) -> None:
    """A context manager to activate and deactivate a virtual environment."""

    # Save the current environment variables to restore them later
    old_path = os.environ.get("PATH")
    old_pythonpath = os.environ.get("PYTHONPATH")
    old_virtual_env = os.environ.get("VIRTUAL_ENV")

    # Activate the virtual environment
    activate_script = os.path.join(venv_path, "bin", "activate_this.py")
    exec(open(activate_script).read(), {"__file__": activate_script})

    try:
        yield
    finally:
        # Deactivate the virtual environment
        os.environ["PATH"] = old_path if old_path else ""
        if old_pythonpath is not None:
            os.environ["PYTHONPATH"] = old_pythonpath
        if old_virtual_env is not None:
            os.environ["VIRTUAL_ENV"] = old_virtual_env


def install_package_version(package_name: str, package_version: str, venv_path: Path) -> str:
    Path(venv_path).mkdir(exist_ok=True)
    os.chdir(venv_path)
    create_venv_result = subprocess.run(["uv", "--quiet", "venv"], capture_output=True, text=True)
    venv_path = f"{venv_path}/.venv"
    with virtualenv(venv_path):
        install_result = subprocess.run(["uv", "--quiet", "pip", "install", f"{package_name}=={package_version}", "pip_system_certs"])
        if create_venv_result.returncode != 0 or install_result.returncode != 0:
            raise errors.InstallTargetVersionError(f"Could not install {package_name}=={package_version}")
    # TODO find a better way to get the path of the installed package
    return f"{venv_path}/bin/{package_name.replace('airbyte-', '')}"


def install_target_version(package_name: str, target_version: str) -> str:
    Path(TARGET_VERSION_VENV_PATH).mkdir(exist_ok=True)
    os.chdir(TARGET_VERSION_VENV_PATH)
    create_venv_result = subprocess.run(["uv", "--quiet", "venv"], capture_output=True, text=True)
    venv_path = f"{TARGET_VERSION_VENV_PATH}/.venv"
    with virtualenv(venv_path):
        install_result = subprocess.run(["uv", "--quiet", "pip", "install", f"{package_name}=={target_version}", "pip_system_certs"])
        if create_venv_result.returncode != 0 or install_result.returncode != 0:
            raise errors.InstallTargetVersionError(f"Could not install {package_name}=={target_version}")
    # TODO find a better way to get the path of the installed package
    return f"{venv_path}/bin/{package_name.replace('airbyte-', '')}"


def get_artifacts_directory_path(artifacts_root_directory: Path, package_name: str, package_version: str, entrypoint_command: str) -> Path:
    return artifacts_root_directory / package_name / package_version / entrypoint_command


def get_artifacts_blobs_prefix(package_name: str, package_version: str, entrypoint_command: str, session_id: str) -> Path:
    return f"{package_name}/{package_version}/{entrypoint_command}/{session_id}"


def get_target_and_control_artifacts_directories(
    artifacts_root_directory: Path, package_name: str, control_version: str, target_version: str, entrypoint_command: str
) -> Tuple[Path, Path]:
    return (
        get_artifacts_directory_path(artifacts_root_directory, package_name, control_version, entrypoint_command),
        get_artifacts_directory_path(artifacts_root_directory, package_name, target_version, entrypoint_command),
    )


def get_target_and_control_artifacts_blob_prefix(
    package_name: str, control_version: str, target_version: str, entrypoint_command: str
) -> Tuple[Path, Path]:
    session_id = str(int(time.time()))
    return (
        get_artifacts_blobs_prefix(package_name, control_version, entrypoint_command, session_id),
        get_artifacts_blobs_prefix(package_name, target_version, entrypoint_command, session_id),
    )


@click.group
def connectors_canary_testing() -> None:
    pass

def patch_args_to_add_absolute_paths(args):
    patched_args = [args[0]]
    for arg in args[1:]:
        if arg.startswith("--") or arg.startswith("/"):
            patched_args.append(arg)
        else:
            patched_args.append(f"/config/{arg}")
    return patched_args

@connectors_canary_testing.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.option(
    "--artifacts-root-directory",
    envvar="CANARY_DIR",
    default="/tmp",
    type=click.Path(exists=True, dir_okay=True, file_okay=False, writable=True, readable=True, path_type=Path),
)
@click.pass_context
def entrypoint(ctx: click.Context, artifacts_root_directory: Path):
    gcs_client = get_gcs_client()
    entrypoint_args = patch_args_to_add_absolute_paths(ctx.args)
    entrypoint_command = entrypoint_args[0]
    metadata = get_metadata()
    package_name = get_pipy_package_name(metadata)
    control_version = get_current_version(metadata)
    target_version = find_latest_version(package_name, control_version)
    control_version_bin_path = install_package_version(package_name, control_version, CONTROL_VERSION_VENV_PATH)
    logger.info(f"Installed control version: {control_version}")
    target_version_bin_path = install_package_version(package_name, target_version, TARGET_VERSION_VENV_PATH)
    logger.info(f"Installed target version: {target_version}")
    control_version_command = [control_version_bin_path] + entrypoint_args
    target_version_command = [target_version_bin_path] + entrypoint_args

    control_artifacts_directory, target_artifacts_directory = get_target_and_control_artifacts_directories(
        artifacts_root_directory, package_name, control_version, target_version, entrypoint_command
    )

    control_artifacts_blob_prefix, target_artifacts_blob_prefix = get_target_and_control_artifacts_blob_prefix(
        package_name, control_version, target_version, entrypoint_command
    )

    control_artifact_generator = collectors.ArtifactGenerator(control_artifacts_directory, entrypoint_args)
    target_artifact_generator = collectors.ArtifactGenerator(target_artifacts_directory, entrypoint_args)

    with proxy.MitmProxy(proxy_port=8080, har_dump_path=control_artifact_generator.har_dump_path) as control_proxy:
        logger.info("Running command on control version")
        control_exit_code = runners.run_command_and_stream_output(
            control_version_command, control_artifact_generator.process_line, tee=True
        )
    control_artifact_generator.save_artifacts(control_exit_code)
    control_artifact_generator.upload_bundled_artifacts_to_gcs(gcs_client, destination_blob_prefix=control_artifacts_blob_prefix)

    with proxy.MitmProxy(
        proxy_port=8081, har_dump_path=target_artifact_generator.har_dump_path, replay_session_path=control_proxy.session_path
    ):
        logger.info("Running command on target version")
        target_exit_code = runners.run_command_and_stream_output(target_version_command, target_artifact_generator.process_line, tee=False)
    target_artifact_generator.save_artifacts(target_exit_code)
    target_artifact_generator.upload_bundled_artifacts_to_gcs(gcs_client, destination_blob_prefix=target_artifacts_blob_prefix)

    sys.exit(control_exit_code)
