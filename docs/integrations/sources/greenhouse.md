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
|:------------------------------|:------------|
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Yes         |
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

## Setting permissions for API Keys
You can specify which API endpoints your API keys have access to from the Greenhouse Dev Center. This will allow you to permit or deny access to each endpoint individually. Any API keys created before January 18th, 2017 will have full permissions to all API endpoints that existed at that time, but any new API keys created after that point will need to be explicitly granted the required endpoint permissions.
To add or remove endpoint permissions on an API key, go to the Dev Center in Greenhouse, click “API Credential Management,” then click “Manage Permissions” next to your Harvest API Key. From there, check or uncheck permissions for any endpoints.

**Important Note**: Users with Harvest API keys may access all the data in the endpoint. Access to data in Harvest is binary: everything or nothing. Harvest API keys should be given to internal developers with this understanding and to third parties with caution. Each key should only be allowed to access the endpoints it absolutely needs.
See more on this [here](https://developers.greenhouse.io/harvest.html#authentication).

## Performance considerations

The Greenhouse connector should not run into Greenhouse API limitations under normal usage. 
Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------|
| 0.3.0   | 2022-10-19 | [18154](https://github.com/airbytehq/airbyte/pull/18154) | Extend `Users` stream schema                                                   |
| 0.2.11  | 2022-09-27 | [17239](https://github.com/airbytehq/airbyte/pull/17239) | Always install the latest version of Airbyte CDK                               |
| 0.2.10  | 2022-09-05 | [16338](https://github.com/airbytehq/airbyte/pull/16338) | Implement incremental syncs & fix SATs                                         |
| 0.2.9   | 2022-08-22 | [15800](https://github.com/airbytehq/airbyte/pull/15800) | Bugfix to allow reading sentry.yaml and schemas at runtime                     |
| 0.2.8   | 2022-08-10 | [15344](https://github.com/airbytehq/airbyte/pull/15344) | Migrate connector to config-based framework                                    |
| 0.2.7   | 2022-04-15 | [11941](https://github.com/airbytehq/airbyte/pull/11941) | Correct Schema data type for Applications, Candidates, Scorecards and Users    |
| 0.2.6   | 2021-11-08 | [7607](https://github.com/airbytehq/airbyte/pull/7607)   | Implement demographics streams support. Update SAT for demographics streams    |
| 0.2.5   | 2021-09-22 | [6377](https://github.com/airbytehq/airbyte/pull/6377)   | Refactor the connector to use CDK. Implement additional stream support         |
| 0.2.4   | 2021-09-15 | [6238](https://github.com/airbytehq/airbyte/pull/6238)   | Add identification of accessible streams for API keys with limited permissions |
