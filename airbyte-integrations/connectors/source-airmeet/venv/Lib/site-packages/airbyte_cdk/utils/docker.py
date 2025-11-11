"""Docker build utilities for Airbyte CDK."""

from __future__ import annotations

import json
import logging
import platform
import subprocess
import sys
from contextlib import ExitStack
from dataclasses import dataclass
from enum import Enum
from io import TextIOWrapper
from pathlib import Path

import click
import requests

from airbyte_cdk.models.connector_metadata import ConnectorLanguage, MetadataFile
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.utils.connector_paths import resolve_airbyte_repo_root


@dataclass(kw_only=True)
class ConnectorImageBuildError(Exception):
    """Custom exception for Docker build errors."""

    error_text: str
    build_args: list[str]

    def __str__(self) -> str:
        return "\n".join(
            [
                f"ConnectorImageBuildError: Could not build image.",
                f"Build args: {self.build_args}",
                f"Error text: {self.error_text}",
            ]
        )


logger = logging.getLogger(__name__)


class ArchEnum(str, Enum):
    """Enum for supported architectures."""

    ARM64 = "arm64"
    AMD64 = "amd64"


def _build_image(
    context_dir: Path,
    dockerfile: Path,
    metadata: MetadataFile,
    tag: str,
    arch: ArchEnum,
    build_args: dict[str, str | None] | None = None,
) -> str:
    """Build a Docker image for the specified architecture.

    Returns the tag of the built image.
    We use buildx to ensure we can build multi-platform images.

    Raises: ConnectorImageBuildError if the build fails.
    """
    docker_args: list[str] = [
        "docker",
        "buildx",
        "build",
        "--platform",
        f"linux/{arch.value}",
        "--file",
        str(dockerfile),
        "--label",
        f"io.airbyte.version={metadata.data.dockerImageTag}",
        "--label",
        f"io.airbyte.name={metadata.data.dockerRepository}",
    ]
    if build_args:
        for key, value in build_args.items():
            if value is not None:
                docker_args.extend(["--build-arg", f"{key}={value}"])
            else:
                docker_args.extend(["--build-arg", key])

    docker_args.extend(
        [
            "-t",
            tag,
            str(context_dir),
        ]
    )

    print(f"Building image: {tag} ({arch})")
    try:
        run_docker_command(
            docker_args,
            raise_if_errors=True,
            capture_stderr=True,
        )
    except subprocess.CalledProcessError as e:
        raise ConnectorImageBuildError(
            error_text=e.stderr,
            build_args=docker_args,
        ) from e

    return tag


def _tag_image(
    tag: str,
    new_tags: list[str] | str,
) -> None:
    """Build a Docker image for the specified architecture.

    Returns the tag of the built image.

    Raises:
        ConnectorImageBuildError: If the docker tag command fails.
    """
    if not isinstance(new_tags, list):
        new_tags = [new_tags]

    for new_tag in new_tags:
        print(f"Tagging image '{tag}' as: {new_tag}")
        docker_args = [
            "docker",
            "tag",
            tag,
            new_tag,
        ]
        try:
            run_docker_command(
                docker_args,
                raise_if_errors=True,
                capture_stderr=True,
            )
        except subprocess.CalledProcessError as e:
            raise ConnectorImageBuildError(
                error_text=e.stderr,
                build_args=docker_args,
            ) from e


def build_connector_image(
    connector_name: str,
    connector_directory: Path,
    *,
    metadata: MetadataFile,
    tag: str,
    no_verify: bool = False,
    dockerfile_override: Path | None = None,
) -> str:
    """Build a connector Docker image.

    This command builds a Docker image for a connector, using either
    the connector's Dockerfile or a base image specified in the metadata.
    The image is built for both AMD64 and ARM64 architectures.

    Args:
        connector_name: The name of the connector.
        connector_directory: The directory containing the connector code.
        metadata: The metadata of the connector.
        tag: The tag to apply to the built image.
        no_verify: If True, skip verification of the built image.

    Raises:
        ValueError: If the connector build options are not defined in metadata.yaml.
        ConnectorImageBuildError: If the image build or tag operation fails.
    """
    # Detect primary architecture based on the machine type.
    primary_arch: ArchEnum = (
        ArchEnum.ARM64
        if platform.machine().lower().startswith(("arm", "aarch"))
        else ArchEnum.AMD64
    )
    if not connector_name:
        raise ValueError("Connector name must be provided.")
    if not connector_directory:
        raise ValueError("Connector directory must be provided.")
    if not connector_directory.exists():
        raise ValueError(f"Connector directory does not exist: {connector_directory}")

    connector_kebab_name = connector_name
    connector_dockerfile_dir = connector_directory / "build" / "docker"

    if dockerfile_override:
        dockerfile_path = dockerfile_override
    else:
        dockerfile_path = connector_dockerfile_dir / "Dockerfile"
        dockerignore_path = connector_dockerfile_dir / "Dockerfile.dockerignore"
        try:
            dockerfile_text, dockerignore_text = get_dockerfile_templates(
                metadata=metadata,
                connector_directory=connector_directory,
            )
        except FileNotFoundError:
            # If the Dockerfile and .dockerignore are not found in the connector directory,
            # download the templates from the Airbyte repo. This is a fallback
            # in case the Airbyte repo not checked out locally.
            try:
                dockerfile_text, dockerignore_text = _download_dockerfile_defs(
                    connector_language=metadata.data.language,
                )
            except requests.HTTPError as e:
                raise ConnectorImageBuildError(
                    build_args=[],
                    error_text=(
                        "Could not locate local dockerfile templates and "
                        f"failed to download Dockerfile templates from github: {e}"
                    ),
                ) from e

        # ensure the directory exists
        connector_dockerfile_dir.mkdir(parents=True, exist_ok=True)
        dockerfile_path.write_text(dockerfile_text)
        dockerignore_path.write_text(dockerignore_text)

    extra_build_script: str = ""
    build_customization_path = connector_directory / "build_customization.py"
    if build_customization_path.exists():
        extra_build_script = str(build_customization_path)

    dockerfile_path.parent.mkdir(parents=True, exist_ok=True)
    if not metadata.data.connectorBuildOptions:
        raise ValueError(
            "Connector build options are not defined in metadata.yaml. "
            "Please check the connector's metadata file."
        )

    base_image = metadata.data.connectorBuildOptions.baseImage
    build_args: dict[str, str | None] = {
        "BASE_IMAGE": base_image,
        "CONNECTOR_NAME": connector_kebab_name,
        "EXTRA_BUILD_SCRIPT": extra_build_script,
    }

    base_tag = f"{metadata.data.dockerRepository}:{tag}"

    if metadata.data.language == ConnectorLanguage.JAVA:
        # This assumes that the repo root ('airbyte') is three levels above the
        # connector directory (airbyte/airbyte-integrations/connectors/source-foo).
        repo_root = connector_directory.parent.parent.parent
        # For Java connectors, we need to build the connector tar file first.
        subprocess.run(
            [
                "./gradlew",
                f":airbyte-integrations:connectors:{connector_name}:distTar",
            ],
            cwd=repo_root,
            text=True,
            check=True,
        )

    # Always build for AMD64, and optionally for ARM64 if needed locally.
    architectures = [ArchEnum.AMD64]
    if primary_arch == ArchEnum.ARM64:
        architectures += [ArchEnum.ARM64]

    built_images: list[str] = []
    for arch in architectures:
        docker_tag = f"{base_tag}-{arch.value}"
        docker_tag_parts = docker_tag.split("/")
        if len(docker_tag_parts) > 2:
            docker_tag = "/".join(docker_tag_parts[-1:])
        built_images.append(
            _build_image(
                context_dir=connector_directory,
                dockerfile=dockerfile_path,
                metadata=metadata,
                tag=docker_tag,
                arch=arch,
                build_args=build_args,
            )
        )

    _tag_image(
        tag=f"{base_tag}-{primary_arch.value}",
        new_tags=[base_tag],
    )
    if not no_verify:
        success, error_message = verify_connector_image(base_tag)
        if success:
            click.echo(f"Build and verification completed successfully: {base_tag}")
            return base_tag

        click.echo(
            f"Built image failed verification: {base_tag}\nError was:{error_message}", err=True
        )
        sys.exit(1)

    click.echo(f"Build completed successfully: {base_tag}")
    return base_tag


def _download_dockerfile_defs(
    connector_language: ConnectorLanguage,
) -> tuple[str, str]:
    """Download the Dockerfile and .dockerignore templates for the specified connector language.

    We use the requests library to download from the master branch hosted on GitHub.

    Args:
        connector_language: The language of the connector.

    Returns:
        A tuple containing the Dockerfile and .dockerignore templates as strings.

    Raises:
        ValueError: If the connector language is not supported.
        requests.HTTPError: If the download fails.
    """
    print("Downloading Dockerfile and .dockerignore templates from GitHub...")
    # Map ConnectorLanguage to template directory
    language_to_template_suffix = {
        ConnectorLanguage.PYTHON: "python-connector",
        ConnectorLanguage.JAVA: "java-connector",
        ConnectorLanguage.MANIFEST_ONLY: "manifest-only-connector",
    }

    if connector_language not in language_to_template_suffix:
        raise ValueError(f"Unsupported connector language: {connector_language}")

    template_suffix = language_to_template_suffix[connector_language]
    base_url = f"https://github.com/airbytehq/airbyte/raw/master/docker-images/"

    dockerfile_url = f"{base_url}/Dockerfile.{template_suffix}"
    dockerignore_url = f"{base_url}/Dockerfile.{template_suffix}.dockerignore"

    dockerfile_resp = requests.get(dockerfile_url)
    dockerfile_resp.raise_for_status()
    dockerfile_text = dockerfile_resp.text

    dockerignore_resp = requests.get(dockerignore_url)
    dockerignore_resp.raise_for_status()
    dockerignore_text = dockerignore_resp.text

    return dockerfile_text, dockerignore_text


def get_dockerfile_templates(
    metadata: MetadataFile,
    connector_directory: Path,
) -> tuple[str, str]:
    """Get the Dockerfile template for the connector.

    Args:
        metadata: The metadata of the connector.
        connector_name: The name of the connector.

    Raises:
        ValueError: If the connector language is not supported.
        FileNotFoundError: If the Dockerfile or .dockerignore is not found.

    Returns:
        A tuple containing the Dockerfile and .dockerignore templates as strings.
    """
    if metadata.data.language not in [
        ConnectorLanguage.PYTHON,
        ConnectorLanguage.MANIFEST_ONLY,
        ConnectorLanguage.JAVA,
    ]:
        raise ValueError(
            f"Unsupported connector language: {metadata.data.language}. "
            "Please check the connector's metadata file."
        )

    airbyte_repo_root = resolve_airbyte_repo_root(
        from_dir=connector_directory,
    )
    # airbyte_repo_root successfully resolved
    dockerfile_path = (
        airbyte_repo_root / "docker-images" / f"Dockerfile.{metadata.data.language.value}-connector"
    )
    dockerignore_path = (
        airbyte_repo_root
        / "docker-images"
        / f"Dockerfile.{metadata.data.language.value}-connector.dockerignore"
    )
    if not dockerfile_path.exists():
        raise FileNotFoundError(
            f"Dockerfile for {metadata.data.language.value} connector not found at {dockerfile_path}"
        )
    if not dockerignore_path.exists():
        raise FileNotFoundError(
            f".dockerignore for {metadata.data.language.value} connector not found at {dockerignore_path}"
        )

    return dockerfile_path.read_text(), dockerignore_path.read_text()


def run_docker_command(
    cmd: list[str],
    *,
    raise_if_errors: bool = True,
    capture_stdout: bool | Path = False,
    capture_stderr: bool | Path = False,
) -> subprocess.CompletedProcess[str]:
    """Run a Docker command as a subprocess.

    Note: When running Airbyte verbs such as `spec`, `discover`, `read`, etc.,
    use `run_docker_airbyte_command` instead to get an `EntrypointOutput` object as
    the return value and to better handle exceptions sent as messages.

    Args:
        cmd: The command to run as a list of strings.
        check: If True, raises an exception if the command fails. If False, the caller is
            responsible for checking the return code.
        capture_stdout: How to process stdout.
        capture_stderr: If True, captures stderr in memory and returns to the caller.
            If a Path is provided, the output is written to the specified file.

    For stdout and stderr process:
    - If False (the default), stdout is not captured.
    - If True, output is captured in memory and returned within the `CompletedProcess` object.
    - If a Path is provided, the output is written to the specified file. (Recommended for large syncs.)

    Raises:
        subprocess.CalledProcessError: If the command fails and check is True.
    """
    print(f"Running command: {' '.join(cmd)}")

    with ExitStack() as stack:
        # Shared context manager to handle file closing, if needed.
        stderr: TextIOWrapper | int | None
        stdout: TextIOWrapper | int | None

        # If capture_stderr or capture_stdout is a Path, we open the file in write mode.
        # If it's a boolean, we set it to either subprocess.PIPE or None.
        if isinstance(capture_stderr, Path):
            stderr = stack.enter_context(capture_stderr.open("w", encoding="utf-8"))
        elif isinstance(capture_stderr, bool):
            stderr = subprocess.PIPE if capture_stderr is True else None

        if isinstance(capture_stdout, Path):
            stdout = stack.enter_context(capture_stdout.open("w", encoding="utf-8"))
        elif isinstance(capture_stdout, bool):
            stdout = subprocess.PIPE if capture_stdout is True else None

        completed_process: subprocess.CompletedProcess[str] = subprocess.run(
            cmd,
            text=True,
            check=raise_if_errors,
            stderr=stderr,
            stdout=stdout,
        )
        return completed_process


def run_docker_airbyte_command(
    cmd: list[str],
    *,
    raise_if_errors: bool = False,
) -> EntrypointOutput:
    """Run an Airbyte command inside a Docker container.

    This wraps the `run_docker_command` function to process its results and
    return an `EntrypointOutput` object.

    Args:
        cmd: The command to run as a list of strings.
        raise_if_errors: If True, raises an exception if the command fails. If False, the caller is
            responsible for checking the for errors.

    Returns:
        The output of the command as an `EntrypointOutput` object.
    """
    process_result = run_docker_command(
        cmd,
        capture_stdout=True,
        capture_stderr=True,
        raise_if_errors=False,  # We want to handle failures ourselves.
    )
    result_output = EntrypointOutput(
        command=cmd,
        messages=process_result.stdout.splitlines(),
        uncaught_exception=(
            subprocess.CalledProcessError(
                cmd=cmd,
                returncode=process_result.returncode,
                output=process_result.stdout,
                stderr=process_result.stderr,
            )
            if process_result.returncode != 0
            else None
        ),
    )
    if raise_if_errors:
        # If check is True, we raise an exception if there are errors.
        # This will do nothing if there are no errors.
        result_output.raise_if_errors()

    return result_output


def verify_docker_installation() -> bool:
    """Verify Docker is installed and running."""
    try:
        run_docker_command(["docker", "--version"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def verify_connector_image(
    image_name: str,
) -> tuple[bool, str]:
    """Verify the built image by running the spec command.

    Args:
        image_name: The full image name with tag.

    Returns:
        True if the spec command succeeds, False otherwise.
    """
    logger.info(f"Verifying image {image_name} with 'spec' command...")

    try:
        result = run_docker_airbyte_command(
            ["docker", "run", "--rm", image_name, "spec"],
        )
        if result.errors:
            err_msg = result.get_formatted_error_message()
            logger.error(err_msg)
            return False, err_msg

        spec_messages = result.spec_messages
        if not spec_messages:
            err_msg = (
                "The container failed to produce valid output for the `spec` command.\nLog output:\n"
                + str(result.logs)
            )
            logger.error(err_msg)
            return False, err_msg

    except Exception as ex:
        err_msg = f"Unexpected error during image verification: {ex}"
        logger.error(err_msg)
        return False, err_msg

    return True, ""
