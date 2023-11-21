#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set

import click
import dagger
import git
from github import PullRequest
from pipelines.helpers.utils import AIRBYTE_REPO_URL, DIFF_FILTER


def check_local_repo_is_airbyte(repo: git.Repo) -> bool:
    """Get the airbyte git repo from the current working directory"""
    for remote in repo.remotes:
        remote_url = remote.config_reader.get("url")
        if os.path.splitext(os.path.basename(remote_url))[0] == "airbyte":
            return True
    return False


async def check_remote_repo_is_airbyte(git_container_with_remote_repo: dagger.Container) -> bool:
    "/airbyte.git" in (await git_container_with_remote_repo.with_exec(["remote", "-v", "airbyte", AIRBYTE_REPO_URL]).stdout())


def get_modified_files_in_local_repo(repo: git.Repo, diffed_git_ref: str) -> Set[str]:
    """Use git diff and git status to spot the modified files on the local branch."""
    head_sha = repo.head.object.hexsha

    modified_files = repo.git.diff(f"--diff-filter={DIFF_FILTER}", "--name-only", f"{diffed_git_ref}...{head_sha}")
    if modified_files:
        modified_files = modified_files.split("\n")
    else:
        modified_files = []
    status_output = repo.git.status("--porcelain")
    for not_committed_change in status_output.split("\n"):
        file_path = not_committed_change.strip().split(" ")[-1]
        if file_path:
            modified_files.append(file_path)
    return set(modified_files)


def get_git_container_with_repo(dagger_client: dagger.Client, repo_dir: dagger.Directory):
    return dagger_client.container().from_("alpine/git:latest").with_workdir("/repo").with_mounted_directory("/repo", repo_dir)


async def get_modified_files_in_remote_repo(git_container_with_remote_repo: dagger.Container, diffed_git_ref: str) -> Set[str]:
    git_container_with_diffed_ref = git_container_with_remote_repo.with_exec(
        [
            "fetch",
            "origin",
            diffed_git_ref,
        ]
    )
    git_ref_has_commit_hash = re.match(r"^[0-9a-fA-F]{40}$", diffed_git_ref.split(":")[0]) is not None

    if not git_ref_has_commit_hash:
        logging.info(f"{diffed_git_ref} is a branch name, use rev-parse to get the latest commit hash in the branch")
        compare_to = (await git_container_with_diffed_ref.with_exec(["rev-parse", f"origin/{diffed_git_ref}"]).stdout()).strip()
    else:
        compare_to = diffed_git_ref.split(":")[0]

    modified_files = await (
        git_container_with_diffed_ref.with_exec(["diff", f"--diff-filter={DIFF_FILTER}", "--name-only", compare_to, "HEAD"]).stdout()
    )
    return set(modified_files.split("\n"))


def get_modified_files_in_pull_request(pull_request: PullRequest) -> List[str]:
    """Retrieve the list of modified files in a pull request."""
    return [f.filename for f in pull_request.get_files()]


def get_airbyte_ci_ignore(local_repo: Optional[git.Repo]) -> List[str]:
    if local_repo:
        airbyte_ci_ignore_path = Path(local_repo.working_tree_dir, ".airbyte_ci_ignore")
        if airbyte_ci_ignore_path.exists():
            return airbyte_ci_ignore_path.read_text().splitlines()
    return []


@dataclass
class TargetRepoState:
    modified_files: List[str]
    repo_dir: dagger.Directory
    is_remote_repository: bool
    head_sha: str
    diffed_git_ref: str
    is_airbyte_repo: bool

    @property
    def is_local_repository(self) -> bool:
        return not self.is_remote_repository


async def get_airbyte_repo_dir(dagger_client: dagger.Client) -> dagger.Directory:
    return dagger_client.git("https://github.com/airbytehq/airbyte.git", keep_git_dir=False).branch("master").tree()


async def get_target_repo_state(dagger_client: dagger.Client, ctx: click.Context):
    target_repo = ctx.obj["target_repo"]
    diffed_git_ref = ctx.obj["diffed_git_ref"]
    remote_repo_url = target_repo if target_repo.startswith("http") else None
    is_remote_repo = remote_repo_url is not None

    if is_remote_repo:
        logging.info(f"Target repo is a remote repo, using {remote_repo_url}")
        branch = ctx.obj["git_branch"]
        commit = ctx.obj["git_revision"]
        target_repo_state = await get_remote_repo_state(dagger_client, remote_repo_url, commit, branch, diffed_git_ref)
    else:
        local_repo = get_local_repo(target_repo)
        logging.info(f"Target repo is a local repo, using {local_repo.working_tree_dir}")
        target_repo_state = get_local_repo_state(dagger_client, local_repo, diffed_git_ref)
    return target_repo_state


def get_local_repo(target_repo: str):
    try:
        return git.Repo(Path(target_repo).resolve(), search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        raise click.UsageError(f"The targeted repository {target_repo} is not a git repository.")


async def get_remote_repo_state(dagger_client, remote_repo_url, commit, branch, diffed_git_ref):
    remote_git_repo = dagger_client.git(remote_repo_url, keep_git_dir=True)
    if commit:
        remote_repo_dir = remote_git_repo.commit(commit).tree()
    else:
        remote_repo_dir = remote_git_repo.branch(branch).tree()

    git_container_with_remote_repo = get_git_container_with_repo(dagger_client, remote_repo_dir)
    remote_repo_is_airbyte = check_remote_repo_is_airbyte(git_container_with_remote_repo)
    head_sha = await git_container_with_remote_repo.with_exec(["rev-parse", "HEAD"]).stdout()
    modified_files = await get_modified_files_in_remote_repo(git_container_with_remote_repo, diffed_git_ref)
    return TargetRepoState(modified_files, remote_repo_dir, True, head_sha, diffed_git_ref, remote_repo_is_airbyte)


def get_local_repo_state(dagger_client, local_repo, diffed_git_ref):
    local_repo_is_airbyte_repo = check_local_repo_is_airbyte(local_repo)
    airbyte_ci_ignore = get_airbyte_ci_ignore(local_repo)
    local_repo_dir = dagger_client.host().directory(local_repo.working_tree_dir, exclude=airbyte_ci_ignore)
    modified_files = get_modified_files_in_local_repo(local_repo, diffed_git_ref)

    return TargetRepoState(modified_files, local_repo_dir, False, local_repo.head.object.hexsha, diffed_git_ref, local_repo_is_airbyte_repo)
