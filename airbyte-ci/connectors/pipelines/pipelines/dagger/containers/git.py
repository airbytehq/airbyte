# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

from dagger import Client, Container
from pipelines.helpers.utils import AIRBYTE_REPO_URL


async def checked_out_git_container(
    dagger_client: Client,
    current_git_branch: str,
    current_git_revision: str,
    diffed_branch: Optional[str] = None,
    repo_url: str = AIRBYTE_REPO_URL,
) -> Container:
    """
    Create a container with git in it.
    We add the airbyte repo as the origin remote and the target repo as the target remote.
    We fetch the diffed branch from the origin remote and the current branch from the target remote.
    We then checkout the current branch.
    """
    current_git_branch = current_git_branch.removeprefix("origin/")
    diffed_branch = current_git_branch if diffed_branch is None else diffed_branch.removeprefix("origin/")
    git_container = (
        dagger_client.container()
        .from_("alpine/git:latest")
        .with_workdir("/repo")
        .with_exec(["init"])
        .with_env_variable("CACHEBUSTER", current_git_revision)
        .with_exec(
            [
                "remote",
                "add",
                "origin",
                AIRBYTE_REPO_URL,
            ]
        )
        .with_exec(
            [
                "remote",
                "add",
                "target",
                repo_url,
            ]
        )
        .with_exec(["fetch", "origin", diffed_branch])
    )
    if diffed_branch != current_git_branch:
        git_container = git_container.with_exec(["fetch", "target", current_git_branch])
    return await git_container.with_exec(["checkout", current_git_branch])
