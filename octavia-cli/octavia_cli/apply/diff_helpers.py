#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import hashlib
from typing import Any

import click
from deepdiff import DeepDiff

SECRET_MASK = "**********"


def compute_checksum(file_path: str) -> str:
    """Compute SHA256 checksum from a file

    Args:
        file_path (str): Path for the file for which you want to compute a checksum.

    Returns:
        str: The computed hash digest
    """
    BLOCK_SIZE = 65536
    file_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        fb = f.read(BLOCK_SIZE)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)
    return file_hash.hexdigest()


def exclude_secrets_from_diff(obj: Any, path: str) -> bool:
    """Callback function used with DeepDiff to ignore secret values from the diff.

    Args:
        obj (Any): Object for which a diff will be computed.
        path (str): unused.

    Returns:
        bool: Whether to ignore the object from the diff.
    """
    if isinstance(obj, str):
        return True if SECRET_MASK in obj else False
    else:
        return False


def compute_diff(a: Any, b: Any) -> DeepDiff:
    """Wrapper around the DeepDiff computation.

    Args:
        a (Any): Object to compare with b.
        b (Any): Object to compare with a.

    Returns:
        DeepDiff: the computed diff object.
    """
    return DeepDiff(a, b, view="tree", exclude_obj_callback=exclude_secrets_from_diff)


def display_diff_line(diff_line: str) -> None:
    """Prettify a diff line and print it to standard output.

    Args:
        diff_line (str): The diff line to display.
    """
    if "changed from" in diff_line:
        color = "yellow"
        prefix = "E"
    elif "added" in diff_line:
        color = "green"
        prefix = "+"
    elif "removed" in diff_line:
        color = "red"
        prefix = "-"
    else:
        prefix = ""
        color = None
    click.echo(click.style(f"\t{prefix} - {diff_line}", fg=color))
