# Asana

This page contains the setup guide and reference information for the Asana source connector.

## Prerequisites

Please follow these [steps](https://developers.asana.com/docs/personal-access-token) to obtain Personal Access Token for your account.

## Setup guide
## Step 1: Set up the Asana connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Asana connector and select **Asana** from the Source type dropdown.
4. Select `Authenticate your account`.
5. Log in and Authorize to the Asana account and click `Set up source`.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source 
3. Enter your `personal_access_token`
4. Click **Set up source**

## Supported sync modes

The Asana source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| Namespaces        | No         |

## Supported Streams

* [Custom fields](https://developers.asana.com/docs/custom-fields)
* [Projects](https://developers.asana.com/docs/projects)
* [Sections](https://developers.asana.com/docs/sections)
* [Stories](https://developers.asana.com/docs/stories)
* [Tags](https://developers.asana.com/docs/tags)
* [Tasks](https://developers.asana.com/docs/tasks)
* [Teams](https://developers.asana.com/docs/teams)
* [Team Memberships](https://developers.asana.com/docs/team-memberships)
* [Users](https://developers.asana.com/docs/users)
* [Workspaces](https://developers.asana.com/docs/workspaces)

## Performance considerations

The connector is restricted by normal Asana [requests limitation](https://developers.asana.com/docs/rate-limits).

## Data type map

| Integration Type         | Airbyte Type |
| :----------------------- | :----------- |
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                     |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------- |
| 0.1.5   | 2022-11-16 | [19561](https://github.com/airbytehq/airbyte/pull/19561) | Added errors handling, updated SAT with new format
| 0.1.4   | 2022-08-18 | [15749](https://github.com/airbytehq/airbyte/pull/15749) | Add cache to project stream                                 |
| 0.1.3   | 2021-10-06 | [6832](https://github.com/airbytehq/airbyte/pull/6832)   | Add oauth init flow parameters support                      |
| 0.1.2   | 2021-09-24 | [6402](https://github.com/airbytehq/airbyte/pull/6402)   | Fix SAT tests: update schemas and invalid\_config.json file |
| 0.1.1   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add entrypoint and bump version for connector               |
| 0.1.0   | 2021-05-25 | [3510](https://github.com/airbytehq/airbyte/pull/3510)   | New Source: Asana                                           |
