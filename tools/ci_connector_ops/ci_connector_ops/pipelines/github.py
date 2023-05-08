#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module grouping functions interacting with the GitHub API."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from ci_connector_ops.utils import console

if TYPE_CHECKING:
    from logging import Logger

from github import Github

AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


def safe_log(logger: Optional[Logger], message: str, level: str = "info") -> None:
    """Log a message to a logger if one is available, otherwise print to the console."""
    if logger:
        log_method = getattr(logger, level.lower())
        log_method(message)
    else:
        console.print(message)


def update_commit_status_check(
    sha: str, state: str, target_url: str, description: str, context: str, is_optional=False, should_send=True, logger: Logger = None
):
    """Call the GitHub API to create commit status check.

    Args:
        sha (str): Hash of the commit for which you want to create a status check.
        state (str): The check state (success, failure, pending)
        target_url (str): The URL to attach to the commit check for details.
        description (str): Description of the check that is run.
        context (str): Name of the Check context e.g: source-pokeapi tests
        should_send (bool, optional): Whether the commit check should actually be sent to GitHub API. Defaults to True.
        logger (Logger, optional): A logger to log info about updates. Defaults to None.
    """
    if not should_send:
        return

    safe_log(logger, f"Attempting to create {state} status for commit {sha} on Github in {context} context.")
    try:
        github_client = Github(os.environ["CI_GITHUB_ACCESS_TOKEN"])
        airbyte_repo = github_client.get_repo(AIRBYTE_GITHUB_REPO)
    except Exception as e:
        if logger:
            logger.error("No commit status check sent, the connection to Github API failed", exc_info=True)
        else:
            console.print(e)
        return

    # If the check is optional, we don't want to fail the build if it fails.
    # Instead, we want to mark it as a warning.
    # Unfortunately, Github doesn't have a warning state, so we use success instead.
    if is_optional and state == "failure":
        state = "success"
        description = f"[WARNING] optional check failed {context}: {description}"

    airbyte_repo.get_commit(sha=sha).create_status(
        state=state,
        target_url=target_url,
        description=description,
        context=context,
    )
    safe_log(logger, f"Created {state} status for commit {sha} on Github in {context} context with desc: {description}.")
