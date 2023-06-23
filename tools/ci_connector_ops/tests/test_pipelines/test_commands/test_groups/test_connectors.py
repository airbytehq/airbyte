#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest import mock

import pytest
from ci_connector_ops.pipelines.commands.groups import connectors


@pytest.mark.parametrize(
    "ctx, expected",
    [
        (
            mock.MagicMock(
                command_path="my_command_path",
                invoked_subcommand="my_subcommand",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": None,
                },
            ),
            "my_command_path/my_subcommand/my_ci_context/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my_command_path",
                invoked_subcommand="my_subcommand",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my_command_path/my_subcommand/my_ci_job_key/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my_command_path another_command",
                invoked_subcommand="my_subcommand",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my_command_path/another_command/my_subcommand/my_ci_job_key/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path=None,
                invoked_subcommand="my_subcommand",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my_subcommand/my_ci_job_key/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path=None,
                invoked_subcommand="my_subcommand",
                obj={
                    "git_branch": "my_branch/with/slashes",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my_subcommand/my_ci_job_key/my_branch_with_slashes/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path=None,
                invoked_subcommand="my_subcommand",
                obj={
                    "git_branch": "my_branch/with/slashes#and!special@characters",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my_subcommand/my_ci_job_key/my_branch_with_slashesandspecialcharacters/my_pipeline_start_timestamp/my_git_revision",
        ),
    ],
)
def test_render_report_output_prefix(ctx, expected):
    assert connectors.render_report_output_prefix(ctx) == expected
