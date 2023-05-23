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

1. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.

2. On the source setup page, select **Jira** from the Source type dropdown and enter a name for this connector.

3. Enter the **API Token** that you have created. **API Token** is used for Authorization to your account by BasicAuth.

4. Enter the **Domain** for your Jira account, e.g. `airbyteio.atlassian.net`. Note that it should not include "https://" or any trailing slashes, and the domain should include any subdomains. For more information on finding your domain, see [this Jira documentation](https://support.atlassian.com/cloud-security/docs/what-is-my-domain-url/).

5. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.

6. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects. To get a more detailed list of project keys, follow the instructions in this [documentation](https://docs.airbyte.com/integrations/sources/jira#how-do-i-find-my-jira-project-keys).

7. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: BoardIssues, IssueComments, IssueProperties, IssueRemoteLinks, IssueVotes, IssueWatchers, IssueWorklogs, Issues, PullRequests, SprintIssues. For other streams, it will replicate all data.

8. Toggle **Expand Issue Changelog** options to get a list of recent updates to every issue in the Issues stream.

9. Toggle **Render Issue Fields** options to return field values rendered in HTML format in the Issues stream.

10. Toggle **Enable Experimental Streams** option to enable experimental PullRequests stream.

For more information on configuring the Jira source connector, you can refer to the [Jira documentation](https://docs.airbyte.com/integrations/sources/jira/).