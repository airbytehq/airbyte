#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import anyio
import asyncer
import dagger
import itertools
import json
import logging
import os

from anyio import Path
from asyncer import asyncify
from dagger import Directory
from dataclasses import dataclass
from rich.console import Group
from rich.logging import RichHandler
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from types import TracebackType
from typing import List, Optional
from typing import Optional

from ci_connector_ops.pipelines import checks, tests
from ci_connector_ops.pipelines.actions import remote_storage, secrets
from ci_connector_ops.pipelines.bases import PipelineContext, TestReport, ContextState
from ci_connector_ops.pipelines.github import update_commit_status_check
from ci_connector_ops.pipelines.utils import DAGGER_CONFIG
from ci_connector_ops.utils import Connector, console


logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s", datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger(__name__)

class ConnectorTestContext(PipelineContext):
    """The connector test context is used to store configuration for a specific connector pipeline run."""

    DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE = "airbyte/connector-acceptance-test:latest"

    def __init__(
        self,
        connector: Connector,
        is_local: bool,
        git_branch: bool,
        git_revision: bool,
        use_remote_secrets: bool = True,
        connector_acceptance_test_image: Optional[str] = DEFAULT_CONNECTOR_ACCEPTANCE_TEST_IMAGE,
        gha_workflow_run_url: Optional[str] = None,
        pipeline_start_timestamp: Optional[int] = None,
        ci_context: Optional[str] = None,
    ):
        pipeline_name = f"CI test for {connector.technical_name}"

        self.connector = connector
        self.use_remote_secrets = use_remote_secrets
        self.connector_acceptance_test_image = connector_acceptance_test_image

        self._secrets_dir = None
        self._updated_secrets_dir = None

        super().__init__(
            pipeline_name=pipeline_name,
            is_local=is_local,
            git_branch=git_branch,
            git_revision=git_revision,
            gha_workflow_run_url=gha_workflow_run_url,
            pipeline_start_timestamp=pipeline_start_timestamp,
            ci_context=ci_context,
        )

    @property
    def secrets_dir(self) -> Directory:
        return self._secrets_dir

    @secrets_dir.setter
    def secrets_dir(self, secrets_dir: Directory):
        self._secrets_dir = secrets_dir

    @property
    def updated_secrets_dir(self) -> Directory:
        return self._updated_secrets_dir

    @updated_secrets_dir.setter
    def updated_secrets_dir(self, updated_secrets_dir: Directory):
        self._updated_secrets_dir = updated_secrets_dir

    @property
    def connector_acceptance_test_source_dir(self) -> Directory:
        return self.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")

    @property
    def should_save_updated_secrets(self):
        return self.use_remote_secrets and self.updated_secrets_dir is not None


    def get_connector_dir(self, exclude=None, include=None) -> Directory:
        return self.get_repo_dir(str(self.connector.code_directory), exclude=exclude, include=include)

    async def __aexit__(
        self, exception_type: Optional[type[BaseException]], exception_value: Optional[BaseException], traceback: Optional[TracebackType]
    ) -> bool:
        """Performs teardown operation for the ConnectorTestContext.
        On the context exit the following operations will happen:
            - Upload updated connector secrets back to Google Secret Manager
            - Write a test report in JSON format locally and to S3 if running in a CI environment
            - Update the commit status check on GitHub if running in a CI environment.
        It should gracefully handle the execution error that happens and always upload a test report and update commit status check.
        Args:
            exception_type (Optional[type[BaseException]]): The exception type if an exception was raised in the context execution, None otherwise.
            exception_value (Optional[BaseException]): The exception value if an exception was raised in the context execution, None otherwise.
            traceback (Optional[TracebackType]): The traceback if an exception was raised in the context execution, None otherwise.
        Returns:
            bool: Wether the teardown operation ran successfully.
        """
        print("EXITTIMEBABY")
        if exception_value:
            self.logger.error("An error got handled by the ConnectorTestContext", exc_info=True)
            self.state = ContextState.ERROR

        if self.test_report is None:
            self.logger.error("No test report was provided. This is probably due to an upstream error")
            self.state = ContextState.ERROR
            self.test_report = ConnectorTestReport(self, [])

        self.dagger_client = self.dagger_client.pipeline(f"Teardown {self.connector.technical_name}")
        if self.should_save_updated_secrets:
            await secrets.upload(self)

        self.test_report.print()
        self.logger.info(self.test_report.to_json())

        local_test_reports_path_root = "tools/ci_connector_ops/test_reports/"
        connector_name = self.test_report.pipeline_context.connector.technical_name
        connector_version = self.test_report.pipeline_context.connector.version
        git_revision = self.test_report.pipeline_context.git_revision
        git_branch = self.test_report.pipeline_context.git_branch.replace("/", "_")
        suffix = f"{connector_name}/{git_branch}/{connector_version}/{git_revision}.json"
        local_report_path = Path(local_test_reports_path_root + suffix)
        await local_report_path.parents[0].mkdir(parents=True, exist_ok=True)
        await local_report_path.write_text(self.test_report.to_json())
        if self.test_report.should_be_saved:
            s3_reports_path_root = "python-poc/tests/history/"
            s3_key = s3_reports_path_root + suffix
            report_upload_exit_code = await remote_storage.upload_to_s3(
                self.dagger_client, str(local_report_path), s3_key, os.environ["TEST_REPORTS_BUCKET_NAME"]
            )
            if report_upload_exit_code != 0:
                self.logger.error("Uploading the report to S3 failed.")
        await asyncify(update_commit_status_check)(**self.github_commit_status)

        # Supress the exception if any
        return True

@dataclass(frozen=True)
class ConnectorTestReport(TestReport):
    @property
    def should_be_saved(self) -> bool:
        return self.pipeline_context.is_ci

    def to_json(self) -> str:
        return json.dumps(
            {
                "connector_technical_name": self.pipeline_context.connector.technical_name,
                "connector_version": self.pipeline_context.connector.version,
                "run_timestamp": self.created_at.isoformat(),
                "run_duration": self.run_duration,
                "success": self.success,
                "failed_steps": [s.step.__class__.__name__ for s in self.failed_steps],
                "successful_steps": [s.step.__class__.__name__ for s in self.successful_steps],
                "skipped_steps": [s.step.__class__.__name__ for s in self.skipped_steps],
                "gha_workflow_run_url": self.pipeline_context.gha_workflow_run_url,
                "pipeline_start_timestamp": self.pipeline_context.pipeline_start_timestamp,
                "pipeline_end_timestamp": round(self.created_at.timestamp()),
                "pipeline_duration": round(self.created_at.timestamp()) - self.pipeline_context.pipeline_start_timestamp,
                "git_branch": self.pipeline_context.git_branch,
                "git_revision": self.pipeline_context.git_revision,
                "ci_context": self.pipeline_context.ci_context,
            }
        )

    def print(self):
        connector_name = self.pipeline_context.connector.technical_name
        main_panel_title = Text(f"{connector_name.upper()} - TEST RESULTS")
        main_panel_title.stylize(Style(color="blue", bold=True))
        duration_subtitle = Text(f"⏲️  Total pipeline duration for {connector_name}: {round(self.run_duration)} seconds")
        step_results_table = Table(title="Steps results")
        step_results_table.add_column("Step")
        step_results_table.add_column("Result")
        step_results_table.add_column("Finished after")

        for step_result in self.steps_results:
            step = Text(step_result.step.title)
            step.stylize(step_result.status.get_rich_style())
            result = Text(step_result.status.value)
            result.stylize(step_result.status.get_rich_style())
            step_results_table.add_row(step, result, f"{round((self.created_at - step_result.created_at).total_seconds())}s")

        to_render = [step_results_table]
        if self.failed_steps:
            sub_panels = []
            for failed_step in self.failed_steps:
                errors = Text(failed_step.stderr)
                panel_title = Text(f"{connector_name} {failed_step.step.title.lower()} failures")
                panel_title.stylize(Style(color="red", bold=True))
                sub_panel = Panel(errors, title=panel_title)
                sub_panels.append(sub_panel)
            failures_group = Group(*sub_panels)
            to_render.append(failures_group)

        main_panel = Panel(Group(*to_render), title=main_panel_title, subtitle=duration_subtitle)
        console.print(main_panel)

async def run(context: ConnectorTestContext, semaphore: anyio.Semaphore) -> ConnectorTestReport:
    """Runs a CI pipeline for a single connector.
    A visual DAG can be found on the README.md file of the pipelines modules.

    Args:
        context (ConnectorTestContext): The initialized connector test context.

    Returns:
        ConnectorTestReport: The test reports holding tests results.
    """
    async with semaphore:
        async with context:
            async with asyncer.create_task_group() as task_group:
                tasks = [
                    task_group.soonify(checks.QaChecks(context).run)(),
                    task_group.soonify(checks.CodeFormatChecks(context).run)(),
                    task_group.soonify(tests.run_all_tests)(context),
                ]
            results = list(itertools.chain(*(task.value for task in tasks)))

            context.test_report = ConnectorTestReport(context, steps_results=results)

        return context.test_report


async def run_connectors_test_pipelines(contexts: List[ConnectorTestContext], concurrency: int = 5):
    """Runs a CI pipeline for all the connectors passed.

    Args:
        contexts (List[ConnectorTestContext]): List of connector test contexts for which a CI pipeline needs to be run.
        concurrency (int): Number of test pipeline that can run in parallel. Defaults to 5
    """
    semaphore = anyio.Semaphore(concurrency)
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        async with anyio.create_task_group() as tg:
            for context in contexts:
                context.dagger_client = dagger_client.pipeline(f"{context.connector.technical_name} - Test Pipeline")
                tg.start_soon(run, context, semaphore)
