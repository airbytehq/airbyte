# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from typing import Callable, List, Set, Tuple

    from dagger import Container

from connector_ops.utils import METADATA_FILE_NAME, Connector  # type: ignore


def remove_strict_encrypt_suffix(connector_technical_name: str) -> str:
    """Remove the strict encrypt suffix from a connector name.

    Args:
        connector_technical_name (str): the connector name.

    Returns:
        str: the connector name without the strict encrypt suffix.
    """
    strict_encrypt_suffixes = [
        "-strict-encrypt",
        "-secure",
    ]

    for suffix in strict_encrypt_suffixes:
        if connector_technical_name.endswith(suffix):
            new_connector_technical_name = connector_technical_name.replace(suffix, "")
            return new_connector_technical_name
    return connector_technical_name


def get_all_connectors_in_directory(directory: Path) -> Set[Connector]:
    """Get all connectors in a directory.

    Args:
        directory (Path): the directory to search for connectors.

    Returns:
        List[Connector]: the list of connectors in the directory.
    """
    connectors = []
    for connector_directory in directory.iterdir():
        if (
            connector_directory.is_dir()
            and (connector_directory / METADATA_FILE_NAME).exists()
            and "scaffold" not in str(connector_directory)
        ):
            connectors.append(Connector(remove_strict_encrypt_suffix(connector_directory.name)))
    return set(connectors)


def gcs_uri_to_bucket_key(gcs_uri: str) -> Tuple[str, str]:
    # Ensure the GCS URI follows the expected pattern
    match = re.match(r"^gs://([^/]+)/(.+)$", gcs_uri)
    if not match:
        raise ValueError(f"Invalid GCS URI: {gcs_uri}")

    bucket, key = match.groups()
    return bucket, key


def never_fail_exec(command: List[str]) -> Callable[[Container], Container]:
    """
    Wrap a command execution with some bash sugar to always exit with a 0 exit code but write the actual exit code to a file.

    Underlying issue:
        When a classic dagger with_exec is returning a >0 exit code an ExecError is raised.
        It's OK for the majority of our container interaction.
        But some execution, like running CAT, are expected to often fail.
        In CAT we don't want ExecError to be raised on container interaction because CAT might write updated secrets that we need to pull from the container after the test run.
        The bash trick below is a hack to always return a 0 exit code but write the actual exit code to a file.
        The file is then read by the pipeline to determine the exit code of the container.

    Args:
        command (List[str]): The command to run in the container.

    Returns:
        Callable: _description_
    """

    def never_fail_exec_inner(container: Container) -> Container:
        return container.with_exec(["sh", "-c", f"{' '.join(command)}; echo $? > /exit_code"])

    return never_fail_exec_inner
