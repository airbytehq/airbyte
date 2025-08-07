#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
import os
import re
import textwrap
from typing import Any, Mapping

import pandas as pd
import requests
import yaml
from github import Auth, Github
from google.cloud import storage

from metadata_service.helpers.gcs import get_gcs_storage_client
from metadata_service.helpers.slack import send_slack_message
from metadata_service.validators.metadata_validator import STALE_METADATA_VALIDATORS, is_valid_metadata

from .constants import (
    EXTENSIBILITY_TEAM_SLACK_TEAM_ID,
    GITHUB_REPO_NAME,
    METADATA_FILE_NAME,
    METADATA_FOLDER,
    PUBLISH_GRACE_PERIOD,
    PUBLISH_UPDATE_CHANNEL,
    STALE_REPORT_CHANNEL,
)

logger = logging.getLogger(__name__)


def _is_younger_than_grace_period(last_modified_at: datetime.datetime) -> bool:
    grace_period_marker = datetime.datetime.now(datetime.timezone.utc) - PUBLISH_GRACE_PERIOD
    return last_modified_at > grace_period_marker


def _entry_should_be_on_gcs(metadata_dict: Mapping[str, Any]) -> bool:
    if not is_valid_metadata(metadata_dict, STALE_METADATA_VALIDATORS):
        logger.error(f"Invalid metadata: {metadata_dict['data']['dockerRepository']}")
        return False
    if metadata_dict["data"].get("supportLevel") == "archived":
        return False
    if "-rc" in metadata_dict["data"].get("dockerImageTag", ""):
        return False
    return True


def _get_latest_metadata_versions_on_github() -> Mapping[str, Any]:
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN is not set")
    auth = Auth.Token(github_token)
    github_client = Github(auth=auth)
    repo = github_client.get_repo(GITHUB_REPO_NAME)

    logger.info(f"Getting latest metadata versions on GitHub for {GITHUB_REPO_NAME}")

    # Gets all files that match the query, then filters for metadata based on path, then gets the latest commit datetime, then checks if it's older than the grace period.
    query = f"repo:{repo.full_name} filename:{METADATA_FILE_NAME}"
    file_contents = github_client.search_code(query)
    logger.debug("Found files matching the query.")

    logger.debug("Getting the download URL for each file.")
    metadata_download_urls = []
    for file_content in file_contents:
        logger.debug(f"File content path: {file_content.path}")
        if re.match(r"airbyte-integrations/connectors/(source|destination)-.+/metadata\.yaml$", file_content.path):
            logger.debug(f"Getting commits for file: {file_content.path}")
            commits = repo.get_commits(path=file_content.path)
            last_modified_at = commits[0].commit.author.date
            if not _is_younger_than_grace_period(last_modified_at):
                metadata_download_urls.append(file_content.download_url)
    logger.debug(f"Found {len(metadata_download_urls)} download URLs")

    # Download and parse the contents of the metadata files
    logger.debug("Downloading and parsing the contents of the metadata files.")
    metadata_dicts = []
    for metadata_download_url in metadata_download_urls:
        logger.debug(f"Downloading metadata from {metadata_download_url}")
        response = requests.get(metadata_download_url)
        response.raise_for_status()
        metadata_yaml = response.text
        metadata_dict = yaml.safe_load(metadata_yaml)
        metadata_dicts.append(metadata_dict)
    logger.debug(f"Parsed {len(metadata_dicts)} metadata files")

    latest_metadata_versions_on_github = {
        metadata_dict["data"]["dockerRepository"]: metadata_dict["data"]["dockerImageTag"]
        for metadata_dict in metadata_dicts
        if _entry_should_be_on_gcs(metadata_dict)
    }

    logger.info(f"Found {len(latest_metadata_versions_on_github)} connectors on GitHub")
    return latest_metadata_versions_on_github


def _get_latest_metadata_entries_on_gcs(bucket_name: str) -> Mapping[str, Any]:
    logger.info(f"Getting latest metadata entries on GCS for {bucket_name}")

    storage_client = get_gcs_storage_client()
    bucket = storage_client.bucket(bucket_name)

    try:
        logger.debug(f"Listing blobs in {bucket_name} with prefix {METADATA_FOLDER}/**/latest/{METADATA_FILE_NAME}")
        blobs = bucket.list_blobs(match_glob=f"{METADATA_FOLDER}/**/latest/{METADATA_FILE_NAME}")
        logger.debug("Found blobs.")
    except Exception as e:
        logger.error(f"Error getting blobs from GCS: {e}")
        raise e

    latest_metadata_entries_on_gcs = {}
    for blob in blobs:
        assert isinstance(blob, storage.Blob)
        metadata_dict = yaml.safe_load(blob.download_as_bytes().decode("utf-8"))
        latest_metadata_entries_on_gcs[metadata_dict["data"]["dockerRepository"]] = metadata_dict["data"]["dockerImageTag"]

    logger.info(f"Found {len(latest_metadata_entries_on_gcs)} connectors on GCS")
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

    stale_connectors.sort(key=lambda x: x.get("connector"))
    return pd.DataFrame(stale_connectors)


def generate_and_publish_stale_metadata_report(bucket_name: str) -> tuple[bool, str]:
    """
    Generate a stale metadata report and publish it to a Slack channel.

    Args:
        bucket_name (str): The name of the GCS bucket to check for stale metadata.
    """
    latest_metadata_versions_on_github = _get_latest_metadata_versions_on_github()
    latest_metadata_entries_on_gcs = _get_latest_metadata_entries_on_gcs(bucket_name)
    stale_metadata_report = _generate_stale_metadata_report(latest_metadata_versions_on_github, latest_metadata_entries_on_gcs)

    any_stale = len(stale_metadata_report) > 0
    if any_stale:
        stale_report_md = stale_metadata_report.to_markdown(index=False)
        send_slack_message(STALE_REPORT_CHANNEL, f"🚨 Stale metadata detected! (cc. <!subteam^{EXTENSIBILITY_TEAM_SLACK_TEAM_ID}>)")
        sent, error_message = send_slack_message(STALE_REPORT_CHANNEL, stale_report_md, enable_code_block_wrapping=True)
        if not sent:
            logger.error(f"Failed to send stale metadata report: {error_message}")
            return sent, error_message
    if not any_stale:
        message = textwrap.dedent(
            f"""
        Analyzed {len(latest_metadata_versions_on_github)} metadata files on our master branch and {len(latest_metadata_entries_on_gcs)} latest metadata files hosted in GCS.
        All dockerImageTag value on master match the latest metadata files on GCS.
        No stale metadata: GCS metadata are up to date with metadata hosted on GCS.
        """
        )
        sent, error_message = send_slack_message(PUBLISH_UPDATE_CHANNEL, message)
        if not sent:
            logger.error(f"Failed to send success message: {error_message}")
            return sent, error_message
    return True, None
