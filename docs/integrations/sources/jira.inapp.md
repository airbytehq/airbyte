## Prerequisites

- Access to a JIRA account
- [JIRA API Token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)
- JIRA Account Domain

## Setup guide

1. Enter a name for the connector.
2. Enter the **API Token** that you have created. The **API Token** is used for Authorization to your account.
2. Enter the **Domain** for your Jira account, e.g. `airbyte.atlassian.net`.
3. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account.
4. (Optional) Enter the list of **Projects** for which you need to replicate data. If empty, data from all projects will be replicated.
5. (Optional) Enter the **Start Date** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated. If empty, all data will be replicated. Note that it will be used only in the following streams: `BoardIssues`, `IssueComments`, `IssueProperties`, `IssueRemoteLinks`, `IssueVotes`, `IssueWatchers`, `IssueWorklogs`, `Issues`, `PullRequests`, `SprintIssues`. For other streams, it will replicate all data.  
9. Toggle **Expand Issue Changelog** to get a list of updates to every issue in the Issues stream. If the toggle is off, the changelog will not be pulled.
10. Toggle **Render Issue Fields** to additionally return field values rendered in HTML format in the Issues stream. Issue fields will always be returned in JSON format.
11. Toggle **Enable Experimental Streams** to enable syncing for undocumented internal JIRA API endpoints and may stop working if those enpoints undergo major changes. Currently, this only applies to the PullRequests stream. 
10. Click **Set up source**

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [JIRA](https://docs.airbyte.com/integrations/sources/jira).
