# Greenhouse

This page contains the setup guide and reference information for the Greenhouse source connector.

## Prerequisites

To set up the Greenhouse source connector, you'll need the [Harvest API key](https://developers.greenhouse.io/harvest.html#authentication) with permissions to the resources Airbyte should be able to access.

## Set up the Greenhouse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Greenhouse** from the Source type dropdown.
4. Enter the name for the Greenhouse connector.
4. Enter your [**Harvest API Key**](https://developers.greenhouse.io/harvest.html#authentication) that you obtained from Greenhouse.
5. Click **Set up source**.

## Supported sync modes

The Greenhouse source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

* [Activity Feed](https://developers.greenhouse.io/harvest.html#get-retrieve-activity-feed)
* [Applications](https://developers.greenhouse.io/harvest.html#get-list-applications)
* [Applications Interviews](https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews-for-application)
* [Approvals](https://developers.greenhouse.io/harvest.html#get-list-approvals-for-job)
* [Candidates](https://developers.greenhouse.io/harvest.html#get-list-candidates)
* [Close Reasons](https://developers.greenhouse.io/harvest.html#get-list-close-reasons)
* [Custom Fields](https://developers.greenhouse.io/harvest.html#get-list-custom-fields)
* [Degrees](https://developers.greenhouse.io/harvest.html#get-list-degrees)
* [Departments](https://developers.greenhouse.io/harvest.html#get-list-departments)
* [Disciplines](https://developers.greenhouse.io/harvest.html#get-list-approvals-for-job)
* [EEOC](https://developers.greenhouse.io/harvest.html#get-list-eeoc)
* [Email Templates](https://developers.greenhouse.io/harvest.html#get-list-email-templates)
* [Interviews](https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews)
* [Job Posts](https://developers.greenhouse.io/harvest.html#get-list-job-posts)
* [Job Stages](https://developers.greenhouse.io/harvest.html#get-list-job-stages)
* [Jobs](https://developers.greenhouse.io/harvest.html#get-list-jobs)
* [Job Openings](https://developers.greenhouse.io/harvest.html#get-list-job-openings)
* [Jobs Stages](https://developers.greenhouse.io/harvest.html#get-list-job-stages-for-job)
* [Offers](https://developers.greenhouse.io/harvest.html#get-list-offers)
* [Offices](https://developers.greenhouse.io/harvest.html#get-list-offices)
* [Prospect Pools](https://developers.greenhouse.io/harvest.html#get-list-prospect-pools)
* [Rejection Reasons](https://developers.greenhouse.io/harvest.html#get-list-rejection-reasons)
* [Schools](https://developers.greenhouse.io/harvest.html#get-list-schools)
* [Scorecards](https://developers.greenhouse.io/harvest.html#get-list-scorecards)
* [Sources](https://developers.greenhouse.io/harvest.html#get-list-sources)
* [Tags](https://developers.greenhouse.io/harvest.html#get-list-candidate-tags)
* [Users](https://developers.greenhouse.io/harvest.html#get-list-users)
* [User Permissions](https://developers.greenhouse.io/harvest.html#get-list-job-permissions)
* [User Roles](https://developers.greenhouse.io/harvest.html#the-user-role-object)

## Performance considerations

The Greenhouse connector should not run into Greenhouse API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                              |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.4.1   | 2023-06-28 | [27773](https://github.com/airbytehq/airbyte/pull/27773) | Update following state breaking changes                                                                                                                              |
| 0.4.0   | 2023-04-26 | [25332](https://github.com/airbytehq/airbyte/pull/25332) | Add new streams: `ActivityFeed`, `Approvals`, `Disciplines`, `Eeoc`, `EmailTemplates`, `Offices`, `ProspectPools`, `Schools`, `Tags`, `UserPermissions`, `UserRoles` |
| 0.3.1   | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version                                                                                                                              |
| 0.3.0   | 2022-10-19 | [18154](https://github.com/airbytehq/airbyte/pull/18154) | Extend `Users` stream schema                                                                                                                                         |
| 0.2.11  | 2022-09-27 | [17239](https://github.com/airbytehq/airbyte/pull/17239) | Always install the latest version of Airbyte CDK                                                                                                                     |
| 0.2.10  | 2022-09-05 | [16338](https://github.com/airbytehq/airbyte/pull/16338) | Implement incremental syncs & fix SATs                                                                                                                               |
| 0.2.9   | 2022-08-22 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml and schemas at runtime                                                                                                           |
| 0.2.8   | 2022-08-10 | [15344](https://github.com/airbytehq/airbyte/pull/15344) | Migrate connector to config-based framework                                                                                                                          |
| 0.2.7   | 2022-04-15 | [11941](https://github.com/airbytehq/airbyte/pull/11941) | Correct Schema data type for Applications, Candidates, Scorecards and Users                                                                                          |
| 0.2.6   | 2021-11-08 | [7607](https://github.com/airbytehq/airbyte/pull/7607)   | Implement demographics streams support. Update SAT for demographics streams                                                                                          |
| 0.2.5   | 2021-09-22 | [6377](https://github.com/airbytehq/airbyte/pull/6377)   | Refactor the connector to use CDK. Implement additional stream support                                                                                               |
| 0.2.4   | 2021-09-15 | [6238](https://github.com/airbytehq/airbyte/pull/6238)   | Add identification of accessible streams for API keys with limited permissions                                                                                       |
