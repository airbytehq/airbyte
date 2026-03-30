#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
from typing import TYPE_CHECKING, Optional, Set

import git
from dagger import Connection, SessionError

from pipelines import main_logger
from pipelines.consts import CIContext
from pipelines.dagger.containers.git import checked_out_git_container
from pipelines.helpers.github import AIRBYTE_GITHUB_REPO_URL
from pipelines.helpers.utils import DAGGER_CONFIG, DIFF_FILTER

if TYPE_CHECKING:
    from github import PullRequest


def get_current_git_revision() -> str:  # noqa D103
    return git.Repo(search_parent_directories=True).head.object.hexsha


def get_current_git_branch() -> str:  # noqa D103
    return git.Repo(search_parent_directories=True).active_branch.name


async def get_modified_files_in_branch_remote(
    current_git_repo_url: str, current_git_branch: str, current_git_revision: str, diffed_branch: str = "master", retries: int = 3
) -> Set[str]:
    """Use git diff to spot the modified files on the remote branch."""
    try:
        async with Connection(DAGGER_CONFIG) as dagger_client:
            container = await checked_out_git_container(
                dagger_client, current_git_branch, current_git_revision, diffed_branch, repo_url=current_git_repo_url
            )
            modified_files = await container.with_exec(
                ["diff", f"--diff-filter={DIFF_FILTER}", "--name-only", f"origin/{diffed_branch}...target/{current_git_branch}"],
                use_entrypoint=True,
            ).stdout()
    except SessionError:
        if retries > 0:
            return await get_modified_files_in_branch_remote(
                current_git_repo_url, current_git_branch, current_git_revision, diffed_branch, retries - 1
            )
        else:
            raise
    return set(modified_files.split("\n"))


def get_modified_files_local(current_git_revision: str, diffed: str = "master") -> Set[str]:
    """Use git diff and git status to spot the modified files in the local repo."""
    airbyte_repo = git.Repo()
    modified_files = airbyte_repo.git.diff(f"--diff-filter={DIFF_FILTER}", "--name-only", f"{diffed}...{current_git_revision}").split("\n")
    status_output = airbyte_repo.git.status("--porcelain")
    for not_committed_change in status_output.split("\n"):
        file_path = not_committed_change.strip().split(" ")[-1]
        if file_path:
            modified_files.append(file_path)
    return set(modified_files)


async def get_modified_files_in_branch(
    current_repo_url: str, current_git_branch: str, current_git_revision: str, diffed_branch: str, is_local: bool = True
) -> Set[str]:
    """Retrieve the list of modified files on the branch."""
    if is_local:
        return get_modified_files_local(current_git_revision, diffed_branch)
    else:
        return await get_modified_files_in_branch_remote(current_repo_url, current_git_branch, current_git_revision, diffed_branch)


async def get_modified_files_in_commit_remote(current_git_branch: str, current_git_revision: str, retries: int = 3) -> Set[str]:
    try:
        async with Connection(DAGGER_CONFIG) as dagger_client:
            container = await checked_out_git_container(dagger_client, current_git_branch, current_git_revision)
            modified_files = await container.with_exec(
                ["diff-tree", "--no-commit-id", "--name-only", current_git_revision, "-r"], use_entrypoint=True
            ).stdout()
    except SessionError:
        if retries > 0:
            return await get_modified_files_in_commit_remote(current_git_branch, current_git_revision, retries - 1)
        else:
            raise
    return set(modified_files.split("\n"))


def get_modified_files_in_commit_local(current_git_revision: str) -> Set[str]:
    airbyte_repo = git.Repo()
    modified_files = airbyte_repo.git.diff_tree("--no-commit-id", "--name-only", current_git_revision, "-r").split("\n")
    return set(modified_files)


async def get_modified_files_in_commit(current_git_branch: str, current_git_revision: str, is_local: bool = True) -> Set[str]:
    if is_local:
        return get_modified_files_in_commit_local(current_git_revision)
    else:
        return await get_modified_files_in_commit_remote(current_git_branch, current_git_revision)


@functools.cache
def get_git_repo() -> git.Repo:
    """Retrieve the git repo."""
    return git.Repo(search_parent_directories=True)


@functools.cache
def get_git_repo_path() -> str:
    """Retrieve the git repo path."""
    return str(get_git_repo().working_tree_dir)


def get_modified_files_from_pull_request(pull_request: "PullRequest.PullRequest") -> Set[str]:
    """Get the list of modified files from a pull request using the GitHub API.

    This is more reliable than git diff for fork PRs because GitHub already knows
    which files are changed in the PR, regardless of how far behind the fork is from master.

    Args:
        pull_request: The PyGithub PullRequest object.

    Returns:
        Set[str]: The set of modified file paths.
    """
    modified_files = set()
    for file in pull_request.get_files():
        modified_files.add(file.filename)
    return modified_files


async def get_modified_files(
    git_branch: str,
    git_revision: str,
    diffed_branch: str,
    is_local: bool,
    ci_context: CIContext,
    git_repo_url: str = AIRBYTE_GITHUB_REPO_URL,
    pull_request: Optional["PullRequest.PullRequest"] = None,
) -> Set[str]:
    """Get the list of modified files in the current git branch.
    If the current branch is master, it will return the list of modified files in the head commit.
    The head commit on master should be the merge commit of the latest merged pull request as we squash commits on merge.
    Pipelines like "publish on merge" are triggered on each new commit on master.

    If a pull_request object is provided, it will use the GitHub API to get the list of modified files.
    This is more reliable for fork PRs because GitHub already knows which files are changed,
    regardless of how far behind the fork is from master.

    If the CI context is a pull request, it will return the list of modified files in the pull request, without using git diff.
    If the current branch is not master, it will return the list of modified files in the current branch.
    This latest case is the one we encounter when running the pipeline locally, on a local branch, or manually on GHA with a workflow dispatch event.
    """
    if ci_context is CIContext.MASTER or (ci_context is CIContext.MANUAL and git_branch == "master"):
        return await get_modified_files_in_commit(git_branch, git_revision, is_local)

    # Use GitHub API to get PR files when available - this is more reliable for fork PRs
    # because it correctly identifies only the files changed in the PR, not files that
    # differ between the fork and master due to the fork being behind.
    if pull_request is not None:
        main_logger.info(f"Using GitHub API to get modified files from PR #{pull_request.number}")
        return get_modified_files_from_pull_request(pull_request)

    return await get_modified_files_in_branch(git_repo_url, git_branch, git_revision, diffed_branch, is_local)
