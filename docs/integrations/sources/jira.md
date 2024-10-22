# Jira

<HideInUI>

This page contains the setup guide and reference information for the [Jira](https://developer.atlassian.com/cloud/jira/platform/) source connector.

</HideInUI>

## Prerequisites

- API Token
- Domain
- Email

## Setup guide

### Step 1: Set up Jira

1. To get access to the Jira API you need to create an API token, please follow the instructions in this [documentation](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/).

### Step 2: Set up the Jira connector in Airbyte

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Jira from the Source type dropdown.
4. Enter a name for the Jira connector.
5. Enter the **API Token** that you have created. **API Token** is used for Authorization to your account by BasicAuth.
6. Enter the **Domain** for your Jira account, e.g. `airbyteio.atlassian.net`.
7. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.
8. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects.
9. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: Board Issues, Issue Comments, Issue Properties, Issue Remote Links, Issue Votes, Issue Watchers, Issue Worklogs, Issues, Pull Requests, Sprint Issues. For other streams it will replicate all data.

<!-- /env:cloud -->

<!-- env:oss -->
#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Jira from the Source type dropdown.
4. Enter a name for the Jira connector.
5. Enter the **API Token** that you have created. **API Token** is used for Authorization to your account by BasicAuth.
6. Enter the **Domain** for your Jira account, e.g. `airbyteio.atlassian.net`.
7. Enter the **Email** for your Jira account which you used to generate the API token. This field is used for Authorization to your account by BasicAuth.
8. Enter the list of **Projects (Optional)** for which you need to replicate data, or leave it empty if you want to replicate data for all projects.
9. Enter the **Start Date (Optional)** from which you'd like to replicate data for Jira in the format YYYY-MM-DDTHH:MM:SSZ. All data generated after this date will be replicated, or leave it empty if you want to replicate all data. Note that it will be used only in the following streams: Board Issues, Issue Comments, Issue Properties, Issue Remote Links, Issue Votes, Issue Watchers, Issue Worklogs, Issues, Pull Requests, Sprint Issues. For other streams it will replicate all data.

<!-- /env:oss -->

## Supported sync modes

The Jira source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following full refresh streams:

- [Application roles](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-get)
- [Avatars](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get)
- [Boards](https://developer.atlassian.com/cloud/jira/software/rest/api-group-other-operations/#api-agile-1-0-board-get)
- [Dashboards](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get)
- [Filters](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get)
- [Filter sharing](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get)
- [Groups](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-groups-picker-get)
- [Issue fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get)
- [Issue field configurations](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfiguration-get)
- [Issue custom field contexts](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get)
- [Issue custom field options](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-options/#api-rest-api-3-field-fieldid-context-contextid-option-get)
- [Issue link types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/#api-rest-api-3-issuelinktype-get)
- [Issue navigator settings](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-navigator-settings/#api-rest-api-3-settings-columns-get)
- [Issue notification schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/#api-rest-api-3-notificationscheme-get)
- [Issue priorities](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/#api-rest-api-3-priority-get)
- [Issue properties](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-propertykey-get)
- [Issue remote links](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get)
- [Issue resolutions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-rest-api-3-resolution-search-get)
- [Issue security schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-security-schemes/#api-rest-api-3-issuesecurityschemes-get)
- [Issue transitions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-get)
- [Issue type schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/#api-rest-api-3-issuetypescheme-get)
- [Issue type screen schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/#api-rest-api-3-issuetypescreenscheme-get)
- [Issue types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/#api-group-issue-types)
- [Issue votes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-votes/#api-group-issue-votes)
- [Issue watchers](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get)
- [Jira settings](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-jira-settings/#api-rest-api-3-application-properties-get)
- [Labels](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-labels/#api-rest-api-3-label-get)
- [Permissions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permissions/#api-rest-api-3-mypermissions-get)
- [Permission schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-permission-schemes/#api-rest-api-3-permissionscheme-get)
- [Projects](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get)
- [Project avatars](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-avatars/#api-rest-api-3-project-projectidorkey-avatars-get)
- [Project categories](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-categories/#api-rest-api-3-projectcategory-get)
- [Project components](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-project-projectidorkey-component-get)
- [Project email](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-email/#api-rest-api-3-project-projectid-email-get)
- [Project permission schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-permission-schemes/#api-group-project-permission-schemes)
- [Project roles](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-roles#api-rest-api-3-role-get)
- [Project types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-types/#api-rest-api-3-project-type-get)
- [Project versions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-versions/#api-rest-api-3-project-projectidorkey-version-get)
- [Screens](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screens/#api-rest-api-3-screens-get)
- [Screen tabs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/#api-rest-api-3-screens-screenid-tabs-get)
- [Screen tab fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get)
- [Screen schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/#api-rest-api-3-screenscheme-get)
- [Sprints](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-sprint-get)
- [Time tracking](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-time-tracking/#api-rest-api-3-configuration-timetracking-list-get)
- [Users](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-search-get)
- [UsersGroupsDetailed](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-rest-api-3-user-get)
- [Workflows](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-search-get)
- [Workflow schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-get)
- [Workflow statuses](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-statuses/#api-rest-api-3-status-get)
- [Workflow status categories](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-status-categories/#api-rest-api-3-statuscategory-get)

This connector outputs the following incremental streams:

- [Board issues](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-rest-agile-1-0-board-boardid-issue-get)
- [Issue comments](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get)
- [Issue worklogs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get)
- [Issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get)
- [Sprint issues](https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-rest-agile-1-0-sprint-sprintid-issue-get)
- [PullRequests](https://docs.airbyte.com/integrations/sources/jira#experimental-tables)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Entity-Relationship Diagram (ERD)
<EntityRelationshipDiagram></EntityRelationshipDiagram>

## Experimental Tables

The following tables depend on undocumented internal Jira API endpoints and are
therefore subject to stop working if those endpoints undergo major changes.
While they will not cause a sync to fail, they may not be able to pull any data.
Use the "Enable Experimental Streams" option when setting up the source to allow
or disallow these tables to be selected when configuring a connection.

- Pull Requests (currently only GitHub PRs are supported)

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Airbyte Forum [here](https://github.com/airbytehq/airbyte/discussions).

## Rate Limiting & Performance

The Jira connector should not run into Jira API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                          |
|:--------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3.2.1 | 2024-10-12 | [44650](https://github.com/airbytehq/airbyte/pull/44650) | Update dependencies |
| 3.2.0 | 2024-10-10 | [46344](https://github.com/airbytehq/airbyte/pull/46344) | Update CDK v5 |
| 3.1.1 | 2024-08-17 | [44251](https://github.com/airbytehq/airbyte/pull/44251) | Update dependencies |
| 3.1.0 | 2024-08-13 | [39558](https://github.com/airbytehq/airbyte/pull/39558) | Ensure config_error when state has improper format |
| 3.0.14 | 2024-08-12 | [43885](https://github.com/airbytehq/airbyte/pull/43885) | Update dependencies |
| 3.0.13 | 2024-08-10 | [43542](https://github.com/airbytehq/airbyte/pull/43542) | Update dependencies |
| 3.0.12 | 2024-08-03 | [43196](https://github.com/airbytehq/airbyte/pull/43196) | Update dependencies |
| 3.0.11 | 2024-07-27 | [42802](https://github.com/airbytehq/airbyte/pull/42802) | Update dependencies |
| 3.0.10 | 2024-07-20 | [42231](https://github.com/airbytehq/airbyte/pull/42231) | Update dependencies |
| 3.0.9 | 2024-07-13 | [41842](https://github.com/airbytehq/airbyte/pull/41842) | Update dependencies |
| 3.0.8 | 2024-07-10 | [41453](https://github.com/airbytehq/airbyte/pull/41453) | Update dependencies |
| 3.0.7 | 2024-07-09 | [41175](https://github.com/airbytehq/airbyte/pull/41175) | Update dependencies |
| 3.0.6 | 2024-07-06 | [40785](https://github.com/airbytehq/airbyte/pull/40785) | Update dependencies |
| 3.0.5 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 3.0.4 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 3.0.3 | 2024-06-25 | [40444](https://github.com/airbytehq/airbyte/pull/40444) | Update dependencies |
| 3.0.2 | 2024-06-21 | [40121](https://github.com/airbytehq/airbyte/pull/40121) | Update dependencies |
| 3.0.1 | 2024-06-13 | [39458](https://github.com/airbytehq/airbyte/pull/39458) | Fix skipping custom_field_options entities when schema.items is options |
| 3.0.0 | 2024-06-14 | [39467](https://github.com/airbytehq/airbyte/pull/39467) | Update pk for Workflows stream from Id(object) to entityId, name(string, string) |
| 2.0.3 | 2024-06-10 | [39347](https://github.com/airbytehq/airbyte/pull/39347) | Update state handling for incremental Python streams |
| 2.0.2 | 2024-06-06 | [39310](https://github.com/airbytehq/airbyte/pull/39310) | Fix projects substreams for deleted projects |
| 2.0.1 | 2024-05-20 | [38341](https://github.com/airbytehq/airbyte/pull/38341) | Update CDK authenticator package |
| 2.0.0 | 2024-04-20 | [37374](https://github.com/airbytehq/airbyte/pull/37374) | Migrate to low-code and fix `Project Avatars` stream |
| 1.2.2 | 2024-04-19 | [36646](https://github.com/airbytehq/airbyte/pull/36646) | Updating to 0.80.0 CDK |
| 1.2.1 | 2024-04-12 | [36646](https://github.com/airbytehq/airbyte/pull/36646) | schema descriptions |
| 1.2.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 1.1.0 | 2024-02-27 | [35656](https://github.com/airbytehq/airbyte/pull/35656) | Add new fields to streams `board_issues`, `filter_sharing`, `filters`, `issues`, `permission_schemes`, `sprint_issues`, `users_groups_detailed`, and `workflows` |
| 1.0.2 | 2024-02-12 | [35160](https://github.com/airbytehq/airbyte/pull/35160) | Manage dependencies with Poetry. |
| 1.0.1 | 2024-01-24 | [34470](https://github.com/airbytehq/airbyte/pull/34470) | Add state checkpoint interval for all streams |
| 1.0.0 | 2024-01-01 | [33715](https://github.com/airbytehq/airbyte/pull/33715) | Save state for stream `Board Issues` per `board` |
| 0.14.1 | 2023-12-19 | [33625](https://github.com/airbytehq/airbyte/pull/33625) | Skip 404 error |
| 0.14.0 | 2023-12-15 | [33532](https://github.com/airbytehq/airbyte/pull/33532) | Add lookback window |
| 0.13.0 | 2023-12-12 | [33353](https://github.com/airbytehq/airbyte/pull/33353) | Fix check command to check access for all available streams |
| 0.12.0 | 2023-12-01 | [33011](https://github.com/airbytehq/airbyte/pull/33011) | Fix BoardIssues stream; increase number of retries for backoff policy to 10 |
| 0.11.0 | 2023-11-29 | [32927](https://github.com/airbytehq/airbyte/pull/32927) | Fix incremental syncs for stream Issues |
| 0.10.2 | 2023-10-26 | [31896](https://github.com/airbytehq/airbyte/pull/31896) | Provide better guidance when configuring the connector with an invalid domain |
| 0.10.1 | 2023-10-23 | [31702](https://github.com/airbytehq/airbyte/pull/31702) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.10.0  | 2023-10-13 | [\#31385](https://github.com/airbytehq/airbyte/pull/31385) | Fixed `aggregatetimeoriginalestimate, timeoriginalestimate` field types for the `Issues` stream schema                                                           |
| 0.9.0   | 2023-09-26 | [\#30688](https://github.com/airbytehq/airbyte/pull/30688) | Added `createdDate` field to sprints schema, Removed `Expand Issues stream` from spec                                                                            |
| 0.8.0   | 2023-09-26 | [\#30755](https://github.com/airbytehq/airbyte/pull/30755) | Add new streams: `Issue custom field options`, `IssueTypes`, `Project Roles`                                                                                     |
| 0.7.2   | 2023-09-19 | [\#30675](https://github.com/airbytehq/airbyte/pull/30675) | Ensure invalid URL does not trigger Sentry alert                                                                                                                 |
| 0.7.1   | 2023-09-19 | [\#30585](https://github.com/airbytehq/airbyte/pull/30585) | Add skip for 404 error in issue properties steam                                                                                                                 |
| 0.7.0   | 2023-09-17 | [\#30532](https://github.com/airbytehq/airbyte/pull/30532) | Add foreign key to stream record where it missing                                                                                                                |
| 0.6.3   | 2023-09-19 | [\#30515](https://github.com/airbytehq/airbyte/pull/30515) | Add transform for invalid date-time format, add 404 handling for check                                                                                           |
| 0.6.2   | 2023-09-19 | [\#30578](https://github.com/airbytehq/airbyte/pull/30578) | Fetch deleted and archived Projects                                                                                                                              |
| 0.6.1   | 2023-09-17 | [\#30550](https://github.com/airbytehq/airbyte/pull/30550) | Update `Issues` expand settings                                                                                                                                  |
| 0.6.0   | 2023-09-17 | [\#30507](https://github.com/airbytehq/airbyte/pull/30507) | Add new stream `IssueTransitions`                                                                                                                                |
| 0.5.0   | 2023-09-14 | [\#29960](https://github.com/airbytehq/airbyte/pull/29960) | Add `boardId` to `sprints` stream                                                                                                                                |
| 0.3.14  | 2023-09-11 | [\#30297](https://github.com/airbytehq/airbyte/pull/30297) | Remove `requests` and `pendulum` from setup dependencies                                                                                                         |
| 0.3.13  | 2023-09-01 | [\#30108](https://github.com/airbytehq/airbyte/pull/30108) | Skip 404 error for stream `IssueWatchers`                                                                                                                        |
| 0.3.12  | 2023-06-01 | [\#26652](https://github.com/airbytehq/airbyte/pull/26652) | Expand on `leads` for `projects` stream                                                                                                                          |
| 0.3.11  | 2023-06-01 | [\#26906](https://github.com/airbytehq/airbyte/pull/26906) | Handle project permissions error                                                                                                                                 |
| 0.3.10  | 2023-05-26 | [\#26652](https://github.com/airbytehq/airbyte/pull/26652) | Fixed bug when `board` doesn't support `sprints`                                                                                                                 |
| 0.3.9   | 2023-05-16 | [\#26114](https://github.com/airbytehq/airbyte/pull/26114) | Update fields info in docs and spec, update to latest airbyte-cdk                                                                                                |
| 0.3.8   | 2023-05-04 | [\#25798](https://github.com/airbytehq/airbyte/pull/25798) | Add sprint info to `sprint_issues` and `sprints` streams for team-managed projects                                                                               |
| 0.3.7   | 2023-04-18 | [\#25275](https://github.com/airbytehq/airbyte/pull/25275) | Add missing types to issues json schema                                                                                                                          |
| 0.3.6   | 2023-04-10 | [\#24636](https://github.com/airbytehq/airbyte/pull/24636) | Removed Connector Domain Pattern from Spec                                                                                                                       |
| 0.3.5   | 2023-04-05 | [\#24890](https://github.com/airbytehq/airbyte/pull/24890) | Fix streams "IssuePropertyKeys", "ScreenTabFields"                                                                                                               |
| 0.3.4   | 2023-02-14 | [\#23006](https://github.com/airbytehq/airbyte/pull/23006) | Remove caching for `Issues` stream                                                                                                                               |
| 0.3.3   | 2023-01-04 | [\#20739](https://github.com/airbytehq/airbyte/pull/20739) | fix: check_connection fails if no projects are defined                                                                                                           |
| 0.3.2   | 2022-12-23 | [\#20859](https://github.com/airbytehq/airbyte/pull/20859) | Fixed pagination for streams `issue_remote_links`, `sprints`                                                                                                     |
| 0.3.1   | 2022-12-14 | [\#20128](https://github.com/airbytehq/airbyte/pull/20128) | Improved code to become beta                                                                                                                                     |
| 0.3.0   | 2022-11-03 | [\#18901](https://github.com/airbytehq/airbyte/pull/18901) | Adds UserGroupsDetailed schema, fix Incremental normalization, add Incremental support for IssueComments, IssueWorklogs                                          |
| 0.2.23  | 2022-10-28 | [\#18505](https://github.com/airbytehq/airbyte/pull/18505) | Correcting `max_results` bug introduced in connector stream                                                                                                      |
| 0.2.22  | 2022-10-03 | [\#16944](https://github.com/airbytehq/airbyte/pull/16944) | Adds support for `max_results` to `users` stream                                                                                                                 |
| 0.2.21  | 2022-07-28 | [\#15135](https://github.com/airbytehq/airbyte/pull/15135) | Adds components to `fields` object on `issues` stream                                                                                                            |
| 0.2.20  | 2022-05-25 | [\#13202](https://github.com/airbytehq/airbyte/pull/13202) | Adds resolutiondate to `fields` object on `issues` stream                                                                                                        |
| 0.2.19  | 2022-05-04 | [\#10835](https://github.com/airbytehq/airbyte/pull/10835) | Change description for array fields                                                                                                                              |
| 0.2.18  | 2021-12-23 | [\#7378](https://github.com/airbytehq/airbyte/pull/7378)   | Adds experimental endpoint Pull Request                                                                                                                          |
| 0.2.17  | 2021-12-23 | [\#9079](https://github.com/airbytehq/airbyte/pull/9079)   | Update schema for `filters` stream + fix fetching `filters` stream                                                                                               |
| 0.2.16  | 2021-12-21 | [\#8999](https://github.com/airbytehq/airbyte/pull/8999)   | Update connector fields title/description                                                                                                                        |
| 0.2.15  | 2021-11-01 | [\#7398](https://github.com/airbytehq/airbyte/pull/7398)   | Add option to render fields in HTML format and fix sprint_issue ids                                                                                              |
| 0.2.14  | 2021-10-27 | [\#7408](https://github.com/airbytehq/airbyte/pull/7408)   | Fix normalization step error. Fix schemas. Fix `acceptance-test-config.yml`. Fix `streams.py`.                                                                   |
| 0.2.13  | 2021-10-20 | [\#7222](https://github.com/airbytehq/airbyte/pull/7222)   | Source Jira: Make recently added configs optional for backwards compatibility                                                                                    |
| 0.2.12  | 2021-10-19 | [\#6621](https://github.com/airbytehq/airbyte/pull/6621)   | Add Board, Epic, and Sprint streams                                                                                                                              |
| 0.2.11  | 2021-09-02 | [\#6523](https://github.com/airbytehq/airbyte/pull/6523)   | Add cache and more streams \(boards and sprints\)                                                                                                                |
| 0.2.9   | 2021-07-28 | [\#5426](https://github.com/airbytehq/airbyte/pull/5426)   | Changed cursor field from fields.created to fields.updated for Issues stream. Made Issues worklogs stream full refresh.                                          |
| 0.2.8   | 2021-07-28 | [\#4947](https://github.com/airbytehq/airbyte/pull/4947)   | Source Jira: fixing schemas accordingly to response.                                                                                                             |
| 0.2.7   | 2021-07-19 | [\#4817](https://github.com/airbytehq/airbyte/pull/4817)   | Fixed `labels` schema properties issue.                                                                                                                          |
| 0.2.6   | 2021-06-15 | [\#4113](https://github.com/airbytehq/airbyte/pull/4113)   | Fixed `user` stream with the correct endpoint and query param.                                                                                                   |
| 0.2.5   | 2021-06-09 | [\#3973](https://github.com/airbytehq/airbyte/pull/3973)   | Added `AIRBYTE_ENTRYPOINT` in base Docker image for Kubernetes support.                                                                                          |
| 0.2.4   |            |                                                            | Implementing base_read acceptance test dived by stream groups.                                                                                                   |
| 0.2.3   |            |                                                            | Implementing incremental sync. Migrated to airbyte-cdk. Adding all available entities in Jira Cloud.                                                             |

</details>
