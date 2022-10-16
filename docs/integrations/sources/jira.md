# Jira

## Features

| Feature | Supported? |  |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes | Only Issues |
| Replicate Incremental Deletes | Coming soon |  |
| SSL connection | Yes |  |

## Troubleshooting

Check out common troubleshooting issues for the Jira connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/source-jira).

## Supported Tables

This source is capable of syncing the following tables and their data:

* [Application roles](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-application-roles/#api-rest-api-3-applicationrole-get)
* [Avatars](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-avatars/#api-rest-api-3-avatar-type-system-get)
* [Dashboards](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-get)
* [Filters](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get)
* [Filters](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get)
* [Filter sharing](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-get)
* [Groups](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-groups/#api-rest-api-3-groups-picker-get)
* [Issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get)
* [Issue comments](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-get)
* [Issue fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-fields/#api-rest-api-3-field-get)
* [Issue field configurations](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-field-configurations/#api-rest-api-3-fieldconfiguration-get)
* [Issue custom field contexts](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-custom-field-contexts/#api-rest-api-3-field-fieldid-context-get)
* [Issue link types](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-link-types/#api-rest-api-3-issuelinktype-get)
* [Issue navigator settings](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-navigator-settings/#api-rest-api-3-settings-columns-get)
* [Issue notification schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-notification-schemes/#api-rest-api-3-notificationscheme-get)
* [Issue priorities](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-priorities/#api-rest-api-3-priority-get)
* [Issue properties](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-properties/#api-rest-api-3-issue-issueidorkey-properties-propertykey-get)
* [Issue remote links](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-get)
* [Issue resolutions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-rest-api-3-resolution-get)
* [Issue security schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-security-schemes/#api-rest-api-3-issuesecurityschemes-get)
* [Issue type schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-schemes/#api-rest-api-3-issuetypescheme-get)
* [Issue type screen schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-type-screen-schemes/#api-rest-api-3-issuetypescreenscheme-get)
* [Issue votes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-votes/#api-group-issue-votes)
* [Issue watchers](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-watchers/#api-rest-api-3-issue-issueidorkey-watchers-get)
* [Issue worklogs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-get)
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
* [Screen tabs](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tabs/)
* [Screen tab fields](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-tab-fields/#api-rest-api-3-screens-screenid-tabs-tabid-fields-get)
* [Screen schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-screen-schemes/#api-rest-api-3-screenscheme-get)
* [Time tracking](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-time-tracking/#api-rest-api-3-configuration-timetracking-list-get)
* [Users](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-search-get)
* [Workflows](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflows/#api-rest-api-3-workflow-search-get)
* [Workflow schemes](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-get)
* [Workflow statuses](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-statuses/#api-rest-api-3-status-get)
* [Workflow status categories](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-status-categories/#api-rest-api-3-statuscategory-get)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Experimental Tables

The following tables depend on undocumented internal Jira API endpoints and are
therefore subject to stop working if those endpoints undergo major changes.
While they will not cause a sync to fail, they may not be able to pull any data.
Use the "Enable Experimental Streams" option when setting up the source to allow
or disallow these tables to be selected when configuring a connection.

* Pull Requests (currently only GitHub PRs are supported)

## Getting Started \(Airbyte Open-Source / Airbyte Cloud\)

### Requirements

* Jira API Token
* Jira Email
* Jira Domain

Please follow the [Jira confluence for generating an API token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html).

## Rate Limiting & Performance

The Jira connector should not run into Jira API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## CHANGELOG

| Version | Date       | Pull Request                                                | Subject                                                                                                                 |
|:--------|:-----------|:------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| 0.2.21  | 2022-07-28 | [\#15135](hhttps://github.com/airbytehq/airbyte/pull/15135) | Adds components to `fields` object on `issues` stream                                                                   |
| 0.2.20  | 2022-05-25 | [\#13202](https://github.com/airbytehq/airbyte/pull/13202)  | Adds resolutiondate to `fields` object on `issues` stream                                                               |
| 0.2.19  | 2022-05-04 | [\#10835](https://github.com/airbytehq/airbyte/pull/10835)  | Change description for array fields                                                                                     |
| 0.2.18  | 2021-12-23 | [\#7378](https://github.com/airbytehq/airbyte/pull/7378)    | Adds experimental endpoint Pull Request                                                                                 |
| 0.2.17  | 2021-12-23 | [\#9079](https://github.com/airbytehq/airbyte/pull/9079)    | Update schema for `filters` stream + fix fetching `filters` stream                                                      |
| 0.2.16  | 2021-12-21 | [\#8999](https://github.com/airbytehq/airbyte/pull/8999)    | Update connector fields title/description                                                                               |
| 0.2.15  | 2021-11-01 | [\#7398](https://github.com/airbytehq/airbyte/pull/7398)    | Add option to render fields in HTML format and fix sprint_issue ids                                                     |
| 0.2.14  | 2021-10-27 | [\#7408](https://github.com/airbytehq/airbyte/pull/7408)    | Fix normalization step error. Fix schemas. Fix `acceptance-test-config.yml`. Fix `streams.py`.                          |
| 0.2.13  | 2021-10-20 | [\#7222](https://github.com/airbytehq/airbyte/pull/7222)    | Source Jira: Make recently added configs optional for backwards compatibility                                           |
| 0.2.12  | 2021-10-19 | [\#6621](https://github.com/airbytehq/airbyte/pull/6621)    | Add Board, Epic, and Sprint streams                                                                                     |
| 0.2.11  | 2021-09-02 | [\#6523](https://github.com/airbytehq/airbyte/pull/6523)    | Add cache and more streams \(boards and sprints\)                                                                       |
| 0.2.9   | 2021-07-28 | [\#5426](https://github.com/airbytehq/airbyte/pull/5426)    | Changed cursor field from fields.created to fields.updated for Issues stream. Made Issues worklogs stream full refresh. |
| 0.2.8   | 2021-07-28 | [\#4947](https://github.com/airbytehq/airbyte/pull/4947)    | Source Jira: fixing schemas accordinately to response.                                                                  |
| 0.2.7   | 2021-07-19 | [\#4817](https://github.com/airbytehq/airbyte/pull/4817)    | Fixed `labels` schema properties issue.                                                                                 |
| 0.2.6   | 2021-06-15 | [\#4113](https://github.com/airbytehq/airbyte/pull/4113)    | Fixed `user` stream with the correct endpoint and query param.                                                          |
| 0.2.5   | 2021-06-09 | [\#3973](https://github.com/airbytehq/airbyte/pull/3973)    | Added `AIRBYTE_ENTRYPOINT` in base Docker image for Kubernetes support.                                                 |
| 0.2.4   |            |                                                             | Implementing base\_read acceptance test dived by stream groups.                                                         |
| 0.2.3   |            |                                                             | Implementing incremental sync. Migrated to airbyte-cdk. Adding all available entities in Jira Cloud.                    |

