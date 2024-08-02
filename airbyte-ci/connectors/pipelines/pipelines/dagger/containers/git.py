# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
from typing import Optional

from dagger import Client, Container
from pipelines.helpers.github import AIRBYTE_GITHUB_REPO_URL
from pipelines.helpers.utils import sh_dash_c


def get_authenticated_repo_url(url: str, github_token: str) -> str:
    return url.replace("https://github.com", f"https://{github_token}@github.com")


async def checked_out_git_container(
    dagger_client: Client,
    current_git_branch: str,
    current_git_revision: str,
    diffed_branch: Optional[str] = None,
    repo_url: str = AIRBYTE_GITHUB_REPO_URL,
) -> Container:
    """
    Create a container with git in it.
    We add the airbyte repo as the origin remote and the target repo as the target remote.
    We fetch the diffed branch from the origin remote and the current branch from the target remote.
    We then checkout the current branch.
    """
    origin_repo_url = AIRBYTE_GITHUB_REPO_URL
    current_git_branch = current_git_branch.removeprefix("origin/")
    diffed_branch = current_git_branch if diffed_branch is None else diffed_branch.removeprefix("origin/")
    if github_token := os.environ.get("CI_GITHUB_ACCESS_TOKEN"):
        origin_repo_url = get_authenticated_repo_url(origin_repo_url, github_token)
        target_repo_url = get_authenticated_repo_url(repo_url, github_token)
    origin_repo_url_secret = dagger_client.set_secret("ORIGIN_REPO_URL", origin_repo_url)
    target_repo_url_secret = dagger_client.set_secret("TARGET_REPO_URL", target_repo_url)

    git_container = (
        dagger_client.container()
        .from_("alpine/git:latest")
        .with_workdir("/repo")
        .with_exec(["init"])
        .with_env_variable("CACHEBUSTER", current_git_revision)
        .with_secret_variable("ORIGIN_REPO_URL", origin_repo_url_secret)
        .with_secret_variable("TARGET_REPO_URL", target_repo_url_secret)
        .with_exec(sh_dash_c(["git remote add origin ${ORIGIN_REPO_URL}"]), skip_entrypoint=True)
        .with_exec(sh_dash_c(["git remote add target ${TARGET_REPO_URL}"]), skip_entrypoint=True)
        .with_exec(["fetch", "origin", diffed_branch])
    )
    if diffed_branch != current_git_branch:
        git_container = git_container.with_exec(["fetch", "target", current_git_branch])
    return await git_container.with_exec(["checkout", current_git_branch])
