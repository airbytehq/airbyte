import pandas as pd
import hashlib
import base64

from dagster import Output, asset, OpExecutionContext
from github import Repository

from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "github"


def _get_md5_of_github_file(context: OpExecutionContext, github_connector_repo: Repository, path: str) -> str:
    """
    Return the md5 hash of a file in the github repo.
    """
    context.log.info(f"retrieving contents of {path}")
    file_contents = github_connector_repo.get_contents(path)

    # calculate the md5 hash of the file contents
    context.log.info(f"calculating md5 hash of {path}")
    md5_hash = hashlib.md5()
    md5_hash.update(file_contents.decoded_content)
    base_64_value = base64.b64encode(md5_hash.digest()).decode("utf8")
    return base_64_value


@asset(required_resource_keys={"github_connectors_directory"}, group_name=GROUP_NAME)
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
        metadata_path: _get_md5_of_github_file(context, github_connector_repo, metadata_path)
        for metadata_path in github_connectors_metadata_files
    }

    return Output(metadata_file_paths, metadata={"preview": metadata_file_paths})


@asset(required_resource_keys={"latest_metadata_file_blobs"}, group_name=GROUP_NAME)
def stale_gcs_latest_metadata_file(context, github_metadata_file_md5s: dict) -> OutputDataFrame:
    """
    Return a list of all metadata files in the github repo and denote whether they are stale or not.

    Stale means that the file in the github repo is not in the latest metadata file blobs.
    """
    latest_gcs_metadata_file_blobs = context.resources.latest_metadata_file_blobs

    latest_gcs_metadata_md5s = {blob.md5_hash: blob.name for blob in latest_gcs_metadata_file_blobs}

    stale_report = [
        {
            "github_path": github_path,
            "stale": latest_gcs_metadata_md5s.get(github_md5) is None,
            "github_md5": github_md5,
            "gcs_md5": latest_gcs_metadata_md5s.get(github_md5),
            "gcs_path": latest_gcs_metadata_md5s.get(github_md5),
        }
        for github_path, github_md5 in github_metadata_file_md5s.items()
    ]

    stale_metadata_files_df = pd.DataFrame(stale_report)

    # sort by stale true to false, then by github_path
    stale_metadata_files_df = stale_metadata_files_df.sort_values(
        by=["stale", "github_path"],
        ascending=[False, True],
    )
    stale_metadata_files_df.replace({True: "🚨 YES!!!", False: "No"}, inplace=True)

    # TODO (ben) add schedule and if stale exist report to slack
    # Waiting on: https://github.com/airbytehq/airbyte/pull/28759

    return output_dataframe(stale_metadata_files_df)


@asset(required_resource_keys={"github_connector_nightly_workflow_successes"}, group_name=GROUP_NAME)
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
