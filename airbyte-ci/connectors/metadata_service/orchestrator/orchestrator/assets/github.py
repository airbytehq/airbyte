#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import datetime
import hashlib
import os
import textwrap

import pandas as pd
import yaml
from dagster import OpExecutionContext, Output, asset
from github import Repository
from orchestrator.logging import sentry
from orchestrator.models.metadata import LatestMetadataEntry, MetadataDefinition
from orchestrator.ops.slack import send_slack_message
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe

GROUP_NAME = "github"
TOOLING_TEAM_SLACK_TEAM_ID = "S077R8636CV"
# We give 6 hours for the metadata to be updated
# This is an empirical value that we can adjust if needed
# When our auto-merge pipeline runs it can merge hundreds of up-to-date PRs following.
# Given our current publish concurrency of 10 runners, it can take up to 6 hours to publish all the connectors.
# A shorter grace period could lead to false positives in stale metadata detection.
PUBLISH_GRACE_PERIOD = datetime.timedelta(hours=int(os.getenv("PUBLISH_GRACE_PERIOD_HOURS", 6)))


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


def _get_content_of_github_file(context: OpExecutionContext, github_connector_repo: Repository, path: str) -> str:
    context.log.debug(f"retrieving contents of {path}")
    return github_connector_repo.get_contents(path)


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


@asset(required_resource_keys={"github_connector_repo", "github_connectors_metadata_files"}, group_name=GROUP_NAME)
def github_metadata_definitions(context):
    """
    Return a list of all metadata definitions hosted on our github repo
    """
    github_connector_repo = context.resources.github_connector_repo
    github_connectors_metadata_files = context.resources.github_connectors_metadata_files

    metadata_definitions = []
    for metadata_file in github_connectors_metadata_files:
        metadata_raw = _get_content_of_github_file(context, github_connector_repo, metadata_file["path"])
        metadata_dict = yaml.safe_load(metadata_raw.decoded_content)
        if metadata_dict.get("data").get("supportLevel") == "archived":
            print(f"Skipping archived connector: {metadata_dict.get('data').get('dockerRepository')}")
            continue
        metadata_definitions.append(
            LatestMetadataEntry(
                metadata_definition=MetadataDefinition.parse_obj(metadata_dict), last_modified=metadata_file["last_modified"]
            )
        )

    return Output(metadata_definitions, metadata={"preview": [md.json() for md in metadata_definitions]})


def entry_should_be_on_gcs(metadata_entry: LatestMetadataEntry) -> bool:
    if metadata_entry.metadata_definition.data.supportLevel == "archived":
        return False
    if getattr(metadata_entry.metadata_definition.releases, "isReleaseCandidate", False):
        return False
    if (
        datetime.datetime.strptime(metadata_entry.last_modified, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=datetime.timezone.utc)
        > datetime.datetime.now(datetime.timezone.utc) - PUBLISH_GRACE_PERIOD
    ):
        return False
    return True


@asset(required_resource_keys={"slack"}, group_name=GROUP_NAME)
def stale_gcs_latest_metadata_file(context, github_metadata_definitions: list, latest_metadata_entries: list) -> OutputDataFrame:
    """
    Return a list of all metadata files in the github repo and denote whether they are stale or not.

    Stale means that the file in the github repo is not in the latest metadata file blobs.
    """
    latest_versions_on_gcs = {
        metadata_entry.metadata_definition.data.dockerRepository: metadata_entry.metadata_definition.data.dockerImageTag
        for metadata_entry in latest_metadata_entries
        if metadata_entry.metadata_definition.data.supportLevel != "archived"
    }

    latest_versions_on_github = {
        metadata_entry.metadata_definition.data.dockerRepository: metadata_entry.metadata_definition.data.dockerImageTag
        for metadata_entry in github_metadata_definitions
        if entry_should_be_on_gcs(metadata_entry)
    }

    stale_connectors = []
    for docker_repository, github_docker_image_tag in latest_versions_on_github.items():
        gcs_docker_image_tag = latest_versions_on_gcs.get(docker_repository)
        if gcs_docker_image_tag != github_docker_image_tag:
            stale_connectors.append(
                {"connector": docker_repository, "master_version": github_docker_image_tag, "gcs_version": gcs_docker_image_tag}
            )

    stale_connectors_df = pd.DataFrame(stale_connectors)

    # If any stale files exist, report to slack
    stale_report_channel = os.getenv("STALE_REPORT_CHANNEL")
    publish_update_channel = os.getenv("PUBLISH_UPDATE_CHANNEL")
    any_stale = len(stale_connectors_df) > 0
    if any_stale and stale_report_channel:
        stale_report_md = stale_connectors_df.to_markdown(index=False)
        send_slack_message(context, stale_report_channel, f"🚨 Stale metadata detected! (cc. <!subteam^{TOOLING_TEAM_SLACK_TEAM_ID}>)")
        send_slack_message(context, stale_report_channel, stale_report_md, enable_code_block_wrapping=True)
    if not any_stale and publish_update_channel:
        message = textwrap.dedent(
            f"""
        Analyzed {len(latest_versions_on_github)} metadata files on our master branch and {len(latest_versions_on_gcs)} latest metadata files hosted in GCS.
        All dockerImageTag value on master match the latest metadata files on GCS.
        No stale metadata: GCS metadata are up to date with metadata hosted on GCS.
        """
        )
        send_slack_message(context, publish_update_channel, message)
    return output_dataframe(stale_connectors_df)


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
