# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from github import Auth, Github

from .consts import AIRBYTE_REPO, AUTO_MERGE_LABEL, BASE_BRANCH, CONNECTOR_PATH_PREFIXES
from .env import GITHUB_TOKEN, PRODUCTION
from .helpers import generate_job_summary_as_markdown
from .pr_validators import ENABLED_VALIDATORS

if TYPE_CHECKING:
    from github.Commit import Commit as GithubCommit
    from github.PullRequest import PullRequest
    from github.Repository import Repository as GithubRepo

logging.basicConfig()
logger = logging.getLogger("auto_merge")
logger.setLevel(logging.INFO)


@contextmanager
def github_client() -> Iterator[Github]:
    client = None
    try:
        client = Github(auth=Auth.Token(GITHUB_TOKEN), seconds_between_requests=0)
        yield client
    finally:
        if client:
            client.close()


def check_if_pr_is_auto_mergeable(head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]) -> bool:
    """Run all enabled validators and return if they all pass.

    Args:
        head_commit (GithubCommit): The head commit of the PR
        pr (PullRequest): The PR to check
        required_checks (set[str]): The set of required passing checks

    Returns:
        bool: True if the PR is auto-mergeable, False otherwise
    """
    for validator in ENABLED_VALIDATORS:
        is_valid, error = validator(head_commit, pr, required_checks)
        if not is_valid:
            if error:
                logger.info(f"PR #{pr.number} - {error}")
            return False
    return True


def process_pr(repo: GithubRepo, pr: PullRequest, required_passing_contexts: set[str], dry_run: bool) -> None | PullRequest:
    """Process a PR to see if it is auto-mergeable and merge it if it is.

    Args:
        repo (GithubRepo): The repository the PR is in
        pr (PullRequest): The PR to process
        required_passing_contexts (set[str]): The set of required passing checks
        dry_run (bool): Whether to actually merge the PR or not

    Returns:
        None | PullRequest: The PR if it was merged, None otherwise
    """
    logger.info(f"Processing PR #{pr.number}")
    head_commit = repo.get_commit(sha=pr.head.sha)
    if check_if_pr_is_auto_mergeable(head_commit, pr, required_passing_contexts):
        if not dry_run:
            pr.merge()
            logger.info(f"PR #{pr.number} was auto-merged")
            return pr
        else:
            logger.info(f"PR #{pr.number} is auto-mergeable but dry-run is enabled")
    return None


def back_off_if_rate_limited(github_client: Github) -> None:
    """Sleep if the rate limit is reached

    Args:
        github_client (Github): The Github client to check the rate limit of
    """
    remaining_requests, _ = github_client.rate_limiting
    if remaining_requests < 100:
        logging.warning(f"Rate limit almost reached. Remaining requests: {remaining_requests}")
    if remaining_requests == 0:
        logging.warning(f"Rate limited. Sleeping for {github_client.rate_limiting_resettime - time.time()} seconds")
        time.sleep(github_client.rate_limiting_resettime - time.time())
    return None


def auto_merge() -> None:
    """Main function to auto-merge PRs that are candidates for auto-merge.
    If the AUTO_MERGE_PRODUCTION environment variable is not set to "true", this will be a dry run.
    """
    dry_run = PRODUCTION is False
    if PRODUCTION:
        logger.info("Running auto-merge in production mode. Mergeable PRs will be merged!")
    else:
        logger.info("Running auto-merge in dry mode mode. Mergeable PRs won't be merged!")

    with github_client() as gh_client:
        repo = gh_client.get_repo(AIRBYTE_REPO)
        main_branch = repo.get_branch(BASE_BRANCH)
        logger.info(f"Fetching required passing contexts for {BASE_BRANCH}")
        required_passing_contexts = set(main_branch.get_required_status_checks().contexts)
        candidate_issues = gh_client.search_issues(f"repo:{AIRBYTE_REPO} is:pr label:{AUTO_MERGE_LABEL} base:{BASE_BRANCH} state:open")
        prs = [issue.as_pull_request() for issue in candidate_issues]
        logger.info(f"Found {len(prs)} open PRs targeting {BASE_BRANCH} with the {AUTO_MERGE_LABEL} label")
        merged_prs = []
        for pr in prs:
            back_off_if_rate_limited(gh_client)
            if merged_pr := process_pr(repo, pr, required_passing_contexts, dry_run):
                merged_prs.append(merged_pr)
        if os.environ["GITHUB_STEP_SUMMARY"]:
            job_summary_path = Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text(generate_job_summary_as_markdown(merged_prs))
            logger.info(f"Job summary written to {job_summary_path}")
