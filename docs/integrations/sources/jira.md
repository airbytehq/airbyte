# Jira Source Connector

This page contains the setup guide and reference information for the Jira source connector.

## Prerequisites

- API Token
- Domain
- Email

## Setup guide

1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.

2. On the source setup page, select **Jira** from the Source type dropdown and enter a name for this connector.

3. To generate the **API Token**, follow the instructions in this [Jira documentation](https://confluence.atlassian.com/cloud/api-tokens-938839638.html). Store the API Token safely as it will be used for Authorization to your account by BasicAuth. 

4. Enter the **API Token** generated in the previous step into the API Token field.

5. Enter the **Domain** for your Jira account, e.g., `airbyteio.atlassian.net`. Note that it should not include "https://" or any trailing slashes, and the domain should include any subdomains. For more information on finding your domain, see [this Jira documentation](https://support.atlassian.com/cloud-security/docs/what-is-my-domain-url/).

6. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.

7. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects. To get a more detailed list of project keys, follow the instructions in this [documentation](https://docs.airbyte.com/integrations/sources/jira#how-do-i-find-my-jira-project-keys).

8. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: BoardIssues, IssueComments, IssueProperties, IssueRemoteLinks, IssueVotes, IssueWatchers, IssueWorklogs, Issues, PullRequests, and SprintIssues. For other streams, it will replicate all data.

9. Toggle **Expand Issue Changelog** options to get a list of recent updates to every issue in the Issues stream.

10. Toggle **Render Issue Fields** options to return field values rendered in HTML format in the Issues stream.

11. Toggle **Enable Experimental Streams** option to enable experimental PullRequests stream.

For more information on configuring the Jira source connector, you can refer to the [Jira documentation](https://docs.airbyte.com/integrations/sources/jira/).

## Supported sync modes

The Jira source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

[Changelog and Supported Stream sections unchanged]