#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import datetime
import logging
import os
import re
import textwrap
from pathlib import Path
from typing import Any, List, Mapping, Optional

import pandas as pd
import requests
import yaml
from github import Auth, Github

from metadata_service.gcs_upload import upload_metadata_to_gcs
from metadata_service.helpers.gcs import get_gcs_storage_client
from metadata_service.helpers.slack import send_slack_message
from metadata_service.models.generated import ConnectorMetadataDefinitionV0
from metadata_service.validators.metadata_validator import ValidatorOptions

from .constants import (
    CONNECTORS_PATH,
    DOCS_FOLDER_PATH,
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


def _get_connector_name_from_docker_repository(docker_repository: str) -> str:
    """
    Extract the connector name from a docker repository string.

    Args:
        docker_repository (str): The docker repository (e.g., "airbyte/source-github").
    Returns:
        str: The connector name (e.g., "source-github").
    """
    return docker_repository.split("/")[-1]


def _get_connector_type_from_name(connector_name: str) -> str:
    """
    Extract the connector type from a connector name.

    Args:
        connector_name (str): The connector name (e.g., "source-github").
    Returns:
        str: The connector type (e.g., "sources" or "destinations").
    """
    if connector_name.startswith("source-"):
        return "sources"
    elif connector_name.startswith("destination-"):
        return "destinations"
    else:
        raise ValueError(f"Unknown connector type for connector: {connector_name}")


def _get_docs_path_for_connector(repo_root: Path, connector_name: str) -> Path:
    """
    Get the docs path for a connector.

    Args:
        repo_root (Path): The root path of the repository.
        connector_name (str): The connector name (e.g., "source-github").
    Returns:
        Path: The path to the connector's documentation file.
    """
    connector_type = _get_connector_type_from_name(connector_name)
    doc_name = connector_name.replace("source-", "").replace("destination-", "")
    return repo_root / DOCS_FOLDER_PATH / connector_type / doc_name


def _auto_heal_stale_connectors(
    stale_connectors: List[str],
    bucket_name: str,
    repo_root: Path,
) -> List[str]:
    """
    Attempt to auto-heal stale connectors by uploading their metadata to GCS.

    Args:
        stale_connectors (List[str]): List of stale connector docker repositories.
        bucket_name (str): The name of the GCS bucket to upload metadata to.
        repo_root (Path): The root path of the repository.
    Returns:
        List[str]: List of connectors that were successfully healed.
    """
    healed_connectors = []

    for docker_repository in stale_connectors:
        connector_name = _get_connector_name_from_docker_repository(docker_repository)
        metadata_file_path = repo_root / CONNECTORS_PATH / connector_name / METADATA_FILE_NAME

        if not metadata_file_path.exists():
            logger.warning(f"Metadata file not found for {connector_name} at {metadata_file_path}. Skipping auto-heal.")
            continue

        try:
            docs_path = _get_docs_path_for_connector(repo_root, connector_name)
            validator_opts = ValidatorOptions(
                docs_path=str(docs_path),
                prerelease_tag=None,
                disable_dockerhub_checks=True,
            )

            logger.info(f"Auto-healing connector {connector_name} by uploading metadata to GCS...")
            upload_info = upload_metadata_to_gcs(bucket_name, metadata_file_path, validator_opts)

            if upload_info.metadata_uploaded:
                logger.info(f"Successfully auto-healed connector {connector_name}")
                healed_connectors.append(docker_repository)
            else:
                logger.warning(f"Metadata upload for {connector_name} did not result in any changes")

        except Exception as e:
            logger.error(f"Failed to auto-heal connector {connector_name}: {e}")
            continue

    return healed_connectors


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


def generate_and_publish_stale_metadata_report(
    bucket_name: str,
    repo_root: Optional[Path] = None,
) -> tuple[bool, Optional[str]]:
    """
    Generate a stale metadata report and publish it to a Slack channel.

    If repo_root is provided, attempts to auto-heal stale connectors by uploading
    their metadata to GCS before publishing the report.

    Args:
        bucket_name (str): The name of the GCS bucket to check for stale metadata.
        repo_root (Optional[Path]): The root path of the repository. If provided,
            enables auto-healing of stale connectors.
    Returns:
        tuple[bool, Optional[str]]: A tuple containing a boolean indicating whether the report was published and an optional error message.
    """
    latest_metadata_entries_on_gcs = _get_latest_metadata_entries_on_gcs(bucket_name)
    latest_metadata_versions_on_github = _get_latest_metadata_versions_on_github()
    stale_metadata_report = _generate_stale_metadata_report(latest_metadata_versions_on_github, latest_metadata_entries_on_gcs)

    if len(stale_metadata_report) > 0 and repo_root is not None:
        logger.info(f"Found {len(stale_metadata_report)} stale connectors. Attempting auto-heal...")
        stale_connector_names = stale_metadata_report["connector"].tolist()
        healed_connectors = _auto_heal_stale_connectors(stale_connector_names, bucket_name, repo_root)

        if healed_connectors:
            logger.info(f"Auto-healed {len(healed_connectors)} connectors. Re-checking for stale metadata...")
            latest_metadata_entries_on_gcs = _get_latest_metadata_entries_on_gcs(bucket_name)
            stale_metadata_report = _generate_stale_metadata_report(latest_metadata_versions_on_github, latest_metadata_entries_on_gcs)
            logger.info(f"After auto-heal, {len(stale_metadata_report)} connectors are still stale.")

    report_published, error_message = _publish_stale_metadata_report(
        stale_metadata_report, len(latest_metadata_versions_on_github), len(latest_metadata_entries_on_gcs)
    )
    return report_published, error_message
