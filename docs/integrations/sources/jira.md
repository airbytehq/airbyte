# Jira

This page contains the setup guide and reference information for the Jira source connector.

## Prerequisites

- API Token
- Domain
- Email

## Setup guide

### Step 1: Set up Jira

1. To get access to the Jira API you need to create an API token. Please follow the instructions in this [documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Step 2: Set up the Jira connector in Airbyte

1. Enter the **API Token** that you have created. The API Token is used for Authorization to your account by BasicAuth.
2. Enter the **Domain** for your Jira account, e.g., `airbyteio.atlassian.net`. You can find the domain in the URL when you are logged in to your Jira account.
3. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.
4. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects. You can find the project keys in your Jira account under the "Projects" section.
5. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: BoardIssues, IssueComments, IssueProperties, IssueRemoteLinks, IssueVotes, IssueWatchers, IssueWorklogs, Issues, PullRequests, SprintIssues. For other streams, it will replicate all data.
6. Toggle **Expand Issue Changelog** to get a list of recent updates to every issue in the Issues stream.
7. Toggle **Render Issue Fields** to return field values rendered in HTML format in the Issues stream.
8. Toggle **Enable Experimental Streams** to enable the experimental PullRequests stream.

## Supported sync modes

The Jira source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

## Supported Streams

[Refer to the original documentation for the list of supported streams.](https://docs.airbyte.com/integrations/sources/jira)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Experimental Tables

[Refer to the original documentation for information on experimental tables.](https://docs.airbyte.com/integrations/sources/jira#experimental-tables)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

## Rate Limiting & Performance

The Jira connector should not run into Jira API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## CHANGELOG

[Refer to the original documentation for the Changelog.](https://docs.airbyte.com/integrations/sources/jira#changelog)