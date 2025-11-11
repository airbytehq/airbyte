# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Airbyte CDK 'image' commands.

The `airbyte-cdk image build` command provides a simple way to work with Airbyte
connector images.
"""

import sys
from pathlib import Path

import rich_click as click

from airbyte_cdk.cli.airbyte_cdk._connector import run_connector_tests
from airbyte_cdk.models.connector_metadata import MetadataFile
from airbyte_cdk.utils.connector_paths import resolve_connector_name_and_directory
from airbyte_cdk.utils.docker import (
    ConnectorImageBuildError,
    build_connector_image,
    verify_docker_installation,
)


@click.group(
    name="image",
    help=__doc__.replace("\n", "\n\n"),  # Render docstring as help text (markdown)
)
def image_cli_group() -> None:
    """Commands for working with connector Docker images."""


@image_cli_group.command()
@click.argument(
    "connector",
    required=False,
    type=str,
    metavar="[CONNECTOR]",
)
@click.option("--tag", default="dev", help="Tag to apply to the built image (default: dev)")
@click.option("--no-verify", is_flag=True, help="Skip verification of the built image")
@click.option(
    "--dockerfile",
    type=click.Path(exists=True, file_okay=True, path_type=Path),
    help="Optional. Override the Dockerfile used for building the image.",
)
def build(
    connector: str | None = None,
    *,
    tag: str = "dev",
    no_verify: bool = False,
    dockerfile: Path | None = None,
) -> None:
    """Build a connector Docker image.

    [CONNECTOR] can be a connector name (e.g. 'source-pokeapi'), a path to a connector directory, or omitted to use the current working directory.
    If a string containing '/' is provided, it is treated as a path. Otherwise, it is treated as a connector name.
    """
    if not verify_docker_installation():
        click.echo(
            "Docker is not installed or not running. Please install Docker and try again.", err=True
        )
        sys.exit(1)

    connector_name, connector_directory = resolve_connector_name_and_directory(connector)

    metadata_file_path: Path = connector_directory / "metadata.yaml"
    try:
        metadata = MetadataFile.from_file(metadata_file_path)
    except (FileNotFoundError, ValueError) as e:
        click.echo(
            f"Error loading metadata file '{metadata_file_path}': {e!s}",
            err=True,
        )
        sys.exit(1)
    click.echo(f"Building Image for Connector: {metadata.data.dockerRepository}:{tag}")
    try:
        build_connector_image(
            connector_directory=connector_directory,
            connector_name=connector_name,
            metadata=metadata,
            tag=tag,
            no_verify=no_verify,
            dockerfile_override=dockerfile or None,
        )
    except ConnectorImageBuildError as e:
        click.echo(
            f"Error building connector image: {e!s}",
            err=True,
        )
        sys.exit(1)


@image_cli_group.command("test")
@click.argument(
    "connector",
    required=False,
    type=str,
    metavar="[CONNECTOR]",
)
@click.option(
    "--image",
    help="Image to test, instead of building a new one.",
)
@click.option(
    "--no-creds",
    is_flag=True,
    default=False,
    help="Skip tests that require credentials (marked with 'requires_creds').",
)
def image_test(  # "image test" command
    connector: str | None = None,
    *,
    image: str | None = None,
    no_creds: bool = False,
) -> None:
    """Test a connector Docker image.

    [CONNECTOR] can be a connector name (e.g. 'source-pokeapi'), a path to a connector directory, or omitted to use the current working directory.
    If a string containing '/' is provided, it is treated as a path. Otherwise, it is treated as a connector name.

    If an image is provided, it will be used for testing instead of building a new one.

    Note: You should run `airbyte-cdk secrets fetch` before running this command to ensure
    that the secrets are available for the connector tests.
    """
    if not verify_docker_installation():
        click.echo(
            "Docker is not installed or not running. Please install Docker and try again.", err=True
        )
        sys.exit(1)

    connector_name, connector_directory = resolve_connector_name_and_directory(connector)

    # Select only tests with the 'image_tests' mark
    pytest_filter = "image_tests"
    if no_creds:
        pytest_filter += " and not requires_creds"

    pytest_args = ["-m", pytest_filter]
    if not image:
        metadata_file_path: Path = connector_directory / "metadata.yaml"
        try:
            metadata = MetadataFile.from_file(metadata_file_path)
        except (FileNotFoundError, ValueError) as e:
            click.echo(
                f"Error loading metadata file '{metadata_file_path}': {e!s}",
                err=True,
            )
            sys.exit(1)

        tag = "dev-latest"
        image = f"{metadata.data.dockerRepository}:{tag}"
        click.echo(f"Building Image for Connector: {image}")
        try:
            image = build_connector_image(
                connector_directory=connector_directory,
                connector_name=connector_name,
                metadata=metadata,
                tag=tag,
                no_verify=True,
            )
        except ConnectorImageBuildError as e:
            click.echo(
                f"Error building connector image: {e!s}",
                err=True,
            )
            sys.exit(1)

    pytest_args.extend(["--connector-image", image])

    click.echo(f"Testing Connector Image: {image}")
    run_connector_tests(
        connector_name=connector_name,
        connector_directory=connector_directory,
        extra_pytest_args=pytest_args,
    )


__all__ = [
    "image_cli_group",
]
