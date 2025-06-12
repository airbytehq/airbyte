#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Module grouping functions interacting with the GitHub API."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import github as github_sdk
from connector_ops.utils import console  # type: ignore

from pipelines import main_logger
from pipelines.consts import CIContext
from pipelines.models.secrets import Secret

if TYPE_CHECKING:
    from logging import Logger
    from typing import Iterable, List, Optional


DEFAULT_AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"
AIRBYTE_GITHUB_REPO = os.environ.get("AIRBYTE_GITHUB_REPO", DEFAULT_AIRBYTE_GITHUB_REPO)
AIRBYTE_GITHUBUSERCONTENT_URL_PREFIX = f"https://raw.githubusercontent.com/{AIRBYTE_GITHUB_REPO}"
AIRBYTE_GITHUB_REPO_URL_PREFIX = f"https://github.com/{AIRBYTE_GITHUB_REPO}"
AIRBYTE_GITHUB_REPO_URL = f"{AIRBYTE_GITHUB_REPO_URL_PREFIX}.git"
BASE_BRANCH = "master"


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
        github_client = github_sdk.Github(auth=github_sdk.Auth.Token(os.environ["CI_GITHUB_ACCESS_TOKEN"]))
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


def get_pull_request(pull_request_number: int, github_access_token: Secret) -> github_sdk.PullRequest.PullRequest:
    """Get a pull request object from its number.

    Args:
        pull_request_number (str): The number of the pull request to get.
        github_access_token (Secret): The GitHub access token to use to authenticate.
    Returns:
        PullRequest: The pull request object.
    """
    github_client = github_sdk.Github(auth=github_sdk.Auth.Token(github_access_token.value))
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


@dataclass
class ChangedFile:
    path: str
    sha: str | None


def create_or_update_github_pull_request(
    modified_repo_files: Iterable[Path],
    github_token: str,
    branch_id: str,
    commit_message: str,
    pr_title: str,
    pr_body: str,
    repo_name: str = AIRBYTE_GITHUB_REPO,
    logger: Optional[Logger] = None,
    skip_ci: bool = False,
    labels: Optional[Iterable[str]] = None,
    force_push: bool = True,
) -> github_sdk.PullRequest.PullRequest:
    logger = logger or main_logger
    g = github_sdk.Github(auth=github_sdk.Auth.Token(github_token))
    repo = g.get_repo(repo_name)
    commit_message = commit_message if not skip_ci else f"[skip ci] {commit_message}"

    changed_files: List[ChangedFile] = []
    for modified_file in modified_repo_files:  # these are relative to the repo root
        if modified_file.exists():
            with open(modified_file, "rb") as file:
                logger.info(f"Reading file: {modified_file}")
                content = base64.b64encode(file.read()).decode("utf-8")  # Encode file content to base64
                blob = repo.create_git_blob(content, "base64")
                changed_file = ChangedFile(path=str(modified_file), sha=blob.sha)
            changed_files.append(changed_file)
        else:
            logger.info(f"{modified_file} no longer exists, adding to PR as a deletion")
            changed_file = ChangedFile(path=str(modified_file), sha=None)
            changed_files.append(changed_file)
    existing_ref = None
    try:
        existing_ref = repo.get_git_ref(f"heads/{branch_id}")
        logger.info(f"Git ref {branch_id} already exists")
    except github_sdk.GithubException:
        pass

    base_sha = repo.get_branch(BASE_BRANCH).commit.sha
    if not existing_ref:
        repo.create_git_ref(f"refs/heads/{branch_id}", base_sha)

    parent_commit = repo.get_git_commit(base_sha)
    parent_tree = repo.get_git_tree(base_sha)

    # Filter and update tree elements
    tree_elements: List[github_sdk.InputGitTreeElement] = []
    for changed_file in changed_files:
        if changed_file.sha is None:
            # make sure it's actually in the current tree
            try:
                # Attempt to get the file from the specified commit
                repo.get_contents(changed_file.path, ref=base_sha)
                # logger.info(f"File {changed_file.path} exists in commit {base_sha}")
            except github_sdk.UnknownObjectException:
                # don't need to add it to the tree
                logger.info(f"{changed_file.path} not in parent: {base_sha}")
                continue

        # Update or new file addition or needed deletion
        tree_elements.append(
            github_sdk.InputGitTreeElement(
                path=changed_file.path,
                mode="100644",
                type="blob",
                sha=changed_file.sha,
            )
        )

    # Create a new commit pointing to that tree
    tree = repo.create_git_tree(tree_elements, base_tree=parent_tree)
    commit = repo.create_git_commit(commit_message, tree, [parent_commit])
    repo.get_git_ref(f"heads/{branch_id}").edit(sha=commit.sha, force=force_push)
    # Check if there's an existing pull request
    found_pr = None
    open_pulls = repo.get_pulls(state="open", base=BASE_BRANCH)
    for pr in open_pulls:
        if pr.head.ref == branch_id:
            found_pr = pr
            logger.info(f"Pull request already exists: {pr.html_url}")
    if found_pr:
        pull_request = found_pr
        found_pr.edit(title=pr_title, body=pr_body)
    else:
        pull_request = repo.create_pull(
            title=pr_title,
            body=pr_body,
            base=BASE_BRANCH,
            head=branch_id,
        )
        logger.info(f"Created pull request: {pull_request.html_url}")

    labels = labels or []
    for label in labels:
        pull_request.add_to_labels(label)
        logger.info(f"Added label {label} to pull request")

    return pull_request


def is_automerge_pull_request(pull_request: Optional[github_sdk.PullRequest.PullRequest]) -> bool:
    labels = [label.name for label in pull_request.get_labels()] if pull_request else []
    if labels and "auto-merge" in labels:
        return True
    return False
