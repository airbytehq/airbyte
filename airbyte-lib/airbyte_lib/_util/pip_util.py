# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
"""Internal utility functions for dealing with pip."""

from __future__ import annotations


def github_pip_url(
    owner: str = "airbytehq",
    repo: str = "airbyte",
    *,
    branch_or_ref: str | None = None,
    package_name: str | None = None,
    subdirectory: str | None = None,
) -> str:
    """Return the pip URL for a GitHub repository.

    Results will look like:
    - `git+airbytehq/airbyte.git@master#egg=airbyte-lib&subdirectory=airbyte-lib'
    - `git+airbytehq/airbyte.git@my-branch#egg=source-github
       &subdirectory=airbyte-integrations/connectors/source-github'
    """
    if not branch_or_ref:
        branch_or_ref = "master" if repo == "airbyte" else "main"

    result = f"git+{owner}/{repo}.git"
    if branch_or_ref:
        result += f"@{branch_or_ref}"
    if package_name:
        result += f"#egg={package_name}"
    if subdirectory:
        result += f"#subdirectory={subdirectory}"

    return result


def connector_pip_url(
    connector_name: str,
    *,
    branch: str | None = None,
) -> str:
    """Return a pip URL for a connector in the main `airbytehq/airbyte` git repo."""
    if not connector_name.startswith("source-") and not connector_name.startswith("destination-"):
        connector_name = "source-" + connector_name

    return github_pip_url(
        branch=branch,
        package_name=f"source-{connector_name}",
        subdirectory=f"airbyte-integrations/connectors/{connector_name}",
    )
