# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from github import Auth, Github

from .consts import AIRBYTE_REPO, AUTO_MERGE_LABEL, BASE_BRANCH, CONNECTOR_PATH_PREFIXES
from .env import GITHUB_TOKEN, PRODUCTION

if TYPE_CHECKING:
    from github.Commit import Commit as GithubCommit
    from github.File import File as GithubFile
    from github.PullRequest import PullRequest
    from github.Repository import Repository as GithubRepo

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


@contextmanager
def github_client() -> Iterator[Github]:
    client = None
    try:
        client = Github(auth=Auth.Token(GITHUB_TOKEN), seconds_between_requests=0)
        yield client
    finally:
        if client:
            client.close()


def check_if_modifies_connectors_only(modified_files: Iterable[GithubFile]) -> bool:
    """Check if all modified files are in CONNECTOR_PATH_PREFIXES

    Args:
        modified_files (Iterable[GithubFile]): All the modified files on a PR.

    Returns:
        bool: True if all modified files are in CONNECTOR_PATH_PREFIXES, False otherwise
    """
    for file in modified_files:
        if not any(file.filename.startswith(prefix) for prefix in CONNECTOR_PATH_PREFIXES):
            return False
    return True


def check_if_head_commit_passes_all_required_checks(head_commit: GithubCommit, required_checks: set[str]) -> bool:
    """Required checks can be a mix of status contexts and check runs. A head commit is considered to pass all required checks if it has successful statuses and check runs for all required checks.

    Args:
        head_commit (GithubCommit): The head commit of the PR
        required_checks (set[str]): The set of required passing checks

    Returns:
        bool: True if the head commit passes all required checks, False otherwise
    """
    successful_status_contexts = [commit_status.context for commit_status in head_commit.get_statuses() if commit_status.state == "success"]
    successful_check_runs = [check_run.name for check_run in head_commit.get_check_runs() if check_run.conclusion == "success"]
    successful_contexts = set(successful_status_contexts + successful_check_runs)
    return required_checks.issubset(successful_contexts)


def check_if_pr_is_auto_mergeable(head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]) -> bool:
    """A PR is considered auto-mergeable if:
    - it has the AUTO_MERGE_LABEL
    - it targets the BASE_BRANCH
    - it touches only files in CONNECTOR_PATH_PREFIXES
    - the head commit passes all required checks

    Args:
        head_commit (GithubCommit): The head commit of the PR
        pr (PullRequest): The PR to check
        required_checks (set[str]): The set of required passing checks

    Returns:
        bool: True if the PR is auto-mergeable, False otherwise
    """
    has_auto_merge_label = any(label.name == AUTO_MERGE_LABEL for label in pr.labels)
    if not has_auto_merge_label:
        logging.info(f"PR {pr.number} does not have the {AUTO_MERGE_LABEL} label")
        return False
    targets_main_branch = pr.base.ref == BASE_BRANCH
    if not targets_main_branch:
        logging.info(f"PR {pr.number} does not target {BASE_BRANCH}")
        return False
    touches_connectors_only = check_if_modifies_connectors_only(pr.get_files())
    if not touches_connectors_only:
        logging.info(f"PR {pr.number} touches files outside connectors")
        return False
    passes_all_checks = check_if_head_commit_passes_all_required_checks(head_commit, required_checks)
    if not passes_all_checks:
        logging.info(f"PR {pr.number} does not pass all required checks")
        return False
    logging.info(f"PR {pr.number} is a candidate for auto-merge! 🎉")
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
    logging.info(f"Processing PR {pr.number}")
    head_commit = repo.get_commit(sha=pr.head.sha)
    if check_if_pr_is_auto_mergeable(head_commit, pr, required_passing_contexts):
        if not dry_run:
            pr.merge()
            logging.info(f"PR {pr.number} auto-merged")
            return pr
        else:
            logging.info(f"PR {pr.number} is auto-mergeable but dry-run is enabled")


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


def generate_job_summary_as_markdown(merged_prs: list[PullRequest]) -> str:
    """Generate a markdown summary of the merged PRs

    Args:
        merged_prs (list[PullRequest]): The PRs that were merged

    Returns:
        str: The markdown summary
    """
    summary_time = time.strftime("%Y-%m-%d %H:%M:%S")
    header = "# Auto-merged PRs"
    details = f"Summary generated at {summary_time}"
    if not merged_prs:
        return f"{header}\n\n{details}\n\n**No PRs were auto-merged**\n"
    merged_pr_list = "\n".join([f"- [#{pr.number} - {pr.title}]({pr.html_url})" for pr in merged_prs])
    return f"{header}\n\n{details}\n\n{merged_pr_list}\n"


def auto_merge() -> None:
    """Main function to auto-merge PRs that are candidates for auto-merge.
    If the AUTO_MERGE_PRODUCTION environment variable is not set to "true", this will be a dry run.
    """
    dry_run = PRODUCTION is False
    with github_client() as gh_client:
        repo = gh_client.get_repo(AIRBYTE_REPO)
        main_branch = repo.get_branch(BASE_BRANCH)
        logging.info(f"Fetching required passing contexts for {BASE_BRANCH}")
        required_passing_contexts = set(main_branch.get_required_status_checks().contexts)
        candidate_issues = gh_client.search_issues(f"repo:{AIRBYTE_REPO} is:pr label:{AUTO_MERGE_LABEL} base:{BASE_BRANCH} state:open")
        prs = [issue.as_pull_request() for issue in candidate_issues]
        logging.info(f"Found {len(prs)} open PRs targeting {BASE_BRANCH} with the {AUTO_MERGE_LABEL} label")
        merged_prs = []
        for pr in prs:
            back_off_if_rate_limited(gh_client)
            if merged_pr := process_pr(repo, pr, required_passing_contexts, dry_run):
                merged_prs.append(merged_pr)
        if PRODUCTION:
            os.environ["GITHUB_STEP_SUMMARY"] = generate_job_summary_as_markdown(merged_prs)
