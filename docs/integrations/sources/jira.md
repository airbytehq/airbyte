# Jira

This page contains the setup guide and reference information for the Jira source connector.

## Prerequisites

- API Token
- Domain
- Email

## Setup guide

### Step 1: Set up Jira

1. To get access to the Jira API you need to create an API token, please follow the instructions in this [documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Step 2: Set up the Jira connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Jira** from the Source type dropdown and enter a name for this connector.
4. Enter the **API Token** that you have created. **API Token** is used for Authorization to your account by BasicAuth.
5. Enter the **Domain** for your Jira account, e.g. `airbyteio.atlassian.net`.
6. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.
7. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects.
8. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams:BoardIssues, IssueComments, IssueProperties, IssueRemoteLinks, IssueVotes, IssueWatchers, IssueWorklogs, Issues, PullRequests, SprintIssues. For other streams it will replicate all data.  
9. Toggle **Expand Issue Changelog** allows you to get a list of recent updates to every issue in the Issues stream.
10. Toggle **Render Issue Fields** allows returning field values rendered in HTML format in the Issues stream.
11. Toggle **Enable Experimental Streams** enables experimental PullRequests stream.

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

* [Application roles](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-get)
* [Avatars](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get)
* [Boards](https://developer.atlassian.com/cloud/jira/software/rest/api-group-other-operations/#api-agile-1-0-board-get)
* [Dashboards](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get)
* [Filters](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get)
* [Filter sharing](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get)
* [Groups](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-groups-picker-get)
* [Issue fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get)
* [Issue field configurations](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfiguration-get)
* [Issue custom field contexts](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get)
* [Issue link types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/#api-rest-api-3-issuelinktype-get)
* [Issue navigator settings](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-navigator-settings/#api-rest-api-3-settings-columns-get)
* [Issue notification schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/#api-rest-api-3-notificationscheme-get)
* [Issue priorities](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/#api-rest-api-3-priority-get)
* [Issue properties](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-propertykey-get)
* [Issue remote links](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get)
* [Issue resolutions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-rest-api-3-resolution-search-get)
* [Issue security schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-security-schemes/#api-rest-api-3-issuesecurityschemes-get)
* [Issue type schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/#api-rest-api-3-issuetypescheme-get)
* [Issue type screen schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/#api-rest-api-3-issuetypescreenscheme-get)
* [Issue votes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-votes/#api-group-issue-votes)
* [Issue watchers](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get)
* [Jira settings](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-settings/#api-rest-api-3-application-properties-get)
* [Labels](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-labels/#api-rest-api-3-label-get)
* [Permissions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/#api-rest-api-3-mypermissions-get)
* [Permission schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/#api-rest-api-3-permissionscheme-get)
* [Projects](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get)
* [Project avatars](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-avatars/#api-rest-api-3-project-projectidorkey-avatars-get)
* [Project categories](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-categories/#api-rest-api-3-projectcategory-get)
* [Project components](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-project-projectidorkey-component-get)
* [Project email](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-email/#api-rest-api-3-project-projectid-email-get)
* [Project permission schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-permission-schemes/#api-group-project-permission-schemes)
* [Project types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-types/#api-rest-api-3-project-type-get)
* [Project versions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/#api-rest-api-3-project-projectidorkey-version-get)
* [Screens](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get)
* [Screen tabs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/#api-rest-api-3-screens-screenid-tabs-get)
* [Screen tab fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get)
* [Screen schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/#api-rest-api-3-screenscheme-get)
* [Sprints](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-sprint-get)
* [Time tracking](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-time-tracking/#api-rest-api-3-configuration-timetracking-list-get)
* [Users](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-search-get)
* [UsersGroupsDetailed](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-user-get)
* [Workflows](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-search-get)
* [Workflow schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-get)
* [Workflow statuses](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-statuses/#api-rest-api-3-status-get)
* [Workflow status categories](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-status-categories/#api-rest-api-3-statuscategory-get)

This connector outputs the following incremental streams:

* [Board issues](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-issue-get)
* [Issue comments](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get)
* [Issue worklogs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get)
* [Issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get)
* [Sprint issues](https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-rest-agile-1-0-sprint-sprintid-issue-get)

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

| Version | Date       | Pull Request                                               | Subject                                                                                                                 |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| 0.3.12  | 2023-06-01 | [\#26652](https://github.com/airbytehq/airbyte/pull/26652) | Expand on `leads` for `projects` stream |
| 0.3.11  | 2023-06-01 | [\#26906](https://github.com/airbytehq/airbyte/pull/26906) | Handle project permissions error                                                                                        |
| 0.3.10  | 2023-05-26 | [\#26652](https://github.com/airbytehq/airbyte/pull/26652) | Fixed bug when `board` doesn't support `sprints`                                                                        |
| 0.3.9   | 2023-05-16 | [\#26114](https://github.com/airbytehq/airbyte/pull/26114) | Update fields info in docs and spec, update to latest airbyte-cdk                                                       |
| 0.3.8   | 2023-05-04 | [\#25798](https://github.com/airbytehq/airbyte/pull/25798) | Add sprint info to `sprint_issues` and `sprints` streams for team-managed projects                                      |
| 0.3.7   | 2023-04-18 | [\#25275](https://github.com/airbytehq/airbyte/pull/25275) | Add missing types to issues json schema                                                                                 |
| 0.3.6   | 2023-04-10 | [\#24636](https://github.com/airbytehq/airbyte/pull/24636) | Removed Connector Domain Pattern from Spec                                                                              |
| 0.3.5   | 2023-04-05 | [\#24890](https://github.com/airbytehq/airbyte/pull/24890) | Fix streams "IssuePropertyKeys", "ScreenTabFields"                                                                      |
| 0.3.4   | 2023-02-14 | [\#23006](https://github.com/airbytehq/airbyte/pull/23006) | Remove caching for `Issues` stream                                                                                      |
| 0.3.3   | 2023-01-04 | [\#20739](https://github.com/airbytehq/airbyte/pull/20739) | fix: check_connection fails if no projects are defined                                                                  |
| 0.3.2   | 2022-12-23 | [\#20859](https://github.com/airbytehq/airbyte/pull/20859) | Fixed pagination for streams `issue_remote_links`, `sprints`                                                            |
| 0.3.1   | 2022-12-14 | [\#20128](https://github.com/airbytehq/airbyte/pull/20128) | Improved code to become beta                                                                                            |
| 0.3.0   | 2022-11-03 | [\#18901](https://github.com/airbytehq/airbyte/pull/18901) | Adds UserGroupsDetailed schema, fix Incremental normalization, add Incremental support for IssueComments, IssueWorklogs |
| 0.2.23  | 2022-10-28 | [\#18505](https://github.com/airbytehq/airbyte/pull/18505) | Correcting `max_results` bug introduced in connector stream                                                             |
| 0.2.22  | 2022-10-03 | [\#16944](https://github.com/airbytehq/airbyte/pull/16944) | Adds support for `max_results` to `users` stream                                                                        |
| 0.2.21  | 2022-07-28 | [\#15135](https://github.com/airbytehq/airbyte/pull/15135) | Adds components to `fields` object on `issues` stream                                                                   |
| 0.2.20  | 2022-05-25 | [\#13202](https://github.com/airbytehq/airbyte/pull/13202) | Adds resolutiondate to `fields` object on `issues` stream                                                               |
| 0.2.19  | 2022-05-04 | [\#10835](https://github.com/airbytehq/airbyte/pull/10835) | Change description for array fields                                                                                     |
| 0.2.18  | 2021-12-23 | [\#7378](https://github.com/airbytehq/airbyte/pull/7378)   | Adds experimental endpoint Pull Request                                                                                 |
| 0.2.17  | 2021-12-23 | [\#9079](https://github.com/airbytehq/airbyte/pull/9079)   | Update schema for `filters` stream + fix fetching `filters` stream                                                      |
| 0.2.16  | 2021-12-21 | [\#8999](https://github.com/airbytehq/airbyte/pull/8999)   | Update connector fields title/description                                                                               |
| 0.2.15  | 2021-11-01 | [\#7398](https://github.com/airbytehq/airbyte/pull/7398)   | Add option to render fields in HTML format and fix sprint_issue ids                                                     |
| 0.2.14  | 2021-10-27 | [\#7408](https://github.com/airbytehq/airbyte/pull/7408)   | Fix normalization step error. Fix schemas. Fix `acceptance-test-config.yml`. Fix `streams.py`.                          |
| 0.2.13  | 2021-10-20 | [\#7222](https://github.com/airbytehq/airbyte/pull/7222)   | Source Jira: Make recently added configs optional for backwards compatibility                                           |
| 0.2.12  | 2021-10-19 | [\#6621](https://github.com/airbytehq/airbyte/pull/6621)   | Add Board, Epic, and Sprint streams                                                                                     |
| 0.2.11  | 2021-09-02 | [\#6523](https://github.com/airbytehq/airbyte/pull/6523)   | Add cache and more streams \(boards and sprints\)                                                                       |
| 0.2.9   | 2021-07-28 | [\#5426](https://github.com/airbytehq/airbyte/pull/5426)   | Changed cursor field from fields.created to fields.updated for Issues stream. Made Issues worklogs stream full refresh. |
| 0.2.8   | 2021-07-28 | [\#4947](https://github.com/airbytehq/airbyte/pull/4947)   | Source Jira: fixing schemas accordinately to response.                                                                  |
| 0.2.7   | 2021-07-19 | [\#4817](https://github.com/airbytehq/airbyte/pull/4817)   | Fixed `labels` schema properties issue.                                                                                 |
| 0.2.6   | 2021-06-15 | [\#4113](https://github.com/airbytehq/airbyte/pull/4113)   | Fixed `user` stream with the correct endpoint and query param.                                                          |
| 0.2.5   | 2021-06-09 | [\#3973](https://github.com/airbytehq/airbyte/pull/3973)   | Added `AIRBYTE_ENTRYPOINT` in base Docker image for Kubernetes support.                                                 |
| 0.2.4   |            |                                                            | Implementing base\_read acceptance test dived by stream groups.                                                         |
| 0.2.3   |            |                                                            | Implementing incremental sync. Migrated to airbyte-cdk. Adding all available entities in Jira Cloud.                    |

