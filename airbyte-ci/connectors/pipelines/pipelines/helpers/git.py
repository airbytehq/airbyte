#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
from typing import Optional, Set

import git
from dagger import Client, Connection, Container
from pipelines.helpers.utils import AIRBYTE_REPO_URL, DAGGER_CONFIG, DIFF_FILTER


def get_current_git_revision() -> str:  # noqa D103
    return git.Repo(search_parent_directories=True).head.object.hexsha


def get_current_git_branch() -> str:  # noqa D103
    return git.Repo(search_parent_directories=True).active_branch.name


async def get_modified_files_in_branch_remote(
    current_git_branch: str, current_git_revision: str, diffed_branch: str = "origin/master"
) -> Set[str]:
    """Use git diff to spot the modified files on the remote branch."""
    async with Connection(DAGGER_CONFIG) as dagger_client:
        container = await checked_out_git_container(dagger_client, current_git_branch, current_git_revision, diffed_branch)
        modified_files = await container.with_exec(
            ["diff", f"--diff-filter={DIFF_FILTER}", "--name-only", f"{diffed_branch}...{current_git_revision}"]
        ).stdout()
    return set(modified_files.split("\n"))


def get_modified_files_in_branch_local(current_git_revision: str, diffed_branch: str = "master") -> Set[str]:
    """Use git diff and git status to spot the modified files on the local branch."""
    airbyte_repo = git.Repo()
    modified_files = airbyte_repo.git.diff(
        f"--diff-filter={DIFF_FILTER}", "--name-only", f"{diffed_branch}...{current_git_revision}"
    ).split("\n")
    status_output = airbyte_repo.git.status("--porcelain")
    for not_committed_change in status_output.split("\n"):
        file_path = not_committed_change.strip().split(" ")[-1]
        if file_path:
            modified_files.append(file_path)
    return set(modified_files)


async def get_modified_files_in_branch(
    current_git_branch: str, current_git_revision: str, diffed_branch: str, is_local: bool = True
) -> Set[str]:
    """Retrieve the list of modified files on the branch."""
    if is_local:
        return get_modified_files_in_branch_local(current_git_revision, diffed_branch)
    else:
        return await get_modified_files_in_branch_remote(current_git_branch, current_git_revision, diffed_branch)


async def get_modified_files_in_commit_remote(current_git_branch: str, current_git_revision: str) -> Set[str]:
    async with Connection(DAGGER_CONFIG) as dagger_client:
        container = await checked_out_git_container(dagger_client, current_git_branch, current_git_revision)
        modified_files = await container.with_exec(["diff-tree", "--no-commit-id", "--name-only", current_git_revision, "-r"]).stdout()
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


async def get_modified_files_since(current_git_branch: str, current_git_revision: str, since: str, is_local: bool = True) -> Set[str]:
    # TODO: implement
    return await get_modified_files_in_commit(current_git_branch, current_git_revision, is_local)


async def checked_out_git_container(
    dagger_client: Client,
    current_git_branch: str,
    current_git_revision: str,
    diffed_branch: Optional[str] = None,
) -> Container:
    current_git_branch = current_git_branch.removeprefix("origin/")
    diffed_branch = current_git_branch if diffed_branch is None else diffed_branch.removeprefix("origin/")
    return await (
        dagger_client.container()
        .from_("alpine/git:latest")
        .with_workdir("/repo")
        .with_exec(["init"])
        .with_env_variable("CACHEBUSTER", current_git_revision)
        .with_exec(
            [
                "remote",
                "add",
                "--fetch",
                "--track",
                current_git_branch,
                "--track",
                diffed_branch if diffed_branch is not None else current_git_branch,
                "origin",
                AIRBYTE_REPO_URL,
            ]
        )
        .with_exec(["checkout", "-t", f"origin/{current_git_branch}"])
    )


@functools.cache
def get_git_repo() -> git.Repo:
    """Retrieve the git repo."""
    return git.Repo(search_parent_directories=True)


@functools.cache
def get_git_repo_path() -> str:
    """Retrieve the git repo path."""
    return get_git_repo().working_tree_dir
