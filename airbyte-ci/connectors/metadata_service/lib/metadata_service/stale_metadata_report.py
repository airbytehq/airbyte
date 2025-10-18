#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
import os
import re
import textwrap
from typing import Any, Mapping, Optional

import pandas as pd
import requests
import yaml
from github import Auth, Github

from metadata_service.helpers.gcs import get_gcs_storage_client
from metadata_service.helpers.slack import send_slack_message
from metadata_service.models.generated import ConnectorMetadataDefinitionV0

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
    """
    Determine if a metadata entry is younger than the grace period.

    Args:
        last_modified_at (datetime.datetime): The last modified date of the metadata entry.
    Returns:
        bool: True if the metadata entry is younger than the grace period, False otherwise.
    """
    grace_period_marker = datetime.datetime.now(datetime.timezone.utc) - PUBLISH_GRACE_PERIOD
    return last_modified_at > grace_period_marker


def _entry_should_be_on_gcs(metadata_model: ConnectorMetadataDefinitionV0) -> bool:
    """
    Determine if a metadata entry should be on GCS.

    Args:
        metadata_model (ConnectorMetadataDefinitionV0): A ConnectorMetadataDefinitionV0 object.
    Returns:
        bool: True if the metadata entry should be on GCS, False otherwise.
    """
    if metadata_model.data.supportLevel and metadata_model.data.supportLevel.__root__ == "archived":
        logger.info(
            f"Skipping. Connector `{metadata_model.data.dockerRepository}` is archived or does not have a support level. Support level: {metadata_model.data.supportLevel.__root__}"
        )
        return False
    if "-rc" in metadata_model.data.dockerImageTag:
        logger.info(
            f"Skipping. Connector `{metadata_model.data.dockerRepository}` is a release candidate. Docker image tag: {metadata_model.data.dockerImageTag}"
        )
        return False
    return True


def _get_github_metadata_download_urls() -> list[str]:
    """
    Get the download URLs for the metadata files on GitHub.

    Returns:
        list[str]: A list of download URLs for the metadata files on GitHub.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN is not set")
    auth = Auth.Token(github_token)
    github_client = Github(auth=auth)
    repo = github_client.get_repo(GITHUB_REPO_NAME)

    query = f"repo:{repo.full_name} filename:{METADATA_FILE_NAME}"
    file_contents = github_client.search_code(query)

    logger.debug("Getting the download URL for each found metadata file.")

    metadata_download_urls = []
    for file_content in file_contents:
        logger.debug(f"File content path: {file_content.path}")
        if re.match(r"airbyte-integrations/connectors/(source|destination)-.+/metadata\.yaml$", file_content.path):
            logger.debug(f"Getting commits for file: {file_content.path}")
            commits = repo.get_commits(path=file_content.path)
            last_modified_at = commits[0].commit.author.date
            if not _is_younger_than_grace_period(last_modified_at):
                metadata_download_urls.append(file_content.download_url)
            else:
                logger.info(
                    f"Skipping. Metadata file on Github `{file_content.path}` was modified more recently than the grace period. Last modified at: {last_modified_at}"
                )
    logger.debug(f"Found {len(metadata_download_urls)} download URLs")

    return metadata_download_urls


def _get_and_parse_metadata_files(metadata_download_urls: list[str]) -> list[ConnectorMetadataDefinitionV0]:
    """
    Get and parse the contents of the metadata files.

    Args:
        metadata_download_urls (list[str]): A list of download URLs for the metadata files.
    Returns:
        list[ConnectorMetadataDefinitionV0]: A list of ConnectorMetadataDefinitionV0 objects.
    """
    logger.debug("Downloading and parsing the contents of the metadata files.")
    connector_metadata_list = []
    for metadata_download_url in metadata_download_urls:
        logger.debug(f"Downloading metadata from {metadata_download_url}")
        response = requests.get(metadata_download_url)
        response.raise_for_status()
        metadata_yaml = response.text
        metadata_dict = yaml.safe_load(metadata_yaml)
        try:
            connector_metadata = ConnectorMetadataDefinitionV0.parse_obj(metadata_dict)
            connector_metadata_list.append(connector_metadata)
        except Exception as e:
            logger.info(f"Skipping. Failed to parse metadata for metadata at path: {metadata_download_url}. Exception: {e}")
            continue
    logger.debug(f"Parsed {len(connector_metadata_list)} metadata files")
    return connector_metadata_list


def _get_latest_metadata_versions_on_github() -> Mapping[str, Any]:
    """
    Get the latest metadata versions on GitHub.

    Returns:
        Mapping[str, Any]: A mapping of connector names to their latest metadata versions on GitHub.
    """
    logger.info(f"Getting latest metadata versions on GitHub for {GITHUB_REPO_NAME}")

    metadata_download_urls = _get_github_metadata_download_urls()
    github_connector_metadata = _get_and_parse_metadata_files(metadata_download_urls)

    latest_metadata_versions_on_github = {
        connector_metadata.data.dockerRepository: connector_metadata.data.dockerImageTag
        for connector_metadata in github_connector_metadata
        if _entry_should_be_on_gcs(connector_metadata)
    }

    logger.info(f"Found {len(latest_metadata_versions_on_github)} connectors on GitHub")

    return latest_metadata_versions_on_github


def _get_latest_metadata_entries_on_gcs(bucket_name: str) -> Mapping[str, Any]:
    """
    Get the latest metadata entries on GCS.

    Args:
        bucket_name (str): The name of the GCS bucket to check for stale metadata.
    Returns:
        Mapping[str, Any]: A mapping of connector names to their latest metadata versions on GCS.
    """
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
        metadata_dict = yaml.safe_load(blob.download_as_bytes().decode("utf-8"))
        connector_metadata = ConnectorMetadataDefinitionV0.parse_obj(metadata_dict)
        latest_metadata_entries_on_gcs[connector_metadata.data.dockerRepository] = connector_metadata.data.dockerImageTag

    logger.info(f"Found {len(latest_metadata_entries_on_gcs)} connectors on GCS")
    return latest_metadata_entries_on_gcs


def _generate_stale_metadata_report(
    latest_metadata_versions_on_github: Mapping[str, Any], latest_metadata_entries_on_gcs: Mapping[str, Any]
) -> pd.DataFrame:
    """
    Generate the stale metadata report.

    Args:
        latest_metadata_versions_on_github (Mapping[str, Any]): A mapping of connector names to their latest metadata versions on GitHub.
        latest_metadata_entries_on_gcs (Mapping[str, Any]): A mapping of connector names to their latest metadata versions on GCS.
    Returns:
        pd.DataFrame: A DataFrame containing the stale metadata.
    """
    stale_connectors = []
    for docker_repository, github_docker_image_tag in latest_metadata_versions_on_github.items():
        gcs_docker_image_tag = latest_metadata_entries_on_gcs.get(docker_repository)
        if gcs_docker_image_tag != github_docker_image_tag:
            stale_connectors.append(
                {"connector": docker_repository, "master_version": github_docker_image_tag, "gcs_version": gcs_docker_image_tag}
            )

    stale_connectors.sort(key=lambda x: x.get("connector"))
    return pd.DataFrame(stale_connectors)


def _publish_stale_metadata_report(
    stale_metadata_report: pd.DataFrame, latest_metadata_versions_on_github_count: int, latest_metadata_versions_on_gcs_count: int
) -> tuple[bool, Optional[str]]:
    """
    Publish the stale metadata report to the specified Slack channels.

    Args:
        stale_metadata_report (pd.DataFrame): A DataFrame containing the stale metadata.
        latest_metadata_versions_on_github_count (int): The number of metadata files on our master branch.
        latest_metadata_versions_on_gcs_count (int): The number of latest metadata files hosted in GCS.
    Returns:
        tuple[bool, Optional[str]]: A tuple containing a boolean indicating whether the report was published and an error message.
    """
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
        Analyzed {latest_metadata_versions_on_github_count} metadata files on our master branch and {latest_metadata_versions_on_gcs_count} latest metadata files hosted in GCS.
        All dockerImageTag value on master match the latest metadata files on GCS.
        No stale metadata: GCS metadata are up to date with metadata hosted on GCS.
        """
        )
        sent, error_message = send_slack_message(PUBLISH_UPDATE_CHANNEL, message)
        if not sent:
            logger.error(f"Failed to send success message: {error_message}")
            return sent, error_message
    return True, None


def generate_and_publish_stale_metadata_report(bucket_name: str) -> tuple[bool, Optional[str]]:
    """
    Generate a stale metadata report and publish it to a Slack channel.

    Args:
        bucket_name (str): The name of the GCS bucket to check for stale metadata.
    Returns:
        tuple[bool, Optional[str]]: A tuple containing a boolean indicating whether the report was published and an optional error message.
    """
    latest_metadata_entries_on_gcs = _get_latest_metadata_entries_on_gcs(bucket_name)
    latest_metadata_versions_on_github = _get_latest_metadata_versions_on_github()
    stale_metadata_report = _generate_stale_metadata_report(latest_metadata_versions_on_github, latest_metadata_entries_on_gcs)
    report_published, error_message = _publish_stale_metadata_report(
        stale_metadata_report, len(latest_metadata_versions_on_github), len(latest_metadata_entries_on_gcs)
    )
    return report_published, error_message
