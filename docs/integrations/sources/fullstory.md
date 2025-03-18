# FullStory

This page contains the setup guide and reference information for the [FullStory](https://developer.fullstory.com/) source

## Prerequisites

API Key (which acts as bearer token) is mandate for this connector to work, It could be seen at settings (ref - https://app.fullstory.com/ui/o-1K942V-na1/settings/apikeys).

## Setup guide

### Step 1: Set up FullStory connection

- Get a FullStory api key via settings (ref - https://app.fullstory.com/ui/o-1K942V-na1/settings/apikeys)
- Setup params (All params are required)
- Available params
  - api_key: The generated api key
  - uid: The unique identifier which can be configured in the fullstory script, under FS.identify
  - start_date: Date filter for eligible streams, enter

## Step 2: Set up the FullStory connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the FullStory connector and select **FullStory** from the Source type dropdown.
4. Enter your `api_key, uid and start_date`.
5. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `api_id, api_token and start_date`.
4. Click **Set up source**.

## Supported sync modes

The FullStory source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- calls
- company
- contacts
- numbers
- tags
- user_availablity
- users
- teams
- webhooks

## API method example

GET https://api.fullstory.com/segments/v1

## Performance considerations

FullStory [API reference](https://api.fullstory.com) has v1 at present. The connector as default uses v1.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                       | Subject        |
| :------ | :--------- | :------------------------------------------------- | :------------- |
| 0.2.14 | 2025-03-08 | [55299](https://github.com/airbytehq/airbyte/pull/55299) | Update dependencies |
| 0.2.13 | 2025-03-01 | [54968](https://github.com/airbytehq/airbyte/pull/54968) | Update dependencies |
| 0.2.12 | 2025-02-22 | [54398](https://github.com/airbytehq/airbyte/pull/54398) | Update dependencies |
| 0.2.11 | 2025-02-15 | [53768](https://github.com/airbytehq/airbyte/pull/53768) | Update dependencies |
| 0.2.10 | 2025-02-08 | [53359](https://github.com/airbytehq/airbyte/pull/53359) | Update dependencies |
| 0.2.9 | 2025-02-01 | [52870](https://github.com/airbytehq/airbyte/pull/52870) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52304](https://github.com/airbytehq/airbyte/pull/52304) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51657](https://github.com/airbytehq/airbyte/pull/51657) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51078](https://github.com/airbytehq/airbyte/pull/51078) | Update dependencies |
| 0.2.5 | 2025-01-04 | [50587](https://github.com/airbytehq/airbyte/pull/50587) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50050](https://github.com/airbytehq/airbyte/pull/50050) | Update dependencies |
| 0.2.3 | 2024-12-14 | [49524](https://github.com/airbytehq/airbyte/pull/49524) | Update dependencies |
| 0.2.2 | 2024-12-12 | [49156](https://github.com/airbytehq/airbyte/pull/49156) | Update dependencies |
| 0.2.1 | 2024-10-29 | [47794](https://github.com/airbytehq/airbyte/pull/47794) | Update dependencies |
| 0.2.0 | 2024-08-23 | [44612](https://github.com/airbytehq/airbyte/pull/44612) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-17 | [44222](https://github.com/airbytehq/airbyte/pull/44222) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43781](https://github.com/airbytehq/airbyte/pull/43781) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43688](https://github.com/airbytehq/airbyte/pull/43688) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43197](https://github.com/airbytehq/airbyte/pull/43197) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42694](https://github.com/airbytehq/airbyte/pull/42694) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42299](https://github.com/airbytehq/airbyte/pull/42299) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41798](https://github.com/airbytehq/airbyte/pull/41798) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41387](https://github.com/airbytehq/airbyte/pull/41387) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41190](https://github.com/airbytehq/airbyte/pull/41190) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40867](https://github.com/airbytehq/airbyte/pull/40867) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40333](https://github.com/airbytehq/airbyte/pull/40333) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40192](https://github.com/airbytehq/airbyte/pull/40192) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39195](https://github.com/airbytehq/airbyte/pull/39195) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38420](https://github.com/airbytehq/airbyte/pull/38420) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2023-04-25 | [Init](https://github.com/airbytehq/airbyte/pull/) | Initial commit |

</details>
