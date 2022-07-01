#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import hashlib
import json
from typing import Any

import click
from deepdiff import DeepDiff

SECRET_MASK = "**********"


def hash_config(configuration: dict) -> str:
    """Computes a SHA256 hash from a dictionnary.

    Args:
        configuration (dict): The configuration to hash

    Returns:
        str: _description_
    """
    stringified = json.dumps(configuration, sort_keys=True)
    return hashlib.sha256(stringified.encode("utf-8")).hexdigest()


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
