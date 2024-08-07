#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import datetime
import hashlib
import os

import dateutil
import humanize
import pandas as pd
from dagster import OpExecutionContext, Output, asset
from github import Repository
from orchestrator.logging import sentry
from orchestrator.ops.slack import send_slack_message
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe

GROUP_NAME = "github"


def _get_md5_of_github_file(context: OpExecutionContext, github_connector_repo: Repository, path: str) -> str:
    """
    Return the md5 hash of a file in the github repo.
    """
    context.log.debug(f"retrieving contents of {path}")
    file_contents = github_connector_repo.get_contents(path)

    # calculate the md5 hash of the file contents
    context.log.debug(f"calculating md5 hash of {path}")
    md5_hash = hashlib.md5()
    md5_hash.update(file_contents.decoded_content)
    base_64_value = base64.b64encode(md5_hash.digest()).decode("utf8")
    return base_64_value


@asset(required_resource_keys={"github_connectors_directory"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def github_connector_folders(context):
    """
    Return a list of all the folders in the github connectors directory.
    """
    github_connectors_directory = context.resources.github_connectors_directory

    folder_names = [item.name for item in github_connectors_directory if item.type == "dir"]
    return Output(folder_names, metadata={"preview": folder_names})


@asset(required_resource_keys={"github_connector_repo", "github_connectors_metadata_files"}, group_name=GROUP_NAME)
def github_metadata_file_md5s(context):
    """
    Return a list of all the folders in the github connectors directory.
    """
    github_connector_repo = context.resources.github_connector_repo
    github_connectors_metadata_files = context.resources.github_connectors_metadata_files

    metadata_file_paths = {
        metadata_file["path"]: {
            "md5": _get_md5_of_github_file(context, github_connector_repo, metadata_file["path"]),
            "last_modified": metadata_file["last_modified"],
        }
        for metadata_file in github_connectors_metadata_files
    }

    return Output(metadata_file_paths, metadata={"preview": metadata_file_paths})


def _should_publish_have_ran(datetime_string: str) -> bool:
    """
    Return true if the datetime is 2 hours old.

    """
    dt = dateutil.parser.parse(datetime_string)
    now = datetime.datetime.now(datetime.timezone.utc)
    two_hours_ago = now - datetime.timedelta(hours=2)
    return dt < two_hours_ago


def _to_time_ago(datetime_string: str) -> str:
    """
    Return a string of how long ago the datetime is human readable format. 10 min
    """
    dt = dateutil.parser.parse(datetime_string)
    return humanize.naturaltime(dt)


def _is_stale(github_file_info: dict, latest_gcs_metadata_md5s: dict) -> bool:
    """
    Return true if the github info is stale.
    """
    not_in_gcs = latest_gcs_metadata_md5s.get(github_file_info["md5"]) is None
    return not_in_gcs and _should_publish_have_ran(github_file_info["last_modified"])


@asset(required_resource_keys={"slack", "latest_metadata_file_blobs"}, group_name=GROUP_NAME)
def stale_gcs_latest_metadata_file(context, github_metadata_file_md5s: dict) -> OutputDataFrame:
    """
    Return a list of all metadata files in the github repo and denote whether they are stale or not.

    Stale means that the file in the github repo is not in the latest metadata file blobs.
    """
    human_readable_stale_bools = {True: "🚨 YES!!!", False: "No"}
    latest_gcs_metadata_file_blobs = context.resources.latest_metadata_file_blobs
    latest_gcs_metadata_md5s = {blob.md5_hash: blob.name for blob in latest_gcs_metadata_file_blobs}

    stale_report = [
        {
            "stale": _is_stale(github_file_info, latest_gcs_metadata_md5s),
            "github_path": github_path,
            "github_md5": github_file_info["md5"],
            "github_last_modified": _to_time_ago(github_file_info["last_modified"]),
            "gcs_md5": latest_gcs_metadata_md5s.get(github_file_info["md5"]),
            "gcs_path": latest_gcs_metadata_md5s.get(github_file_info["md5"]),
        }
        for github_path, github_file_info in github_metadata_file_md5s.items()
    ]

    stale_metadata_files_df = pd.DataFrame(stale_report)

    # sort by stale true to false, then by github_path
    stale_metadata_files_df = stale_metadata_files_df.sort_values(
        by=["stale", "github_path"],
        ascending=[False, True],
    )

    # If any stale files exist, report to slack
    channel = os.getenv("STALE_REPORT_CHANNEL")
    any_stale = stale_metadata_files_df["stale"].any()
    if channel and any_stale:
        only_stale_df = stale_metadata_files_df[stale_metadata_files_df["stale"] == True]
        pretty_stale_df = only_stale_df.replace(human_readable_stale_bools)
        stale_report_md = pretty_stale_df.to_markdown(index=False)
        send_slack_message(context, channel, stale_report_md, enable_code_block_wrapping=True)

    stale_metadata_files_df.replace(human_readable_stale_bools, inplace=True)
    return output_dataframe(stale_metadata_files_df)


@asset(required_resource_keys={"github_connector_nightly_workflow_successes"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def github_connector_nightly_workflow_successes(context: OpExecutionContext) -> OutputDataFrame:
    """
    Return a list of all the latest nightly workflow runs for the connectors repo.
    """
    github_connector_nightly_workflow_successes = context.resources.github_connector_nightly_workflow_successes

    workflow_df = pd.DataFrame(github_connector_nightly_workflow_successes)
    workflow_df = workflow_df[
        [
            "id",
            "name",
            "head_branch",
            "head_sha",
            "run_number",
            "status",
            "conclusion",
            "workflow_id",
            "url",
            "created_at",
            "updated_at",
            "run_started_at",
        ]
    ]
    return output_dataframe(workflow_df)
