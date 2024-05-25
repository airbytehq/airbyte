#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import base64
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List, Set

from github import Auth, Github, GithubException, InputGitTreeElement, UnknownObjectException
from pipelines import main_logger
from pipelines.airbyte_ci.connectors.bump_version.pipeline import (
    AddChangelogEntry,
    RestoreVersionState,
    SetConnectorVersion,
    get_bumped_version,
)
from pipelines.airbyte_ci.connectors.consts import CONNECTOR_TEST_STEP_ID
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import Report
from pipelines.consts import LOCAL_BUILD_PLATFORM, CIContext
from pipelines.helpers.connectors.command import run_connector_steps
from pipelines.helpers.execution.run_steps import STEP_TREE, StepToRun
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths
from pipelines.models.steps import Step, StepResult, StepStatus

if TYPE_CHECKING:
    from anyio import Semaphore


class RestorePullRequestState(Step):
    context: ConnectorContext

    title = "Restore original state"

    def __init__(self, context: ConnectorContext) -> None:
        super().__init__(context)
        self.bump_state = RestoreVersionState(context)

    async def _run(self) -> StepResult:
        result = await self.bump_state.run()
        if result.status is not StepStatus.SUCCESS:
            return result
        return StepResult(step=self, status=StepStatus.SUCCESS)

    async def _cleanup(self) -> StepResult:
        result = await self.bump_state._cleanup()
        if result.status is not StepStatus.SUCCESS:
            return result
        return StepResult(step=self, status=StepStatus.SUCCESS)


PULL_REQUEST_OUTPUT_ID = "pull_request_number"


class CreatePullRequest(Step):
    context: ConnectorContext
    message: str
    branch_id: str
    write: bool
    input_title: str | None
    input_body: str | None
    changelog: bool
    bump: str | None

    title = "Create a pull request of changed files."

    def __init__(
        self,
        context: ConnectorContext,
        message: str,
        branch_id: str | None,
        input_title: str | None,
        input_body: str | None,
        dry_run: bool,
    ) -> None:
        super().__init__(context)
        self.message = message
        self.branch_id = branch_id or default_branch_details(message)  # makes branch like: {branch_id}/{connector_name}
        self.input_title = input_title
        self.input_body = input_body
        self.write = not dry_run

    async def _run(self) -> StepResult:

        connector_files = await get_connector_changes(self.context)
        if len(connector_files) == 0:
            return StepResult(step=self, status=StepStatus.SKIPPED, stderr="No files modified in this connector.")

        pull_request_number = await create_github_pull_request(
            write=self.write,
            context=self.context,
            file_paths=connector_files,
            branch_id=self.branch_id,
            message=self.message,
            input_title=self.input_title,
            input_body=self.input_body,
        )

        return StepResult(step=self, status=StepStatus.SUCCESS, output={PULL_REQUEST_OUTPUT_ID: pull_request_number})


async def get_connector_changes(context: ConnectorContext) -> Set[Path]:
    logger = main_logger
    all_modified_files = set(
        transform_strs_to_paths(
            await get_modified_files(
                context.git_branch,
                context.git_revision,
                context.diffed_branch,
                context.is_local,
                CIContext(context.ci_context),
                context.git_repo_url,
            )
        )
    )

    directory = context.connector.code_directory
    logger.info(f"    Filtering to changes in {directory}")
    # get a list of files that are a child of this path
    connector_files = set([file for file in all_modified_files if directory in file.parents])
    # get doc too
    doc_path = context.connector.documentation_file_path

    if doc_path in all_modified_files:
        connector_files.add(doc_path)

    return connector_files


def default_branch_details(message: str) -> str:
    transformed = re.sub(r"\W", "-", message.lower())
    truncated = transformed[:20]
    data_bytes = message.encode()
    hash_object = hashlib.sha256(data_bytes)
    desc = f"{truncated}-{hash_object.hexdigest()[:6]}"
    return desc


@dataclass
class ChangedFile:
    path: str
    sha: str | None


# outputs a pull request number
async def create_github_pull_request(
    write: bool,
    context: ConnectorContext,
    file_paths: set[Path],
    branch_id: str,
    message: str,
    input_title: str | None,
    input_body: str | None,
) -> int:
    if not context.ci_github_access_token:
        raise Exception("GitHub access token is required to create a pull request. Set the CI_GITHUB_ACCESS_TOKEN environment variable.")

    g = Github(auth=Auth.Token(context.ci_github_access_token.value))
    connector = context.connector
    connector_full_name = connector.technical_name
    logger = main_logger

    if input_title:
        input_title = f"{connector_full_name}: {input_title}"

    REPO_NAME = "airbytehq/airbyte"
    BASE_BRANCH = "master"
    new_branch_name = f"{branch_id}/{connector_full_name}"
    logger.info(f"    Creating pull request: {new_branch_name}")
    logger.info(f"       branch: {new_branch_name}")

    # Get the repository
    repo = g.get_repo(REPO_NAME)

    # TODO: I'm relatively sure there is a gap here when the branch already exists.
    # The files being passed in are the ones that are different than master
    # if a branch already exists that had added a file that was not in master (or was reerted to exactly master contents)
    # _and_ the new code no longer has it (so it was commited and then removed again),
    # it will not be removed from the tree becuse it as not in the original list.
    #
    # What we would have to do is one of the following:
    #   1. Don't have this global list. Each of these connectors looks for the existing branch and uses the files that
    #           are different than that branch to this list to see if they have since been modified or deleted.
    #   2. Have this force push on top of the current master branch so that the history is not relevant.
    # I generally lean towards the second option because it's more predictable and less error prone, but there
    # would be less commits in in the PR which could be a feature in some cases.

    # Read the content of each file and create blobs
    changed_files: List[ChangedFile] = []
    for sub_path in file_paths:  # these are relative to the repo root
        logger.info(f"          {sub_path}")
        if sub_path.exists():
            with open(sub_path, "rb") as file:
                logger.info(f"          Reading file: {sub_path}")
                content = base64.b64encode(file.read()).decode("utf-8")  # Encode file content to base64
                blob = repo.create_git_blob(content, "base64")
                changed_file = ChangedFile(path=str(sub_path), sha=blob.sha)
        else:
            # it's deleted
            logger.info(f"          Deleted file: {sub_path}")
            changed_file = ChangedFile(path=str(sub_path), sha=None)
        changed_files.append(changed_file)

    existing_ref = None
    try:
        existing_ref = repo.get_git_ref(f"heads/{new_branch_name}")
        logger.info(f"          Existing git ref {new_branch_name}")
    except GithubException:
        pass

    if existing_ref:
        base_sha = existing_ref.object.sha
    else:
        base_sha = repo.get_branch(BASE_BRANCH).commit.sha
        if write:
            repo.create_git_ref(f"refs/heads/{new_branch_name}", base_sha)

    # remove from the tree if we are deleting something that's not there
    parent_commit = repo.get_git_commit(base_sha)
    parent_tree = repo.get_git_tree(base_sha)

    # Filter and update tree elements
    tree_elements: List[InputGitTreeElement] = []
    for changed_file in changed_files:
        if changed_file.sha is None:
            # make sure it's actually in the current tree
            try:
                # Attempt to get the file from the specified commit
                repo.get_contents(changed_file.path, ref=base_sha)
                # logger.info(f"File {changed_file.path} exists in commit {base_sha}")
            except UnknownObjectException:
                # don't need to add it to the tree
                logger.info(f"        {changed_file.path} not in parent: {base_sha}")
                continue

        # Update or new file addition or needed deletion
        tree_elements.append(
            InputGitTreeElement(
                path=changed_file.path,
                mode="100644",
                type="blob",
                sha=changed_file.sha,
            )
        )

    # Create a new commit pointing to that tree
    if write:
        tree = repo.create_git_tree(tree_elements, base_tree=parent_tree)
        commit = repo.create_git_commit(message, tree, [parent_commit])
        repo.get_git_ref(f"heads/{new_branch_name}").edit(sha=commit.sha)

    # Check if there's an existing pull request
    found_pr = None
    open_pulls = repo.get_pulls(state="open", base="master")
    for pr in open_pulls:
        if pr.head.ref == new_branch_name:
            found_pr = pr
            logger.info(f"        Pull request already exists: {pr.html_url}")

    if found_pr:
        pull_request_number = found_pr.number
        if input_title and input_body:
            logger.info("          Updating title and body")
            if write:
                found_pr.edit(title=input_title, body=input_body)
        elif input_title:
            logger.info("          Updating title")
            if write:
                found_pr.edit(title=input_title)
        elif input_body:
            logger.info("          Updating body")
            if write:
                found_pr.edit(body=input_body)
    else:
        # Create a pull request if it's a new branch
        if not write:
            pull_request_number = 0
        else:
            pull_request_title = input_title or f"{connector_full_name}: {message}"
            pull_request_body = input_body or ""
            pull_request = repo.create_pull(
                title=pull_request_title,
                body=pull_request_body,
                base=BASE_BRANCH,
                head=new_branch_name,
            )

            # TODO: could pass in additional labels
            label = repo.get_label("autopull")
            pull_request.add_to_labels(label)
            logger.info(f"        Created pull request: {pull_request.html_url}")
            pull_request_number = pull_request.number

    return pull_request_number


async def run_connector_pull_request_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    message: str,
    branch_id: str,
    title: str | None,
    body: str | None,
    changelog: bool,
    bump: str | None,
    dry_run: bool,
) -> Report:
    restore_original_state = RestorePullRequestState(context)

    context.targeted_platforms = [LOCAL_BUILD_PLATFORM]

    connector_version: str | None = context.connector.version

    steps_to_run: STEP_TREE = []

    steps_to_run.append(
        [
            StepToRun(
                id=CONNECTOR_TEST_STEP_ID.PULL_REQUEST_CREATE,
                step=CreatePullRequest(
                    context=context,
                    message=message,
                    branch_id=branch_id,
                    input_title=title,
                    input_body=body,
                    dry_run=dry_run,
                ),
                depends_on=[],
            )
        ]
    )

    update_step_ids: List[str] = []
    if bump:
        # we are only bumping if there are changes, though
        connector_version = get_bumped_version(connector_version, bump)
        update_step_ids.append(CONNECTOR_TEST_STEP_ID.SET_CONNECTOR_VERSION)
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.SET_CONNECTOR_VERSION,
                    step=SetConnectorVersion(context, connector_version),
                    depends_on=[CONNECTOR_TEST_STEP_ID.PULL_REQUEST_CREATE],
                )
            ]
        )

    if changelog:
        if not connector_version:
            raise Exception("Connector version is required to add a changelog entry.")
        if not context.connector.documentation_file_path:
            raise Exception("Connector documentation file path is required to add a changelog entry.")
        update_step_ids.append(CONNECTOR_TEST_STEP_ID.ADD_CHANGELOG_ENTRY)
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.ADD_CHANGELOG_ENTRY,
                    step=AddChangelogEntry(
                        context,
                        connector_version,
                        message,
                        "0",  # overridden in the step via args
                    ),
                    depends_on=[CONNECTOR_TEST_STEP_ID.PULL_REQUEST_CREATE],
                    args=lambda results: {
                        "pull_request_number": results[CONNECTOR_TEST_STEP_ID.PULL_REQUEST_CREATE].output[PULL_REQUEST_OUTPUT_ID],
                    },
                )
            ]
        )

    if update_step_ids:
        # make a pull request with the changelog entry
        steps_to_run.append(
            [
                StepToRun(
                    id=CONNECTOR_TEST_STEP_ID.PULL_REQUEST_UPDATE,
                    step=CreatePullRequest(
                        context=context,
                        message=message,
                        branch_id=branch_id,
                        input_title=title,
                        input_body=body,
                        dry_run=dry_run,
                    ),
                    depends_on=update_step_ids,
                )
            ]
        )

    return await run_connector_steps(context, semaphore, steps_to_run, restore_original_state=restore_original_state)
