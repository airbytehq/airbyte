# Jira

This page contains the setup guide and reference information for the Jira source connector.

## Prerequisites

- API Token
- Domain
- Email

## Setup guide

### Step 1: Set up Jira

1. To get access to the Jira API, you need to create an API token. Please follow the instructions in this [documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Step 2: Set up the Jira connector in Airbyte

1. Enter the **API Token** that you have created. The **API Token** is used for authorization to your account via BasicAuth. To get your token, log in to your Jira account and click on your Profile icon in the top-right corner, then click "Settings" -> "Atlassian Account settings" -> "Security" -> "Create and manage API tokens". You can find more details in the [Jira documentation](https://confluence.atlassian.com/cloud/api-tokens-938839638.html).

2. Enter the **Domain** for your Jira account, e.g., `airbyteio.atlassian.net`. Your domain can be found in the URL of your Jira site; for example, if your Jira site URL is `https://examplecompany.atlassian.net`, your Domain would be `examplecompany.atlassian.net`.

3. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.

4. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects. To find the project keys, go to your Jira dashboard, and click on "Projects" in the left navigation panel. The project key is displayed under each project name.

5. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format `YYYY-MM-DDTHH:MM:SSZ`. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: BoardIssues, IssueComments, IssueProperties, IssueRemoteLinks, IssueVotes, IssueWatchers, IssueWorklogs, Issues, PullRequests, SprintIssues. For other streams, it will replicate all data.

6. Toggle **Expand Issue Changelog** allows you to get a list of recent updates to every issue in the Issues stream.

7. Toggle **Render Issue Fields** allows returning field values rendered in HTML format in the Issues stream.

8. Toggle **Enable Experimental Streams** enables experimental PullRequests stream.

## Supported sync modes

The Jira source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

## Supported Streams
... (Keep the Supported Streams section as-is from the original documentation) ...

## Experimental Tables
... (Keep the Experimental Tables section as-is from the original documentation) ...

## Troubleshooting
... (Keep the Troubleshooting section as-is from the original documentation) ...

## Rate Limiting & Performance
... (Keep the Rate Limiting & Performance section as-is from the original documentation) ...

## CHANGELOG
... (Keep the CHANGELOG section as-is from the original documentation) ...