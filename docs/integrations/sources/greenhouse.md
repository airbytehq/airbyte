# Greenhouse

This page contains the setup guide and reference information for the Greenhouse source connector.

## Prerequisites

To set up the Greenhouse source connector, you'll need the [Harvest API key](https://developers.greenhouse.io/harvest.html#authentication) with permissions to the resources Airbyte should be able to access.

## Set up the Greenhouse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Greenhouse** from the Source type dropdown.
4. Enter the name for the Greenhouse connector.
5. Enter your [**Harvest API Key**](https://developers.greenhouse.io/harvest.html#authentication) that you obtained from Greenhouse.
6. Click **Set up source**.

## Supported sync modes

The Greenhouse source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

- [Activity Feed](https://developers.greenhouse.io/harvest.html#get-retrieve-activity-feed)
- [Applications](https://developers.greenhouse.io/harvest.html#get-list-applications) \(Incremental\)
- [Applications Interviews](https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews-for-application) \(Incremental\)
- [Applications Demographics Answers](https://developers.greenhouse.io/harvest.html#get-list-demographic-answers-for-application) \(Incremental\)
- [Demographics Answers](https://developers.greenhouse.io/harvest.html#get-list-demographic-answers) \(Incremental\)
- [Demographic Answer Options](https://developers.greenhouse.io/harvest.html#get-list-demographic-answer-options)
- [Demographic Answer Options For Question](https://developers.greenhouse.io/harvest.html#get-list-demographic-answer-options-for-demographic-question)
- [Demographic Questions](https://developers.greenhouse.io/harvest.html#get-list-demographic-questions)
- [Demographic Question Set](https://developers.greenhouse.io/harvest.html#get-list-demographic-question-sets)
- [Demographic Questions For Question Set](https://developers.greenhouse.io/harvest.html#get-list-demographic-questions-for-demographic-question-set)
- [Approvals](https://developers.greenhouse.io/harvest.html#get-list-approvals-for-job)
- [Candidates](https://developers.greenhouse.io/harvest.html#get-list-candidates) \(Incremental\)
- [Close Reasons](https://developers.greenhouse.io/harvest.html#get-list-close-reasons)
- [Custom Fields](https://developers.greenhouse.io/harvest.html#get-list-custom-fields)
- [Degrees](https://developers.greenhouse.io/harvest.html#get-list-degrees)
- [Departments](https://developers.greenhouse.io/harvest.html#get-list-departments)
- [Disciplines](https://developers.greenhouse.io/harvest.html#get-list-approvals-for-job)
- [EEOC](https://developers.greenhouse.io/harvest.html#get-list-eeoc) \(Incremental\)
- [Email Templates](https://developers.greenhouse.io/harvest.html#get-list-email-templates) \(Incremental\)
- [Interviews](https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews) \(Incremental\)
- [Job Posts](https://developers.greenhouse.io/harvest.html#get-list-job-posts) \(Incremental\)
- [Job Stages](https://developers.greenhouse.io/harvest.html#get-list-job-stages) \(Incremental\)
- [Jobs](https://developers.greenhouse.io/harvest.html#get-list-jobs) \(Incremental\)
- [Job Openings](https://developers.greenhouse.io/harvest.html#get-list-job-openings)
- [Jobs Stages](https://developers.greenhouse.io/harvest.html#get-list-job-stages-for-job) \(Incremental\)
- [Offers](https://developers.greenhouse.io/harvest.html#get-list-offers) \(Incremental\)
- [Offices](https://developers.greenhouse.io/harvest.html#get-list-offices)
- [Prospect Pools](https://developers.greenhouse.io/harvest.html#get-list-prospect-pools)
- [Rejection Reasons](https://developers.greenhouse.io/harvest.html#get-list-rejection-reasons)
- [Schools](https://developers.greenhouse.io/harvest.html#get-list-schools)
- [Scorecards](https://developers.greenhouse.io/harvest.html#get-list-scorecards) \(Incremental\)
- [Sources](https://developers.greenhouse.io/harvest.html#get-list-sources)
- [Tags](https://developers.greenhouse.io/harvest.html#get-list-candidate-tags)
- [Users](https://developers.greenhouse.io/harvest.html#get-list-users) \(Incremental\)
- [User Permissions](https://developers.greenhouse.io/harvest.html#get-list-job-permissions)
- [User Roles](https://developers.greenhouse.io/harvest.html#the-user-role-object)

## Performance considerations

The Greenhouse connector should not run into Greenhouse API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you encounter any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                              |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.5.3   | 2024-04-19 | [36640](https://github.com/airbytehq/airbyte/pull/36640) | Updating to 0.80.0 CDK                                                                                                                                               |
| 0.5.2   | 2024-04-12 | [36640](https://github.com/airbytehq/airbyte/pull/36640) | schema descriptions                                                                                                                                                  |
| 0.5.1   | 2024-03-12 | [35988](https://github.com/airbytehq/airbyte/pull/35988) | Unpin CDK version                                                                                                                                                    |
| 0.5.0   | 2024-02-20 | [35465](https://github.com/airbytehq/airbyte/pull/35465) | Per-error reporting and continue sync on stream failures                                                                                                             |
| 0.4.5   | 2024-02-09 | [35077](https://github.com/airbytehq/airbyte/pull/35077) | Manage dependencies with Poetry.                                                                                                                                     |
| 0.4.4   | 2023-11-29 | [32397](https://github.com/airbytehq/airbyte/pull/32397) | Increase test coverage and migrate to base image                                                                                                                     |
| 0.4.3   | 2023-09-20 | [30648](https://github.com/airbytehq/airbyte/pull/30648) | Update candidates.json                                                                                                                                               |
| 0.4.2   | 2023-08-02 | [28969](https://github.com/airbytehq/airbyte/pull/28969) | Update CDK version                                                                                                                                                   |
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

</details>