#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from ci_connector_ops.utils import console

if TYPE_CHECKING:
    from logging import Logger

from github import Github

AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


def update_commit_status_check(
    sha: str, state: str, target_url: str, description: str, context: str, should_send=True, logger: Logger = None
):
    if not should_send:
        return

    try:
        github_client = Github(os.environ["CI_GITHUB_ACCESS_TOKEN"])
        airbyte_repo = github_client.get_repo(AIRBYTE_GITHUB_REPO)
    except Exception as e:
        if logger:
            logger.error("No commit status check sent, the connection to Github API failed", exc_info=True)
        else:
            console.print(e)
        return

    airbyte_repo.get_commit(sha=sha).create_status(
        state=state,
        target_url=target_url,
        description=description,
        context=context,
    )
    logger.info(f"Created {state} status for commit {sha} on Github in {context} context.")
