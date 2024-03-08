# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Internal utility functions for dealing with pip."""

from __future__ import annotations


def github_pip_url(
    owner: str = "airbytehq",
    repo: str = "airbyte",
    *,
    package_name: str,
    branch_or_ref: str | None = None,
    subdirectory: str | None = None,
) -> str:
    """Return the pip URL for a GitHub repository.

    Results will look like:
    - `git+airbytehq/airbyte.git#egg=airbyte-lib&subdirectory=airbyte-lib'
    - `git+airbytehq/airbyte.git@master#egg=airbyte-lib&subdirectory=airbyte-lib'
    - `git+airbytehq/airbyte.git@my-branch#egg=source-github
       &subdirectory=airbyte-integrations/connectors/source-github'
    """
    result = f"git+https://github.com/{owner}/{repo}.git"

    if branch_or_ref:
        result += f"@{branch_or_ref}"

    next_delimiter = "#"
    if package_name:
        result += f"{next_delimiter}egg={package_name}"
        next_delimiter = "&"

    if subdirectory:
        result += f"{next_delimiter}subdirectory={subdirectory}"

    return result


def connector_pip_url(
    connector_name: str,
    /,
    branch: str,
    *,
    owner: str | None = None,
) -> str:
    """Return a pip URL for a connector in the main `airbytehq/airbyte` git repo."""
    owner = owner or "airbytehq"
    if not connector_name.startswith("source-") and not connector_name.startswith("destination-"):
        connector_name = "source-" + connector_name

    return github_pip_url(
        owner=owner,
        repo="airbyte",
        branch_or_ref=branch,
        package_name=connector_name,
        subdirectory=f"airbyte-integrations/connectors/{connector_name}",
    )
