import pandas as pd
import json
import os
import re
from datetime import datetime

from dagster import Output, asset, OpExecutionContext, MetadataValue
from google.cloud import storage
from typing import List, Type, TypeVar

from orchestrator.ops.slack import send_slack_webhook
from orchestrator.models.ci_report import ConnectorNightlyReport, ConnectorPipelineReport
from orchestrator.config import (
    NIGHTLY_COMPLETE_REPORT_FILE_NAME,
)
from orchestrator.templates.render import (
    render_connector_nightly_report_md,
)
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


T = TypeVar("T")

GROUP_NAME = "connector_test_report"

# HELPERS


def json_blob_to_model(blob: storage.Blob, Model: Type[T]) -> T:
    report = blob.download_as_string()
    file_path = blob.name

    # parse json
    report_json = json.loads(report)

    # parse into pydandic model
    report_model = Model(file_path=file_path, **report_json)

    return report_model


def blobs_to_typed_df(blobs: List[storage.Blob], Model: Type[T]) -> pd.DataFrame:
    # read each blob into a model
    models = [json_blob_to_model(blob, Model) for blob in blobs]

    # convert to dataframe
    models_df = pd.DataFrame(models)

    return models_df


def get_latest_reports(blobs: List[storage.Blob], number_to_get: int) -> List[storage.Blob]:
    """
    Get the latest n reports from a list of blobs

    Args:
        blobs(List[storage.Blob]): A list of nightly report complete.json blobs
        number_to_get(int): The number of latest reports to get

    Returns:
        A list of blobs
    """

    # We can sort by the name to get the latest 10 nightly runs
    # As the nightly reports have the timestamp in the path by design
    # e.g. airbyte-ci/connectors/test/nightly_builds/master/1686132340/05d686eb0eee2888f6af010b385a4ede330a886b/complete.json
    latest_nightly_complete_file_blobs = sorted(blobs, key=lambda blob: blob.name, reverse=True)[:number_to_get]
    return latest_nightly_complete_file_blobs


def get_relevant_test_outputs(
    latest_nightly_test_output_file_blobs: List[storage.Blob], latest_nightly_complete_file_blobs: List[storage.Blob]
) -> List[storage.Blob]:
    """
    Get the relevant test output blobs that are in the same folder to any latest nightly runs

    Args:
        latest_nightly_test_output_file_blobs (List[storage.Blob]): A list of connector report output.json blobs
        latest_nightly_complete_file_blobs (List[storage.Blob]): A list of nightly report complete.json blobs

    Returns:
        List[storage.Blob]: A list of relevant test output blobs
    """
    # get all parent file paths of latest_nightly_complete_file_blobs by removing complete.json from the end of the file path
    latest_nightly_complete_file_paths = [
        blob.name.replace(f"/{NIGHTLY_COMPLETE_REPORT_FILE_NAME}", "") for blob in latest_nightly_complete_file_blobs
    ]

    # filter latest_nightly_test_output_file_blobs to only those that have a parent file path in latest_nightly_complete_file_paths
    # This is to filter out incomplete, or unrelated/old connector test output files
    relevant_nightly_test_output_file_blobs = [
        blob
        for blob in latest_nightly_test_output_file_blobs
        if any([parent_prefix in blob.name for parent_prefix in latest_nightly_complete_file_paths])
    ]

    return relevant_nightly_test_output_file_blobs


def compute_connector_nightly_report_history(
    nightly_report_complete_df: pd.DataFrame, nightly_report_test_output_df: pd.DataFrame
) -> pd.DataFrame:
    # Add a new column to nightly_report_complete_df that is the parent file path of the complete.json file
    nightly_report_complete_df["parent_prefix"] = nightly_report_complete_df["file_path"].apply(
        lambda file_path: file_path.replace(f"/{NIGHTLY_COMPLETE_REPORT_FILE_NAME}", "")
    )

    # Add a new column to nightly_report_test_output_df that is the nightly report file path that the test output belongs to
    nightly_report_test_output_df["nightly_path"] = nightly_report_test_output_df["file_path"].apply(
        lambda file_path: [parent_prefix for parent_prefix in nightly_report_complete_df["parent_prefix"] if parent_prefix in file_path][0]
    )

    # This will be a matrix of connector success/failure for each nightly run
    matrix_df = nightly_report_test_output_df.pivot(index="connector_technical_name", columns="nightly_path", values="success")

    # Sort columns by name
    matrix_df = matrix_df.reindex(sorted(matrix_df.columns), axis=1)

    return matrix_df


# ASSETS


@asset(required_resource_keys={"latest_nightly_complete_file_blobs", "latest_nightly_test_output_file_blobs"}, group_name=GROUP_NAME)
def generate_nightly_report(context: OpExecutionContext) -> Output[pd.DataFrame]:
    """
    Generate the Connector Nightly Report from the latest 10 nightly runs
    """
    latest_nightly_complete_file_blobs = context.resources.latest_nightly_complete_file_blobs
    latest_nightly_test_output_file_blobs = context.resources.latest_nightly_test_output_file_blobs

    latest_10_nightly_complete_file_blobs = get_latest_reports(latest_nightly_complete_file_blobs, 10)
    relevant_nightly_test_output_file_blobs = get_relevant_test_outputs(
        latest_nightly_test_output_file_blobs, latest_10_nightly_complete_file_blobs
    )

    nightly_report_complete_df = blobs_to_typed_df(latest_10_nightly_complete_file_blobs, ConnectorNightlyReport)
    nightly_report_test_output_df = blobs_to_typed_df(relevant_nightly_test_output_file_blobs, ConnectorPipelineReport)

    nightly_report_connector_matrix_df = compute_connector_nightly_report_history(nightly_report_complete_df, nightly_report_test_output_df)

    nightly_report_complete_md = render_connector_nightly_report_md(nightly_report_connector_matrix_df, nightly_report_complete_df)

    slack_webhook_url = os.getenv("NIGHTLY_REPORT_SLACK_WEBHOOK_URL")
    if slack_webhook_url:
        send_slack_webhook(slack_webhook_url, nightly_report_complete_md)

    return Output(
        nightly_report_connector_matrix_df,
        metadata={"count": len(nightly_report_connector_matrix_df), "preview": MetadataValue.md(nightly_report_complete_md)},
    )

@asset(required_resource_keys={"gcp_gcs_client"}, group_name=GROUP_NAME)
def last_10_connector_test_results(context: OpExecutionContext) -> OutputDataFrame:
    # TODO pull into resources
    gcp_gcs_client = context.resources.gcp_gcs_client
    ci_report_bucket = os.getenv("CI_REPORT_BUCKET")

    prefix = "airbyte-ci/connectors/test"
    branch = "master"
    suffix = "output.json"

    bucket = gcp_gcs_client.get_bucket(ci_report_bucket)
    gcs_file_blobs = bucket.list_blobs(prefix=prefix)

    # regex that matches any path that contains the branch name and ends with output.json
    # e.g. airbyte-ci/connectors/test/somerandomfoler/master/connectorname/connectorversion/gitsha/output.json
    # TODO make all work off regex
    regex = f".*{branch}.*{suffix}$"



    # filter gcs_file_blobs to only those that match the regex
    gcs_file_blobs = [blob for blob in gcs_file_blobs if re.match(regex, blob.name)]

    # This is an example path a blob that match the regex airbyte-ci/connectors/test/nightly_builds/master/1686249301/61a6f8ed68cbeaa8b8b1ff4e64496d989826fd5e/source-strava/0.1.4/output.json
    # We want to extract the following information from the path
    # 1. connector name (source-strava)
    # 2. connector version (0.1.4)
    # 3. timestamp (1686249301)
    # And add them as columns to the dataframe
    # note that we should only pay attention to the end of the file path, not the beginning
    # because the beginning of the file path is not consistent 1686249301/61a6f8ed68cbeaa8b8b1ff4e64496d989826fd5e/source-strava/0.1.4/output.json
    report_status = [
        {
            "connector_name": blob.name.split("/")[-3],
            "connector_version": blob.name.split("/")[-2],
            "timestamp": blob.name.split("/")[-5],
            "blob": blob,
            # "success": json_blob_to_model(blob, ConnectorPipelineReport).success,
        }
        for blob in gcs_file_blobs
    ]

    # group by connector name and only keep the latest 10 timestamps
    report_status = (
        pd.DataFrame(report_status)
        .groupby("connector_name")
        .apply(lambda x: x.sort_values("timestamp", ascending=False).head(10))
        .reset_index(drop=True)
    )

    # add an entry for each connectors timestamp that is whether the test passed or failed
    report_status["model"] = report_status["blob"].apply(lambda blob: json_blob_to_model(blob, ConnectorPipelineReport))
    report_status["success"] = report_status["model"].apply(lambda model: model.success)
    report_status["gha_workflow_run_url"] = report_status["model"].apply(lambda model: model.gha_workflow_run_url)

    # Drop the blob column
    report_status = report_status.drop(columns=["blob", "model"])

    # TODO
    # 1. add a persist summary asset (we will need the connectors icon url for this)
    # 2. add a persist badge asset (we will need the connectors icon url for this)

    return output_dataframe(report_status)

@asset(required_resource_keys={"registry_report_directory_manager"}, group_name=GROUP_NAME)
def persist_connectors_test_summary_files(context: OpExecutionContext, last_10_connector_test_results: OutputDataFrame) -> OutputDataFrame:
    registry_report_directory_manager = context.resources.registry_report_directory_manager

    # We want to create a dataframe per connector_name that contains the following columns
    # 1. date
    # 2. connector_version
    # 3. success
    # 4. gha_workflow_run_url
    # so that we can create a summary file for each connector
    # for connector_name, connector_df in last_10_connector_test_results.items():
    metadata = {}
    all_connector_names = last_10_connector_test_results["connector_name"].unique()
    for connector_name in all_connector_names:
        all_connector_test_results = last_10_connector_test_results[last_10_connector_test_results["connector_name"] == connector_name]
        connector_test_summary = all_connector_test_results[["timestamp", "connector_version", "success", "gha_workflow_run_url"]]

        # Order by timestamp descending
        connector_test_summary = connector_test_summary.sort_values("timestamp", ascending=False)

        # convert unix timestamp to iso date
        connector_test_summary["date"] = connector_test_summary["timestamp"].apply(lambda timestamp: datetime.fromtimestamp(int(timestamp)).isoformat())

        # drop the timestamp column
        connector_test_summary = connector_test_summary.drop(columns=["timestamp"])
        report_file_name = f"test_summary/{connector_name}"
        markdown_string = connector_test_summary.to_markdown()

        # add to metadata
        metadata[report_file_name] = MetadataValue.md(markdown_string)
        # json_file_handle = registry_report_directory_manager.write_data(json_string.encode(), ext="json", key=report_file_name)

    return Output(
        value=last_10_connector_test_results,
        metadata=metadata,
    )

