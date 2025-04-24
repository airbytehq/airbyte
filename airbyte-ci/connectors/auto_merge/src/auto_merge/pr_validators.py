# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Tuple

from .consts import AUTO_MERGE_BYPASS_CI_CHECKS_LABEL, AUTO_MERGE_LABEL, BASE_BRANCH, CONNECTOR_PATH_PREFIXES

if TYPE_CHECKING:
    from github.Commit import Commit as GithubCommit
    from github.PullRequest import PullRequest


def has_auto_merge_label(head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]) -> Tuple[bool, Optional[str]]:
    has_auto_merge_label = any(label.name == AUTO_MERGE_LABEL for label in pr.labels)
    if not has_auto_merge_label:
        return False, f"does not have the {AUTO_MERGE_LABEL} label"
    return True, None


def has_auto_merge_bypass_ci_checks_label(
    head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]
) -> Tuple[bool, Optional[str]]:
    has_auto_merge_bypass_ci_checks_label = any(label.name == AUTO_MERGE_BYPASS_CI_CHECKS_LABEL for label in pr.labels)
    if not has_auto_merge_bypass_ci_checks_label:
        return False, f"does not have the {AUTO_MERGE_BYPASS_CI_CHECKS_LABEL} label"
    return True, None


def targets_main_branch(head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]) -> Tuple[bool, Optional[str]]:
    if not pr.base.ref == BASE_BRANCH:
        return False, f"does not target {BASE_BRANCH}"
    return True, None


def only_modifies_connectors(head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]) -> Tuple[bool, Optional[str]]:
    modified_files = pr.get_files()
    for file in modified_files:
        if not any(file.filename.startswith(prefix) for prefix in CONNECTOR_PATH_PREFIXES):
            return False, "is not only modifying connectors"
    return True, None


def head_commit_passes_all_required_checks(
    head_commit: GithubCommit, pr: PullRequest, required_checks: set[str]
) -> Tuple[bool, Optional[str]]:
    successful_status_contexts = [commit_status.context for commit_status in head_commit.get_statuses() if commit_status.state == "success"]
    successful_check_runs = [
        check_run.name
        for check_run in head_commit.get_check_runs()
        # Github considers a required check as passing if it has a conclusion of "success" or "skipped"
        if check_run.conclusion == "success" or check_run.conclusion == "skipped"
    ]
    successful_contexts = set(successful_status_contexts + successful_check_runs)
    if not required_checks.issubset(successful_contexts):
        return False, "not all required checks passed"
    return True, None


# A PR is considered auto-mergeable if:
#     - it has the AUTO_MERGE_LABEL
#     - it targets the BASE_BRANCH
#     - it touches only files in CONNECTOR_PATH_PREFIXES
#     - the head commit passes all required checks

# PLEASE BE CAREFUL OF THE VALIDATOR ORDERING
# Let's declare faster checks first as the check_if_pr_is_auto_mergeable function fails fast.
COMMON_VALIDATORS = {
    targets_main_branch,
    only_modifies_connectors,
}
# Let's declare faster checks first as the check_if_pr_is_auto_mergeable function fails fast.
VALIDATOR_MAPPING: dict[str, set[Callable]] = {
    AUTO_MERGE_LABEL: COMMON_VALIDATORS | {has_auto_merge_label, head_commit_passes_all_required_checks},
    AUTO_MERGE_BYPASS_CI_CHECKS_LABEL: COMMON_VALIDATORS | {has_auto_merge_bypass_ci_checks_label},
}
