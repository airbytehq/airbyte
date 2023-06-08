import pandas as pd
import json
import os

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

T = TypeVar("T")

GROUP_NAME = "connector_nightly_report"

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
