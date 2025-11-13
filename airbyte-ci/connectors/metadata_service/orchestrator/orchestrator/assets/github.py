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
