# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import re
from pathlib import Path
from typing import Set, Tuple

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
        if connector_directory.is_dir() and (connector_directory / METADATA_FILE_NAME).exists():
            connectors.append(Connector(connector_directory.name))
    return set(connectors)


def gcs_uri_to_bucket_key(gcs_uri: str) -> Tuple[str, str]:
    # Ensure the GCS URI follows the expected pattern
    match = re.match(r"^gs://([^/]+)/(.+)$", gcs_uri)
    if not match:
        raise ValueError(f"Invalid GCS URI: {gcs_uri}")

    bucket, key = match.groups()
    return bucket, key
