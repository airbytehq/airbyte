# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from github.PullRequest import PullRequest


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
