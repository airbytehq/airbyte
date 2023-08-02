from dagster import Output, asset, OpExecutionContext
import pandas as pd
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "github"


@asset(required_resource_keys={"github_connectors_directory"}, group_name=GROUP_NAME)
def github_connector_folders(context):
    """
    Return a list of all the folders in the github connectors directory.
    """
    github_connectors_directory = context.resources.github_connectors_directory

    folder_names = [item.name for item in github_connectors_directory if item.type == "dir"]
    return Output(folder_names, metadata={"preview": folder_names})


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
