#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

from typing import TYPE_CHECKING

import asyncclick as click
import asyncer
from pipelines.airbyte_ci.test import INTERNAL_POETRY_PACKAGES, INTERNAL_POETRY_PACKAGES_PATH, pipeline
from pipelines.cli.click_decorators import click_ci_requirements_option, click_ignore_unused_kwargs, click_merge_args_into_context_obj
from pipelines.helpers.git import get_modified_files
from pipelines.helpers.utils import transform_strs_to_paths
from pipelines.models.contexts.click_pipeline_context import ClickPipelineContext, pass_pipeline_context
from pipelines.models.steps import StepStatus

if TYPE_CHECKING:
    from pathlib import Path
    from typing import List, Set, Tuple


async def find_modified_internal_packages(pipeline_context: ClickPipelineContext) -> Set[Path]:
    """Finds the modified internal packages according to the modified files on the branch/commit.

    Args:
        pipeline_context (ClickPipelineContext): The context object.

    Returns:
        Set[Path]: The set of modified internal packages.
    """
    modified_files = transform_strs_to_paths(
        await get_modified_files(
            pipeline_context.params["git_branch"],
            pipeline_context.params["git_revision"],
            pipeline_context.params["diffed_branch"],
            pipeline_context.params["is_local"],
            pipeline_context.params["ci_context"],
            git_repo_url=pipeline_context.params["git_repo_url"],
        )
    )
    modified_packages = set()
    for modified_file in modified_files:
        for internal_package in INTERNAL_POETRY_PACKAGES_PATH:
            if modified_file.is_relative_to(internal_package):
                modified_packages.add(internal_package)
    return modified_packages


async def get_packages_to_run(pipeline_context: ClickPipelineContext) -> Set[Path]:
    """Gets the packages to run the poe tasks on.

    Args:
        pipeline_context (ClickPipelineContext): The context object.

    Raises:
        click.ClickException: If no packages are specified to run the poe tasks on.

    Returns:
        Set[Path]: The set of packages to run the poe tasks on.
    """
    if not pipeline_context.params["poetry_package_paths"] and not pipeline_context.params["modified"]:
        raise click.ClickException("You must specify at least one package to test.")

    poetry_package_paths = set()
    if pipeline_context.params["modified"]:
        poetry_package_paths = await find_modified_internal_packages(pipeline_context)

    return poetry_package_paths.union(set(pipeline_context.params["poetry_package_paths"]))


def crash_on_any_failure(poetry_package_poe_tasks_results: List[Tuple[Path, asyncer.SoonValue]]) -> None:
    """Fail the command if any of the poe tasks failed.

    Args:
        poetry_package_poe_tasks_results (List[Tuple[Path, asyncer.SoonValue]]): The results of the poe tasks.

    Raises:
        click.ClickException: If any of the poe tasks failed.
    """
    failed_packages = set()
    for poetry_package_paths, package_result in poetry_package_poe_tasks_results:
        poe_command_results = package_result.value
        if any([result.status is StepStatus.FAILURE for result in poe_command_results]):
            failed_packages.add(poetry_package_paths)
    if failed_packages:
        raise click.ClickException(
            f"The following packages failed to run poe tasks:  {', '.join([str(package_path) for package_path in failed_packages])}"
        )
    return None


@click.command()
@click.option("--modified", default=False, is_flag=True, help="Run on modified internal packages.")
@click.option(
    "--poetry-package-path",
    "-p",
    "poetry_package_paths",
    help="The path to the poetry package to test.",
    type=click.Choice(INTERNAL_POETRY_PACKAGES),
    multiple=True,
)
@click_ci_requirements_option()
@click_merge_args_into_context_obj
@pass_pipeline_context
@click_ignore_unused_kwargs
# TODO this command should be renamed ci and go under the poetry command group
# e.g. airbyte-ci poetry ci --poetry-package-path airbyte-ci/connectors/pipelines
async def test(pipeline_context: ClickPipelineContext) -> None:
    """Runs the tests for the given airbyte-ci package

    Args:
        pipeline_context (ClickPipelineContext): The context object.
    """
    poetry_package_paths = await get_packages_to_run(pipeline_context)
    click.echo(f"Running poe tasks of the following packages: {', '.join([str(package_path) for package_path in poetry_package_paths])}")
    dagger_client = await pipeline_context.get_dagger_client()

    poetry_package_poe_tasks_results: List[Tuple[Path, asyncer.SoonValue]] = []
    async with asyncer.create_task_group() as poetry_packages_task_group:
        for poetry_package_path in poetry_package_paths:
            poetry_package_poe_tasks_results.append(
                (
                    poetry_package_path,
                    poetry_packages_task_group.soonify(pipeline.run_poe_tasks_for_package)(
                        dagger_client, poetry_package_path, pipeline_context.params
                    ),
                )
            )

    crash_on_any_failure(poetry_package_poe_tasks_results)
