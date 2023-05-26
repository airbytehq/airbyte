# Jira

This page contains the setup guide and reference information for the Jira source connector.

## Prerequisites

- API Token
- Domain
- Email

## Setup guide

### Step 1: Obtain the Jira API Token

1. To get access to the Jira API, you need to create an API token. Follow the instructions in this [documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Step 2: Set up the Jira connector in Airbyte

1. Once you have your API token, enter it in the **API Token** field. API Token is used for Authorization to your account by BasicAuth.

2. Next, enter the **Domain** for your Jira account in the **Domain** field, e.g. `airbyteio.atlassian.net`. Note that it should not include "https://" or any trailing slashes, and the domain should include any subdomains. For more information on finding your domain, see [this Jira documentation](https://support.atlassian.com/cloud-security/docs/what-is-my-domain-url/).

3. Enter the **Email** for your Jira account which you used to generate the API token in the **Email** field. This field is used for Authorization to your account by BasicAuth.

4. Optionally, enter the list of **Projects** for which you need to replicate data, or leave it empty if you want to replicate data for all projects. To get a more detailed list of project keys, follow the instructions in this [documentation](https://docs.airbyte.com/integrations/sources/jira#how-do-i-find-my-jira-project-keys).

5. Optionally, enter the **Start Date** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: BoardIssues, IssueComments, IssueProperties, IssueRemoteLinks, IssueVotes, IssueWatchers, IssueWorklogs, Issues, PullRequests, SprintIssues. For other streams, it will replicate all data.

6. Toggle **Expand Issue Changelog** if you want to get a list of recent updates to every issue in the Issues stream.

7. Toggle **Render Issue Fields** if you want to return field values rendered in HTML format in the Issues stream.

8. Toggle **Enable Experimental Streams** if you want to enable the experimental PullRequests stream.

For more information on configuring the Jira source connector, you can refer to the [Jira documentation](https://docs.airbyte.com/integrations/sources/jira/).

## Supported sync modes

The Jira source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

## Supported Streams

This connector outputs the following full refresh streams:

[...The list of streams goes here...]

This connector outputs the following incremental streams:

[...The list of streams goes here...]

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Experimental Tables

The following tables depend on undocumented internal Jira API endpoints and are
therefore subject to stop working if those endpoints undergo major changes.
While they will not cause a sync to fail, they may not be able to pull any data.
Use the "Enable Experimental Streams" option when setting up the source to allow
or disallow these tables to be selected when configuring a connection.

* Pull Requests (currently only GitHub PRs are supported)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

## Rate Limiting & Performance

The Jira connector should not run into Jira API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## CHANGELOG

[...The Changelog goes here...]