from dagster import Output, asset, OpExecutionContext
import pandas as pd
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "connector_nightly_report"


@asset(required_resource_keys={"latest_nightly_file_blobs"}, group_name=GROUP_NAME)
def generate_nightly_report(context: OpExecutionContext) -> OutputDataFrame:
    """
    TODO
    0. Get recent 10 nightly runs
    2. Get the github action url
    1. Parse all connectors into a pass fail, not present
    2. Filter to Failed last build, and more than last build
    3. Write the report to a markdown file
    5. Message slack with report contents
    6. Look at updating badge
    """
    latest_nightly_file_blobs = context.resources.latest_nightly_file_blobs
    file_paths = [blob.name for blob in latest_nightly_file_blobs]

    file_paths_df = pd.DataFrame(file_paths)
    return output_dataframe(file_paths_df)
