#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Set

from pipelines import main_logger
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport, Report
from pipelines.airbyte_ci.steps.pull_request import CreateOrUpdatePullRequest
from pipelines.consts import CIContext
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths

if TYPE_CHECKING:
    from anyio import Semaphore


## HELPER FUNCTIONS
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
    logger.info(f"Filtering to changes in {directory}")
    # get a list of files that are a child of this path
    connector_files = set([file for file in all_modified_files if directory in file.parents])
    # get doc too
    doc_path = context.connector.documentation_file_path

    if doc_path in all_modified_files:
        connector_files.add(doc_path)

    return connector_files


def replace_placeholder_with_pr_number(context: ConnectorContext, pr_number: int) -> Set[Path]:
    current_doc = context.connector.documentation_file_path.read_text()
    updated_doc = current_doc.replace("*PR_NUMBER_PLACEHOLDER*", str(pr_number))
    context.connector.documentation_file_path.write_text(updated_doc)
    return {context.connector.documentation_file_path}


async def run_connector_pull_request_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    message: str,
    branch_id: str,
    title: str | None = None,
    body: str | None = None,
) -> Report | ConnectorReport | None:
    title = title or message
    body = body or ""
    async with semaphore:
        async with context:
            step_results = []
            modified_files = await get_connector_changes(context)

            create_or_update_pull_request = CreateOrUpdatePullRequest(context, skip_ci=True)

            if not modified_files:
                step_results.append(create_or_update_pull_request.skip("No changes detected in the connector directory."))
                context.report = ConnectorReport(context, step_results, name="PULL REQUEST")
                return context.report

            create_or_update_pull_request_result = await create_or_update_pull_request.run(
                modified_files,
                branch_id,
                message,
                title,
                body,
            )
            step_results.append(create_or_update_pull_request_result)

            if not create_or_update_pull_request_result.success:
                return ConnectorReport(
                    context,
                    step_results,
                    name="PULL REQUEST",
                )

            created_pr = create_or_update_pull_request_result.output
            modified_files.update(replace_placeholder_with_pr_number(context, created_pr.number))
            update_pull_request = CreateOrUpdatePullRequest(context, skip_ci=False)
            update_pull_request_result = await update_pull_request.run(
                modified_files,
                branch_id,
                message,
                title,
                body,
            )
            step_results.append(update_pull_request_result)

            context.report = ConnectorReport(context, step_results, name="PULL REQUEST")
    return context.report
