# Mailchimp

This page guides you through setting up the [Mailchimp](https://mailchimp.com/) source connector.

## Prerequisites

<!-- env:cloud -->

#### For Airbyte Cloud

- Access to a valid Mailchimp account. If you are not an Owner/Admin of the account, you must be [granted Admin access](https://mailchimp.com/help/manage-user-levels-in-your-account/#Grant_account_access) by the account's Owner/Admin.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source

- A valid Mailchimp **API Key** (recommended) or OAuth credentials: **Client ID**, **Client Secret** and **Access Token**

<!-- /env:oss -->

## Setup guide

<!-- env:oss -->

### Airbyte Open Source: Generate a Mailchimp API key

1. Navigate to the API Keys section of your Mailchimp account.
2. Click **Create New Key**, and give the key a name to help you identify it. You won't be able to see or copy the key once you finish generating it, so be sure to copy the key and store it in a secure location.

For more information on Mailchimp API Keys, please refer to the [official Mailchimp docs](https://mailchimp.com/help/about-api-keys/#api+key+security). If you want to use OAuth authentication with Airbyte Open Source, please follow the steps laid out [here](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/) to obtain your OAuth **Client ID**, **Client Secret** and **Access Token**.

<!-- /env:oss -->

## Set up the Mailchimp source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. Find and select **Mailchimp** from the list of available sources.
4. Enter a name for your source.
5. You can use OAuth or an API key to authenticate your Mailchimp account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.

<!-- env:cloud -->

- To authenticate using OAuth for Airbyte Cloud, click **Authenticate your Mailchimp account** and follow the instructions to sign in with Mailchimp and authorize your account.

<!-- /env:cloud -->

<!-- env:oss -->

- To authenticate using an API key for Airbyte Open Source, select **API key** from the Authentication dropdown and enter the [API key](https://mailchimp.com/developer/marketing/guides/quick-start/#generate-your-api-key) for your Mailchimp account.
- To authenticate using OAuth credentials, select **Oauth2.0** from the dropdown and enter the **Client ID**, **Client Secret** and **Access Token** you obtained.

<!-- /env:oss -->

6. (Optional) You may optionally provide an **Incremental Sync Start Date** using the provided datepicker, or by programmatically entering a UTC date-time in the format `YYYY-MM-DDThh:mm:ss.sssZ`. If set, only data generated on or after the configured date-time will be synced. Leaving this field blank will sync all data returned from the API.
7. Click **Set up source** and wait for the tests to complete.

<HideInUI>

## Supported streams

The Mailchimp source connector supports the following streams and [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

| Stream                                                                                                             | Full Refresh | Incremental |
| :----------------------------------------------------------------------------------------------------------------- | :----------- | :---------- |
| [Automations](https://mailchimp.com/developer/marketing/api/automation/list-automations/)                          | ✓            | ✓           |
| [Campaigns](https://mailchimp.com/developer/marketing/api/campaigns/get-campaign-info/)                            | ✓            | ✓           |
| [Email Activity](https://mailchimp.com/developer/marketing/api/email-activity-reports/list-email-activity/)        | ✓            | ✓           |
| [Interests](https://mailchimp.com/developer/marketing/api/interests/list-interests-in-category/)                   | ✓            |             |
| [Interest Categories](https://mailchimp.com/developer/marketing/api/interest-categories/list-interest-categories/) | ✓            |             |
| [Lists](https://mailchimp.com/developer/api/marketing/lists/get-list-info)                                         | ✓            | ✓           |
| [List Members](https://mailchimp.com/developer/marketing/api/list-members/list-members-info/)                      | ✓            | ✓           |
| [Reports](https://mailchimp.com/developer/marketing/api/reports/list-campaign-reports/)                            | ✓            | ✓           |
| [Segments](https://mailchimp.com/developer/marketing/api/list-segments/list-segments/)                             | ✓            | ✓           |
| [Segment Members](https://mailchimp.com/developer/marketing/api/list-segment-members/list-members-in-segment/)     | ✓            | ✓           |
| [Tags](https://mailchimp.com/developer/marketing/api/lists-tags-search/search-for-tags-on-a-list-by-name/)         | ✓            |             |
| [Unsubscribes](https://mailchimp.com/developer/marketing/api/unsub-reports/list-unsubscribed-members/)             | ✓            | ✓           |

### A note on primary keys

The `EmailActivity` and `Unsubscribes` streams do not have an `id` primary key, and therefore use the following composite keys as unique identifiers:

- EmailActivity [`email_id`, `action`, `timestamp`]
- Unsubscribes [`campaign_id`, `email_id`, `timestamp`]

All other streams contain an `id` primary key.

## Data type mapping

| Integration Type     | Airbyte Type              | Notes                                                                               |
|:---------------------|:--------------------------|:------------------------------------------------------------------------------------|
| `array`              | `array`                   | the type of elements in the array is determined based on the mappings in this table |
| `string`             | `string`                  |                                                                                     |
| `float`, `number`    | `number`                  |                                                                                     |
| `integer`            | `integer`                 |                                                                                     |
| `object`             | `object`                  | properties within objects are mapped based on the mappings in this table            |
| `string` (timestamp) | `timestamp_with_timezone` | Mailchimp timestamps are formatted as `YYYY-MM-DDTHH:MM:SS+00:00`                   |

## Limitations & Troubleshooting

<details>
<summary>

Expand to see details about Mailchimp connector limitations and troubleshooting

</summary>

### Connector limitations

[Mailchimp does not impose rate limits](https://mailchimp.com/developer/guides/marketing-api-conventions/#throttling) on how much data is read from its API in a single sync process. However, Mailchimp enforces a maximum of 10 simultaneous connections to its API, which means that Airbyte is unable to run more than 10 concurrent syncs from Mailchimp using API keys generated from the same account.

</details>

## Tutorials

Now that you have set up the Mailchimp source connector, check out the following Mailchimp tutorial:

- [Build a data ingestion pipeline from Mailchimp to Snowflake](https://airbyte.com/tutorials/data-ingestion-pipeline-mailchimp-snowflake)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                    |
|---------|------------|----------------------------------------------------------|----------------------------------------------------------------------------|
| 2.0.25 | 2025-01-11 | [51215](https://github.com/airbytehq/airbyte/pull/51215) | Update dependencies |
| 2.0.24 | 2025-01-04 | [50894](https://github.com/airbytehq/airbyte/pull/50894) | Update dependencies |
| 2.0.23 | 2024-12-28 | [50633](https://github.com/airbytehq/airbyte/pull/50633) | Update dependencies |
| 2.0.22 | 2024-12-21 | [50139](https://github.com/airbytehq/airbyte/pull/50139) | Update dependencies |
| 2.0.21 | 2024-12-14 | [49148](https://github.com/airbytehq/airbyte/pull/49148) | Update dependencies |
| 2.0.20 | 2024-11-22 | [45282](https://github.com/airbytehq/airbyte/pull/45282) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 2.0.19 | 2024-08-31 | [45031](https://github.com/airbytehq/airbyte/pull/45031) | Update dependencies |
| 2.0.18 | 2024-08-24 | [44708](https://github.com/airbytehq/airbyte/pull/44708) | Update dependencies |
| 2.0.17 | 2024-08-17 | [44323](https://github.com/airbytehq/airbyte/pull/44323) | Update dependencies |
| 2.0.16 | 2024-08-12 | [43752](https://github.com/airbytehq/airbyte/pull/43752) | Update dependencies |
| 2.0.15 | 2024-08-10 | [43554](https://github.com/airbytehq/airbyte/pull/43554) | Update dependencies |
| 2.0.14 | 2024-08-03 | [43228](https://github.com/airbytehq/airbyte/pull/43228) | Update dependencies |
| 2.0.13 | 2024-07-27 | [42683](https://github.com/airbytehq/airbyte/pull/42683) | Update dependencies |
| 2.0.12 | 2024-07-20 | [42381](https://github.com/airbytehq/airbyte/pull/42381) | Update dependencies |
| 2.0.11 | 2024-07-13 | [41683](https://github.com/airbytehq/airbyte/pull/41683) | Update dependencies |
| 2.0.10 | 2024-07-10 | [41399](https://github.com/airbytehq/airbyte/pull/41399) | Update dependencies |
| 2.0.9 | 2024-07-09 | [41152](https://github.com/airbytehq/airbyte/pull/41152) | Update dependencies |
| 2.0.8 | 2024-07-06 | [40897](https://github.com/airbytehq/airbyte/pull/40897) | Update dependencies |
| 2.0.7 | 2024-06-25 | [40320](https://github.com/airbytehq/airbyte/pull/40320) | Update dependencies |
| 2.0.6 | 2024-06-21 | [39937](https://github.com/airbytehq/airbyte/pull/39937) | Update dependencies |
| 2.0.5 | 2024-06-18 | [38868](https://github.com/airbytehq/airbyte/pull/38868) | Refactor:  use `client_side_incremental` feature |
| 2.0.4 | 2024-06-06 | [39202](https://github.com/airbytehq/airbyte/pull/39202) | [autopull] Upgrade base image to v1.2.2 |
| 2.0.3 | 2024-05-02 | [36649](https://github.com/airbytehq/airbyte/pull/36649) | Schema descriptions |
| 2.0.2 | 2024-04-25 | [37572](https://github.com/airbytehq/airbyte/pull/37572) | Fixed `start_date` format issue for the `email_activity` stream |
| 2.0.1 | 2024-04-19 | [37434](https://github.com/airbytehq/airbyte/pull/37434) | Fixed cursor format for the `email_activity` stream |
| 2.0.0 | 2024-04-01 | [35281](https://github.com/airbytehq/airbyte/pull/35281) | Migrate to Low-Code |
| 1.2.0 | 2024-03-28 | [36600](https://github.com/airbytehq/airbyte/pull/36600) | Migrate to latest Airbyte-CDK. |
| 1.1.2 | 2024-02-09 | [35092](https://github.com/airbytehq/airbyte/pull/35092) | Manage dependencies with Poetry. |
| 1.1.1 | 2024-01-11 | [34157](https://github.com/airbytehq/airbyte/pull/34157) | Prepare for airbyte-lib |
| 1.1.0 | 2023-12-20 | [32852](https://github.com/airbytehq/airbyte/pull/32852) | Add optional start_date for incremental streams |
| 1.0.0 | 2023-12-19 | [32836](https://github.com/airbytehq/airbyte/pull/32836) | Add airbyte-type to `datetime` columns and remove `._links` column |
| 0.10.0 | 2023-11-23 | [32782](https://github.com/airbytehq/airbyte/pull/32782) | Add SegmentMembers stream |
| 0.9.0 | 2023-11-17 | [32218](https://github.com/airbytehq/airbyte/pull/32218) | Add Interests, InterestCategories, Tags streams |
| 0.8.3 | 2023-11-15 | [32543](https://github.com/airbytehq/airbyte/pull/32543) | Handle empty datetime fields in Reports stream |
| 0.8.2 | 2023-11-13 | [32466](https://github.com/airbytehq/airbyte/pull/32466) | Improve error handling during connection check |
| 0.8.1 | 2023-11-06 | [32226](https://github.com/airbytehq/airbyte/pull/32226) | Unmute expected records test after data anonymisation |
| 0.8.0 | 2023-11-01 | [32032](https://github.com/airbytehq/airbyte/pull/32032) | Add ListMembers stream |
| 0.7.0 | 2023-10-27 | [31940](https://github.com/airbytehq/airbyte/pull/31940) | Implement availability strategy |
| 0.6.0 | 2023-10-27 | [31922](https://github.com/airbytehq/airbyte/pull/31922) | Add Segments stream |
| 0.5.0 | 2023-10-20 | [31675](https://github.com/airbytehq/airbyte/pull/31675) | Add Unsubscribes stream |
| 0.4.1 | 2023-05-02 | [25717](https://github.com/airbytehq/airbyte/pull/25717) | Handle unknown error in EmailActivity |
| 0.4.0 | 2023-04-11 | [23290](https://github.com/airbytehq/airbyte/pull/23290) | Add Automations stream |
| 0.3.5 | 2023-02-28 | [23464](https://github.com/airbytehq/airbyte/pull/23464) | Add Reports stream |
| 0.3.4 | 2023-02-06 | [22405](https://github.com/airbytehq/airbyte/pull/22405) | Revert extra logging |
| 0.3.3 | 2023-02-01 | [22228](https://github.com/airbytehq/airbyte/pull/22228) | Add extra logging |
| 0.3.2 | 2023-01-27 | [22014](https://github.com/airbytehq/airbyte/pull/22014) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.3.1 | 2022-12-20 | [20720](https://github.com/airbytehq/airbyte/pull/20720) | Use stream slices as a source for request params instead of a stream state |
| 0.3.0 | 2022-11-07 | [19023](https://github.com/airbytehq/airbyte/pull/19023) | Set primary key for Email Activity stream. |
| 0.2.15 | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states. |
| 0.2.14 | 2022-04-12 | [11352](https://github.com/airbytehq/airbyte/pull/11352) | Update documentation |
| 0.2.13 | 2022-04-11 | [11632](https://github.com/airbytehq/airbyte/pull/11632) | Add unit tests |
| 0.2.12 | 2022-03-17 | [10975](https://github.com/airbytehq/airbyte/pull/10975) | Fix campaign's stream normalization |
| 0.2.11 | 2021-12-24 | [7159](https://github.com/airbytehq/airbyte/pull/7159) | Add oauth2.0 support |
| 0.2.10 | 2021-12-21 | [9000](https://github.com/airbytehq/airbyte/pull/9000) | Update connector fields title/description |
| 0.2.9 | 2021-12-13 | [7975](https://github.com/airbytehq/airbyte/pull/7975) | Updated JSON schemas |
| 0.2.8 | 2021-08-17 | [5481](https://github.com/airbytehq/airbyte/pull/5481) | Remove date-time type from some fields |
| 0.2.7 | 2021-08-03 | [5137](https://github.com/airbytehq/airbyte/pull/5137) | Source Mailchimp: fix primary key for email activities |
| 0.2.6 | 2021-07-28 | [5024](https://github.com/airbytehq/airbyte/pull/5024) | Source Mailchimp: handle records with no no "activity" field in response |
| 0.2.5 | 2021-07-08 | [4621](https://github.com/airbytehq/airbyte/pull/4621) | Mailchimp fix url-base |
| 0.2.4 | 2021-06-09 | [4285](https://github.com/airbytehq/airbyte/pull/4285) | Use datacenter URL parameter from apikey |
| 0.2.3 | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support |
| 0.2.2 | 2021-06-08 | [3415](https://github.com/airbytehq/airbyte/pull/3415) | Get Members activities |
| 0.2.1 | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.0 | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.4 | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |

</details>

</HideInUI>
