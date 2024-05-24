#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module grouping functions interacting with the GitHub API."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional

from connector_ops.utils import console  # type: ignore
from pipelines import main_logger
from pipelines.consts import CIContext
from pipelines.models.secrets import Secret

if TYPE_CHECKING:
    from logging import Logger

from github import Auth, Github, PullRequest

AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


def safe_log(logger: Optional[Logger], message: str, level: str = "info") -> None:
    """Log a message to a logger if one is available, otherwise print to the console."""
    if logger:
        log_method = getattr(logger, level.lower())
        log_method(message)
    else:
        main_logger.info(message)


def update_commit_status_check(
    sha: str,
    state: str,
    target_url: str,
    description: str,
    context: str,
    is_optional: bool = False,
    should_send: bool = True,
    logger: Optional[Logger] = None,
) -> None:
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
        github_client = Github(auth=Auth.Token(os.environ["CI_GITHUB_ACCESS_TOKEN"]))
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

    context = context if bool(os.environ.get("PRODUCTION", False)) is True else f"[please ignore] {context}"
    airbyte_repo.get_commit(sha=sha).create_status(
        state=state,
        target_url=target_url,
        description=description,
        context=context,
    )
    safe_log(logger, f"Created {state} status for commit {sha} on Github in {context} context with desc: {description}.")


def get_pull_request(pull_request_number: int, github_access_token: Secret) -> PullRequest.PullRequest:
    """Get a pull request object from its number.

    Args:
        pull_request_number (str): The number of the pull request to get.
        github_access_token (Secret): The GitHub access token to use to authenticate.
    Returns:
        PullRequest: The pull request object.
    """
    github_client = Github(auth=Auth.Token(github_access_token.value))
    airbyte_repo = github_client.get_repo(AIRBYTE_GITHUB_REPO)
    return airbyte_repo.get_pull(pull_request_number)


def update_global_commit_status_check_for_tests(click_context: dict, github_state: str, logger: Optional[Logger] = None) -> None:

    update_commit_status_check(
        click_context["git_revision"],
        github_state,
        click_context["gha_workflow_run_url"],
        click_context["global_status_check_description"],
        click_context["global_status_check_context"],
        should_send=click_context.get("ci_context") == CIContext.PULL_REQUEST,
        logger=logger,
    )
