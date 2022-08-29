# Greenhouse

This page contains the setup guide and reference information for the Greenhouse source connector.

## Prerequisites

Please follow the [Greenhouse documentation for generating an API key](https://developers.greenhouse.io/harvest.html#authentication).

## Setup guide
## Step 1: Set up the Greenhouse connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Source**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Greenhouse connector and select **Greenhouse** from the Source type dropdown. 
4. Enter your `api_key`
5. Click **Set up source**

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `api_key`
4. Click **Set up source**

## Supported sync modes

The Greenhouse source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

## Supported Streams

* [Applications](https://developers.greenhouse.io/harvest.html#get-list-applications)
* [Applications Interviews](https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews-for-application)
* [Candidates](https://developers.greenhouse.io/harvest.html#get-list-candidates)
* [Close Reasons](https://developers.greenhouse.io/harvest.html#get-list-close-reasons)
* [Custom Fields](https://developers.greenhouse.io/harvest.html#get-list-custom-fields)
* [Degrees](https://developers.greenhouse.io/harvest.html#get-list-degrees)
* [Departments](https://developers.greenhouse.io/harvest.html#get-list-departments)
* [Interviews](https://developers.greenhouse.io/harvest.html#get-list-scheduled-interviews)
* [Job Posts](https://developers.greenhouse.io/harvest.html#get-list-job-posts)
* [Job Stages](https://developers.greenhouse.io/harvest.html#get-list-job-stages)
* [Jobs](https://developers.greenhouse.io/harvest.html#get-list-jobs)
* [Jobs Openings](https://developers.greenhouse.io/harvest.html#get-list-job-openings)
* [Jobs Stages](https://developers.greenhouse.io/harvest.html#get-list-job-stages-for-job)
* [Offers](https://developers.greenhouse.io/harvest.html#get-list-offers)
* [Rejection Reasons](https://developers.greenhouse.io/harvest.html#get-list-rejection-reasons)
* [Scorecards](https://developers.greenhouse.io/harvest.html#get-list-scorecards)
* [Sources](https://developers.greenhouse.io/harvest.html#get-list-sources)
* [Users](https://developers.greenhouse.io/harvest.html#get-list-users)

## Performance considerations

The Greenhouse connector should not run into Greenhouse API limitations under normal usage. 
Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                          |
|:--------|:-----------|:---------------------------------------------------------|:---------------------------------------------------------------------------------|
| 0.2.9   | 2022-08-22 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml and schemas at runtime                       |
| 0.2.8   | 2022-08-10 | [15344](https://github.com/airbytehq/airbyte/pull/15344) | Migrate connector to config-based framework                                      |
| 0.2.7   | 2022-04-15 | [11941](https://github.com/airbytehq/airbyte/pull/11941) | Correct Schema data type for Applications, Candidates, Scorecards and Users      |
| 0.2.6   | 2021-11-08 | [7607](https://github.com/airbytehq/airbyte/pull/7607)   | Implement demographics streams support. Update SAT for demographics streams      |
| 0.2.5   | 2021-09-22 | [6377](https://github.com/airbytehq/airbyte/pull/6377)   | Refactor the connector to use CDK. Implement additional stream support           |
| 0.2.4   | 2021-09-15 | [6238](https://github.com/airbytehq/airbyte/pull/6238)   | Add identification of accessible streams for API keys with limited permissions |
