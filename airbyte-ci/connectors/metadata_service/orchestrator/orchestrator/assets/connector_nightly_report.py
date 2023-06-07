from dagster import Output, asset, OpExecutionContext
import pandas as pd
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "connector_nightly_report"


@asset(required_resource_keys={"latest_nightly_file_blobs"}, group_name=GROUP_NAME)
def generate_nightly_report(context: OpExecutionContext) -> OutputDataFrame:
    """
    """
    latest_nightly_file_blobs = context.resources.latest_nightly_file_blobs
    file_paths = [blob.name for blob in latest_nightly_file_blobs]

    file_paths_df = pd.DataFrame(file_paths)
    return output_dataframe(file_paths_df)
