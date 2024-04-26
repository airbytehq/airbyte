# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

from dagger import Client, Container
from pipelines.helpers.utils import AIRBYTE_REPO_URL


async def checked_out_git_container(
    dagger_client: Client,
    current_git_branch: str,
    current_git_revision: str,
    diffed_branch: Optional[str] = None,
) -> Container:
    """Builds git-based container with the current branch checked out."""
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
