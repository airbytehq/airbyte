#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
import os
import textwrap
from typing import Any, Mapping

import pandas as pd
import requests
import yaml
from github import Auth, Github
from github.ContentFile import ContentFile
from google.cloud import storage

from metadata_service.helpers.gcs import get_gcs_storage_client
from metadata_service.helpers.slack import send_slack_message

from .constants import METADATA_FILE_NAME, METADATA_FOLDER, REPOSITORY_NAME

logger = logging.getLogger(__name__)


EXTENSIBILITY_TEAM_SLACK_TEAM_ID = "S08SQDL2RS9"  # @oc-extensibility-critical-systems
# We give 6 hours for the metadata to be updated
# This is an empirical value that we can adjust if needed
# When our auto-merge pipeline runs it can merge hundreds of up-to-date PRs following.
# Given our current publish concurrency of 10 runners, it can take up to 6 hours to publish all the connectors.
# A shorter grace period could lead to false positives in stale metadata detection.
PUBLISH_GRACE_PERIOD = datetime.timedelta(hours=int(os.getenv("PUBLISH_GRACE_PERIOD_HOURS", 6)))


def _is_younger_than_grace_period(file_content: ContentFile) -> bool:
    grace_period_marker = datetime.datetime.now(datetime.timezone.utc) - PUBLISH_GRACE_PERIOD
    return file_content.last_modified_at > grace_period_marker


def _entry_should_be_on_gcs(metadata_dict: Mapping[str, Any]) -> bool:
    if metadata_dict["supportLevel"] == "archived":
        return False
    if "-rc" in metadata_dict["dockerImageTag"]:
        return False
    return True


def _get_latest_metadata_versions_on_github() -> Mapping[str, Any]:
    github_token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(github_token)
    github_client = Github(auth=auth)
    repo = github_client.get_repo(REPOSITORY_NAME)

    # Gets all files in the connectors folder, then filters for metadata.yaml files that are older than the grace period and appends the download url to a list.
    contents = repo.get_contents("/airbyte-integrations/connectors/")
    metadata_download_urls = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        elif file_content.name == "metadata.yaml" and not _is_younger_than_grace_period(file_content):
            metadata_download_urls.append(file_content.download_url)

    metadata_dicts = []
    for metadata_download_url in metadata_download_urls:
        response = requests.get(metadata_download_url)
        response.raise_for_status()
        metadata_yaml = response.text
        metadata_dict = yaml.safe_load(metadata_yaml)
        metadata_dicts.append(metadata_dict)

    latest_metadata_versions_on_github = {
        metadata_dict["dockerRepository"]: metadata_dict["dockerImageTag"]
        for metadata_dict in metadata_dicts
        if _entry_should_be_on_gcs(metadata_dict)
    }

    return latest_metadata_versions_on_github


def _get_latest_metadata_entries_on_gcs(bucket_name: str) -> Mapping[str, Any]:
    storage_client = get_gcs_storage_client()
    bucket = storage_client.bucket(bucket_name)

    blobs: list[storage.Blob] = bucket.list_blobs(match_glob=f"{METADATA_FOLDER}/**/latest/{METADATA_FILE_NAME}")

    latest_metadata_entries_on_gcs = {}
    for blob in blobs:
        metadata_dict = yaml.safe_load(blob.download_as_string().decode("utf-8"))
        latest_metadata_entries_on_gcs[metadata_dict["dockerRepository"]] = metadata_dict["dockerImageTag"]

    return latest_metadata_entries_on_gcs


def _generate_stale_metadata_report(
    latest_metadata_versions_on_github: Mapping[str, Any], latest_metadata_entries_on_gcs: Mapping[str, Any]
) -> pd.DataFrame:
    stale_connectors = []
    for docker_repository, github_docker_image_tag in latest_metadata_versions_on_github.items():
        gcs_docker_image_tag = latest_metadata_entries_on_gcs.get(docker_repository)
        if gcs_docker_image_tag != github_docker_image_tag:
            stale_connectors.append(
                {"connector": docker_repository, "master_version": github_docker_image_tag, "gcs_version": gcs_docker_image_tag}
            )

    return pd.DataFrame(stale_connectors)


def generate_and_publish_stale_metadata_report(bucket_name: str) -> tuple[bool, str]:
    """
    Generate a stale metadata report and publish it to a Slack channel.

    Args:
        bucket_name (str): The name of the GCS bucket to check for stale metadata.

    Returns:
        bool: True if any stale metadata was detected, False otherwise.
    """

    latest_metadata_versions_on_github = _get_latest_metadata_versions_on_github()
    latest_metadata_entries_on_gcs = _get_latest_metadata_entries_on_gcs(bucket_name)
    stale_metadata_report = _generate_stale_metadata_report(latest_metadata_versions_on_github, latest_metadata_entries_on_gcs)

    stale_report_channel = os.getenv("STALE_REPORT_CHANNEL")
    publish_update_channel = os.getenv("PUBLISH_UPDATE_CHANNEL")
    any_stale = len(stale_metadata_report) > 0
    if any_stale and stale_report_channel:
        stale_report_md = stale_metadata_report.to_markdown(index=False)
        send_slack_message(stale_report_channel, f"🚨 Stale metadata detected! (cc. <!subteam^{EXTENSIBILITY_TEAM_SLACK_TEAM_ID}>)")
        send_slack_message(stale_report_channel, stale_report_md, enable_code_block_wrapping=True)

    if not any_stale and publish_update_channel:
        message = textwrap.dedent(
            f"""
        Analyzed {len(latest_metadata_versions_on_github)} metadata files on our master branch and {len(latest_metadata_entries_on_gcs)} latest metadata files hosted in GCS.
        All dockerImageTag value on master match the latest metadata files on GCS.
        No stale metadata: GCS metadata are up to date with metadata hosted on GCS.
        """
        )
        send_slack_message(publish_update_channel, message)
