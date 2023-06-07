from dagster import Output, asset, OpExecutionContext, MetadataValue
import pandas as pd
import json
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe
from orchestrator.models.ci_report import ConnectorNightlyReport, ConnectorPipelineReport
from orchestrator.config import REPORT_FOLDER, REGISTRIES_FOLDER, CONNECTORS_PATH, CONNECTOR_REPO_NAME, NIGHTLY_FOLDER, NIGHTLY_COMPLETE_REPORT_FILE_NAME, NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME
from orchestrator.templates.render import (
    render_connector_nightly_report_md,
)

GROUP_NAME = "connector_nightly_report"

# HELPERS

def blob_to_model(blob, Model):
    report = blob.download_as_string()
    file_path = blob.name

    # parse json
    report_json = json.loads(report)

    # parse into pydandic model
    report_model = Model(file_path=file_path, **report_json)

    return report_model

def blobs_to_typed_df(blobs, Model):
    # read each blob into a model
    models = [blob_to_model(blob, Model) for blob in blobs]

    # convert to dataframe
    models_df = pd.DataFrame(models)


    return models_df

def get_latest_reports(blobs, number_to_get):
    # Given that the name of these blobs is in the following format airbyte-ci/connectors/test/{unixtimestamp}/{gitsha}/complete.json
    # We can sort by the name to get the latest 10 nightly runs
    # todo write test for this
    latest_nightly_complete_file_blobs = sorted(blobs, key=lambda blob: blob.name, reverse=True)[:number_to_get]
    return latest_nightly_complete_file_blobs

def get_relevant_test_outputs(latest_nightly_test_output_file_blobs, latest_nightly_complete_file_blobs):
    # get all parent file paths of latest_nightly_complete_file_blobs by removing complete.json from the end of the file path
    latest_nightly_complete_file_paths = [
        blob.name.replace(f"/{NIGHTLY_COMPLETE_REPORT_FILE_NAME}", "") for blob in latest_nightly_complete_file_blobs
        for blob
        in latest_nightly_complete_file_blobs
    ]

    # filter latest_nightly_test_output_file_blobs to only those that have a parent file path in latest_nightly_complete_file_paths
    relevant_nightly_test_output_file_blobs = [
        blob
        for blob
        in latest_nightly_test_output_file_blobs
        if any([parent_file_path in blob.name for parent_file_path in latest_nightly_complete_file_paths])
    ]

    return relevant_nightly_test_output_file_blobs

def compute_connector_nightly_report_history(nightly_report_complete_df, nightly_report_test_output_df):

    # Add a new column to nightly_report_complete_df that is the parent file path of the complete.json file
    nightly_report_complete_df["parent_file_path"] = nightly_report_complete_df["file_path"].apply(lambda file_path: file_path.replace(f"/{NIGHTLY_COMPLETE_REPORT_FILE_NAME}", ""))

    # Add a new column to nightly_report_test_output_df that is the nightly report file path that the test output belongs to
    # The nightly parent_file_path will be in the format airbyte-ci/connectors/test/{unixtimestamp}/{gitsha}/complete.json
    # The nightly test output file path will be in the format airbyte-ci/connectors/test/{unixtimestamp}/{gitsha}/{connector_name}/{connector_version}/output.json
    # So the best way to do this is to check and see if the nightly parent_file_path is in the nightly test output file path
    nightly_report_test_output_df["nightly_path"] = nightly_report_test_output_df["file_path"].apply(lambda file_path: [parent_file_path for parent_file_path in nightly_report_complete_df["parent_file_path"] if parent_file_path in file_path][0])

    # Create a new dataframe thats row is the `nightly_report_test_output_df.connector_technical_name`, the columns are the `nightly_report_complete_df.parent_file_path`, and the values are `nightly_report_test_output_df.success`
    # This will be a matrix of connector success/failure for each nightly run
    matrix_df = nightly_report_test_output_df.pivot(index="connector_technical_name", columns="nightly_path", values="success")

    # Sort columns by name
    matrix_df = matrix_df.reindex(sorted(matrix_df.columns), axis=1)

    # import pdb; pdb.set_trace()

    return matrix_df

# ASSETS


@asset(required_resource_keys={"latest_nightly_complete_file_blobs", "latest_nightly_test_output_file_blobs"}, group_name=GROUP_NAME)
def generate_nightly_report(context: OpExecutionContext) -> Output[pd.DataFrame]:
    """
    TODO
    3. Write the report to a markdown file
    5. Message slack with report contents
    6. Write to badge locations with same data
    """
    latest_nightly_complete_file_blobs = context.resources.latest_nightly_complete_file_blobs
    latest_nightly_test_output_file_blobs = context.resources.latest_nightly_test_output_file_blobs

    # Given that the name of these blobs is in the following format airbyte-ci/connectors/test/{unixtimestamp}/{gitsha}/complete.json
    # We can sort by the name to get the latest 10 nightly runs
    # TODO write test for this
    latest_10_nightly_complete_file_blobs = get_latest_reports(latest_nightly_complete_file_blobs, 10)
    relevant_nightly_test_output_file_blobs = get_relevant_test_outputs(latest_nightly_test_output_file_blobs, latest_10_nightly_complete_file_blobs)

    nightly_report_complete_df = blobs_to_typed_df(latest_10_nightly_complete_file_blobs, ConnectorNightlyReport)
    nightly_report_test_output_df = blobs_to_typed_df(relevant_nightly_test_output_file_blobs, ConnectorPipelineReport)

    nightly_report_connector_matrix_df = compute_connector_nightly_report_history(nightly_report_complete_df, nightly_report_test_output_df)

    nightly_report_complete_md = render_connector_nightly_report_md(nightly_report_connector_matrix_df, nightly_report_complete_df)

    return Output(nightly_report_connector_matrix_df, metadata={"count": len(nightly_report_connector_matrix_df), "preview": MetadataValue.md(nightly_report_complete_md)})
