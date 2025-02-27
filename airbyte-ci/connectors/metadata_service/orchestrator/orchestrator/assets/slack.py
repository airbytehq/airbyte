#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

import pandas as pd
from dagster import AutoMaterializePolicy, FreshnessPolicy, OpExecutionContext, Output, asset
from orchestrator.utils.dagster_helpers import OutputDataFrame, output_dataframe


GROUP_NAME = "slack"

USER_REQUEST_CHUNK_SIZE = 2000
MAX_REQUESTS = 5


@asset(
    group_name=GROUP_NAME,
    required_resource_keys={"slack"},
    auto_materialize_policy=AutoMaterializePolicy.eager(),
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=60 * 12),
)
def airbyte_slack_users(context: OpExecutionContext) -> OutputDataFrame:
    """
    Return a list of all users in the airbyte slack.
    """
    if not os.getenv("SLACK_TOKEN"):
        context.log.info("Skipping Slack Users asset as SLACK_TOKEN is not set")
        return None

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
