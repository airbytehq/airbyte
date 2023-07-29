#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest import mock

import pytest
from connector_ops.utils import Connector
from pipelines import utils


@pytest.mark.parametrize(
    "ctx, expected",
    [
        (
            mock.MagicMock(
                command_path="my command path",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": None,
                },
            ),
            "my/command/path/my_ci_context/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my command path",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my/command/path/my_ci_job_key/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my command path",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my/command/path/my_ci_job_key/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my command path",
                obj={
                    "git_branch": "my_branch",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my/command/path/my_ci_job_key/my_branch/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my command path",
                obj={
                    "git_branch": "my_branch/with/slashes",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my/command/path/my_ci_job_key/my_branch_with_slashes/my_pipeline_start_timestamp/my_git_revision",
        ),
        (
            mock.MagicMock(
                command_path="my command path",
                obj={
                    "git_branch": "my_branch/with/slashes#and!special@characters",
                    "git_revision": "my_git_revision",
                    "pipeline_start_timestamp": "my_pipeline_start_timestamp",
                    "ci_context": "my_ci_context",
                    "ci_job_key": "my_ci_job_key",
                },
            ),
            "my/command/path/my_ci_job_key/my_branch_with_slashesandspecialcharacters/my_pipeline_start_timestamp/my_git_revision",
        ),
    ],
)
def test_render_report_output_prefix(ctx, expected):
    assert utils.DaggerPipelineCommand.render_report_output_prefix(ctx) == expected


def test_get_modified_connectors_and_files(new_connector: Connector):
    modified_files = ["airbyte-integrations/connectors/source-pokeapi/source_pokeapi/spec.json", new_connector.code_directory / "setup.py"]
    assert utils.get_modified_connectors_and_files(modified_files) == {
        Connector("source-pokeapi"): [modified_files[0]],
        new_connector: [modified_files[1]],
    }
