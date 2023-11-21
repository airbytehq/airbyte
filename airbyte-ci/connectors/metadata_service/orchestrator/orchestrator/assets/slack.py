#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

from dagster import OpExecutionContext, Output, asset
import pandas as pd

from orchestrator.utils.dagster_helpers import output_dataframe, OutputDataFrame

GROUP_NAME = "slack"

USER_REQUEST_CHUNK_SIZE = 2000
MAX_REQUESTS = 5

@asset(required_resource_keys={"slack"}, group_name=GROUP_NAME)
def airbyte_slack_users(context: OpExecutionContext) -> OutputDataFrame:
    """
    Return a list of all users in the airbyte slack.
    """
    if not os.getenv("SLACK_TOKEN"):
        context.log.info("Skipping Slack Users asset as SLACK_TOKEN is not set")
        return output_dataframe(pd.DataFrame())

# Ensure that a failure to send a slack message does not cause the pipeline to fail
    client = context.resources.slack.get_client()
    users_response = client.users_list(limit=2000)
    metadata = users_response.data["response_metadata"]
    users = users_response.data["members"]
    requests_count = 1

    while metadata["next_cursor"] and requests_count < MAX_REQUESTS:
        users_response = client.users_list(limit=2000, cursor=metadata["next_cursor"])
        metadata = users_response.data["response_metadata"]
        users.extend(users_response.data["members"])
        requests_count += 1

    # Convert to a dataframe of id, real_name, and email
    # Remove any deleted  or bot profiles
    users_df = pd.DataFrame(users)
    users_df = users_df[users_df["deleted"] == False]
    users_df = users_df[users_df["is_bot"] == False]
    users_df["email"] = users_df["profile"].apply(lambda x: x.get("email", None))
    users_df = users_df[["id", "real_name", "email"]]

    return output_dataframe(users_df)

