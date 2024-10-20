#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, PackageLoader, select_autoescape
from pipelines.airbyte_ci.connectors.build_image.steps.python_connectors import BuildConnectorImages
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.airbyte_ci.connectors.reports import ConnectorReport
from pipelines.airbyte_ci.steps.base_image import UpdateBaseImageMetadata
from pipelines.airbyte_ci.steps.bump_version import BumpConnectorVersion
from pipelines.airbyte_ci.steps.changelog import AddChangelogEntry
from pipelines.airbyte_ci.steps.pull_request import CreateOrUpdatePullRequest
from pipelines.consts import LOCAL_BUILD_PLATFORM

from .steps import DependencyUpdate, GetDependencyUpdates, PoetryUpdate

if TYPE_CHECKING:
    from typing import Dict, Iterable, List, Set, Tuple

    from anyio import Semaphore
    from github import PullRequest
    from pipelines.models.steps import StepResult

UP_TO_DATE_PR_LABEL = "up-to-date"
AUTO_MERGE_PR_LABEL = "auto-merge"
DEFAULT_PR_LABELS = [UP_TO_DATE_PR_LABEL]
BUMP_TYPE = "patch"
CHANGELOG_ENTRY_COMMENT = "Update dependencies"


## HELPER FUNCTIONS


def get_pr_body(context: ConnectorContext, step_results: Iterable[StepResult], dependency_updates: Iterable[DependencyUpdate]) -> str:
    env = Environment(
        loader=PackageLoader("pipelines.airbyte_ci.connectors.up_to_date"),
        autoescape=select_autoescape(),
        trim_blocks=False,
        lstrip_blocks=True,
    )
    template = env.get_template("up_to_date_pr_body.md.j2")
    latest_docker_image = f"{context.connector.metadata['dockerRepository']}:latest"
    return template.render(
        connector_technical_name=context.connector.technical_name,
        step_results=step_results,
        dependency_updates=dependency_updates,
        connector_latest_docker_image=latest_docker_image,
    )


def get_pr_creation_arguments(
    modified_files: Iterable[Path],
    context: ConnectorContext,
    step_results: Iterable[StepResult],
    dependency_updates: Iterable[DependencyUpdate],
) -> Tuple[Tuple, Dict]:
    return (modified_files,), {
        "branch_id": f"up-to-date/{context.connector.technical_name}",
        "commit_message": "\n".join(step_result.step.title for step_result in step_results if step_result.success),
        "pr_title": f"🐙 {context.connector.technical_name}: run up-to-date pipeline [{datetime.now(timezone.utc).strftime('%Y-%m-%d')}]",
        "pr_body": get_pr_body(context, step_results, dependency_updates),
    }


## MAIN FUNCTION
async def run_connector_up_to_date_pipeline(
    context: ConnectorContext,
    semaphore: "Semaphore",
    create_pull_request: bool = False,
    auto_merge: bool = False,
    specific_dependencies: List[str] = [],
    bump_connector_version: bool = True,
) -> ConnectorReport:
    async with semaphore:
        async with context:
            step_results: List[StepResult] = []
            all_modified_files: Set[Path] = set()
            created_pr: PullRequest.PullRequest | None = None
            new_version: str | None = None

            connector_directory = await context.get_connector_dir()
            upgrade_base_image_in_metadata = UpdateBaseImageMetadata(context, connector_directory)
            upgrade_base_image_in_metadata_result = await upgrade_base_image_in_metadata.run()
            step_results.append(upgrade_base_image_in_metadata_result)
            if upgrade_base_image_in_metadata_result.success:
                connector_directory = upgrade_base_image_in_metadata_result.output
                exported_modified_files = await upgrade_base_image_in_metadata.export_modified_files(context.connector.code_directory)
                context.logger.info(f"Exported files following the base image upgrade: {exported_modified_files}")
                all_modified_files.update(exported_modified_files)
                connector_directory = upgrade_base_image_in_metadata_result.output

            if context.connector.is_using_poetry:
                # We run the poetry update step after the base image upgrade because the base image upgrade may change the python environment
                poetry_update = PoetryUpdate(context, connector_directory, specific_dependencies=specific_dependencies)
                poetry_update_result = await poetry_update.run()
                step_results.append(poetry_update_result)
                if poetry_update_result.success:
                    exported_modified_files = await poetry_update.export_modified_files(context.connector.code_directory)
                    context.logger.info(f"Exported files following the Poetry update: {exported_modified_files}")
                    all_modified_files.update(exported_modified_files)
                    connector_directory = poetry_update_result.output

            one_previous_step_is_successful = any(step_result.success for step_result in step_results)

            # NOTE:
            # BumpConnectorVersion will already work for manifest-only and Java connectors too
            if bump_connector_version and one_previous_step_is_successful:
                bump_version = BumpConnectorVersion(context, connector_directory, BUMP_TYPE)
                bump_version_result = await bump_version.run()
                step_results.append(bump_version_result)
                if bump_version_result.success:
                    new_version = bump_version.new_version
                    exported_modified_files = await bump_version.export_modified_files(context.connector.code_directory)
                    context.logger.info(f"Exported files following the version bump: {exported_modified_files}")
                    all_modified_files.update(exported_modified_files)

            # Only create the PR if the flag is on, and if there's anything to contribute
            create_pull_request = create_pull_request and one_previous_step_is_successful and bump_version_result.success

            # We run build and get dependency updates only if we are creating a pull request,
            # to fill the PR body with the correct information about what exactly got updated.
            if create_pull_request:
                # Building connector images is also universal across connector technologies.
                build_result = await BuildConnectorImages(context).run()
                step_results.append(build_result)
                dependency_updates: List[DependencyUpdate] = []

                if build_result.success:
                    built_connector_container = build_result.output[LOCAL_BUILD_PLATFORM]

                    # Dependencies here mean Syft deps in the container image itself, not framework-level deps.
                    get_dependency_updates = GetDependencyUpdates(context)
                    dependency_updates_result = await get_dependency_updates.run(built_connector_container)
                    step_results.append(dependency_updates_result)
                    dependency_updates = dependency_updates_result.output

                # We open a PR even if build is failing.
                # This might allow a developer to fix the build in the PR.
                # ---
                # We are skipping CI on this first PR creation attempt to avoid useless runs:
                # the new changelog entry is missing, it will fail QA checks
                initial_pr_creation = CreateOrUpdatePullRequest(context, skip_ci=True, labels=DEFAULT_PR_LABELS)
                pr_creation_args, pr_creation_kwargs = get_pr_creation_arguments(
                    all_modified_files, context, step_results, dependency_updates
                )
                initial_pr_creation_result = await initial_pr_creation.run(*pr_creation_args, **pr_creation_kwargs)
                step_results.append(initial_pr_creation_result)
                if initial_pr_creation_result.success:
                    created_pr = initial_pr_creation_result.output

            if new_version and created_pr:
                documentation_directory = await context.get_repo_dir(
                    include=[str(context.connector.local_connector_documentation_directory)]
                ).directory(str(context.connector.local_connector_documentation_directory))
                add_changelog_entry = AddChangelogEntry(
                    context, documentation_directory, new_version, CHANGELOG_ENTRY_COMMENT, created_pr.number
                )
                add_changelog_entry_result = await add_changelog_entry.run()
                step_results.append(add_changelog_entry_result)
                if add_changelog_entry_result.success:
                    # File path modified by the changelog entry step are relative to the repo root
                    exported_modified_files = await add_changelog_entry.export_modified_files(Path("."))
                    context.logger.info(f"Exported files following the changelog entry: {exported_modified_files}")
                    all_modified_files.update(exported_modified_files)
                    final_labels = DEFAULT_PR_LABELS + [AUTO_MERGE_PR_LABEL] if auto_merge else DEFAULT_PR_LABELS
                    post_changelog_pr_update = CreateOrUpdatePullRequest(context, skip_ci=False, labels=final_labels)
                    pr_creation_args, pr_creation_kwargs = get_pr_creation_arguments(
                        all_modified_files, context, step_results, dependency_updates
                    )
                    post_changelog_pr_update_result = await post_changelog_pr_update.run(*pr_creation_args, **pr_creation_kwargs)
                    step_results.append(post_changelog_pr_update_result)

            report = ConnectorReport(context, step_results, name="UP-TO-DATE RESULTS")
            context.report = report
    return report
