# Mailchimp

This page guides you through setting up the Mailchimp source connector.

## Prerequisite

You can use [OAuth](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/) or an API key to authenticate your Mailchimp account. If you choose to authenticate with OAuth, [register](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/#register-your-application) your Mailchimp account.

## Set up the Mailchimp source connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Mailchimp** from the Source type dropdown.
4. Enter a name for your source.

6. You can use OAuth or an API key to authenticate your Mailchimp account. We recommend using OAuth for Airbyte Cloud and an API key for Airbyte Open Source.
    - To authenticate using OAuth for Airbyte Cloud, ensure you have [registered your Mailchimp account](#prerequisite) and then click **Authenticate your Mailchimp account** to sign in with Mailchimp and authorize your account. 
    - To authenticate using an API key for Airbyte Open Source, select **API key** from the Authentication dropdown and enter the [API key](https://mailchimp.com/developer/marketing/guides/quick-start/#generate-your-api-key) for your Mailchimp account.    
    :::note
    Check the [performance considerations](#performance-considerations) before using an API key.
    :::
7. Click **Set up source**.

## Supported sync modes

The Mailchimp source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

 - Full Refresh
 - Incremental

Airbyte doesn't support Incremental Deletes for the `Campaigns`, `Lists`, and `Email Activity` streams because Mailchimp doesn't provide any information about deleted data in these streams.

## Performance considerations

[Mailchimp does not impose rate limits](https://mailchimp.com/developer/guides/marketing-api-conventions/#throttling) on how much data is read from its API in a single sync process. However, Mailchimp enforces a maximum of 10 simultaneous connections to its API, which means that Airbyte is unable to run more than 10 concurrent syncs from Mailchimp using API keys generated from the same account.

## Supported streams

The Mailchimp source connector supports the following streams:

[Automations](https://mailchimp.com/developer/marketing/api/automation/list-automations/)
[Campaigns](https://mailchimp.com/developer/marketing/api/campaigns/get-campaign-info/)
[Email Activity](https://mailchimp.com/developer/marketing/api/email-activity-reports/list-email-activity/)
[Lists](https://mailchimp.com/developer/api/marketing/lists/get-list-info)
[ListMembers](https://mailchimp.com/developer/marketing/api/list-members/list-members-info/)
[Reports](https://mailchimp.com/developer/marketing/api/reports/list-campaign-reports/)
[Segments](https://mailchimp.com/developer/marketing/api/list-segments/list-segments/)
[Unsubscribes](https://mailchimp.com/developer/marketing/api/unsub-reports/list-unsubscribed-members/)

### A note on primary keys

The `EmailActivity` and `Unsubscribes` streams do not have an `id` primary key, and therefore use the following composite keys as unique identifiers:

- EmailActivity [`email_id`, `action`, `timestamp`]
- Unsubscribes [`campaign_id`, `email_id`, `timestamp`]

All other streams contain an `id` primary key.

## Data type mapping

| Integration Type           | Airbyte Type | Notes                                                                               |
|:---------------------------|:-------------|:------------------------------------------------------------------------------------|
| `array`                    | `array`      | the type of elements in the array is determined based on the mappings in this table |
| `date`, `time`, `datetime` | `string`     |                                                                                     |
| `int`, `float`, `number`   | `number`     |                                                                                     |
| `object`                   | `object`     | properties within objects are mapped based on the mappings in this table            |
| `string`                   | `string`     |                                                                                     |

## Tutorials

Now that you have set up the Mailchimp source connector, check out the following Mailchimp tutorial:

- [Build a data ingestion pipeline from Mailchimp to Snowflake](https://airbyte.com/tutorials/data-ingestion-pipeline-mailchimp-snowflake)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                    |
|---------|------------|----------------------------------------------------------|----------------------------------------------------------------------------|
| 0.8.2   | 2023-11-13 | [32466](https://github.com/airbytehq/airbyte/pull/32466) | Improve error handling during connection check                             |
| 0.8.1   | 2023-11-06 | [32226](https://github.com/airbytehq/airbyte/pull/32226) | Unmute expected records test after data anonymisation                      |
| 0.8.0   | 2023-11-01 | [32032](https://github.com/airbytehq/airbyte/pull/32032) | Add ListMembers stream                                                     |
| 0.7.0   | 2023-10-27 | [31940](https://github.com/airbytehq/airbyte/pull/31940) | Implement availability strategy                                            |
| 0.6.0   | 2023-10-27 | [31922](https://github.com/airbytehq/airbyte/pull/31922) | Add Segments stream                                                        |
| 0.5.0   | 2023-10-20 | [31675](https://github.com/airbytehq/airbyte/pull/31675) | Add Unsubscribes stream                                                    |
| 0.4.1   | 2023-05-02 | [25717](https://github.com/airbytehq/airbyte/pull/25717) | Handle unknown error in EmailActivity                                      |
| 0.4.0   | 2023-04-11 | [23290](https://github.com/airbytehq/airbyte/pull/23290) | Add Automations stream                                                     |
| 0.3.5   | 2023-02-28 | [23464](https://github.com/airbytehq/airbyte/pull/23464) | Add Reports stream                                                         |
| 0.3.4   | 2023-02-06 | [22405](https://github.com/airbytehq/airbyte/pull/22405) | Revert extra logging                                                       |
| 0.3.3   | 2023-02-01 | [22228](https://github.com/airbytehq/airbyte/pull/22228) | Add extra logging                                                          |
| 0.3.2   | 2023-01-27 | [22014](https://github.com/airbytehq/airbyte/pull/22014) | Set `AvailabilityStrategy` for streams explicitly to `None`                |
| 0.3.1   | 2022-12-20 | [20720](https://github.com/airbytehq/airbyte/pull/20720) | Use stream slices as a source for request params instead of a stream state |
| 0.3.0   | 2022-11-07 | [19023](https://github.com/airbytehq/airbyte/pull/19023) | Set primary key for Email Activity stream.                                 |
| 0.2.15  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                              |
| 0.2.14  | 2022-04-12 | [11352](https://github.com/airbytehq/airbyte/pull/11352) | Update documentation                                                       |
| 0.2.13  | 2022-04-11 | [11632](https://github.com/airbytehq/airbyte/pull/11632) | Add unit tests                                                             |
| 0.2.12  | 2022-03-17 | [10975](https://github.com/airbytehq/airbyte/pull/10975) | Fix campaign's stream normalization                                        |
| 0.2.11  | 2021-12-24 | [7159](https://github.com/airbytehq/airbyte/pull/7159)   | Add oauth2.0 support                                                       |
| 0.2.10  | 2021-12-21 | [9000](https://github.com/airbytehq/airbyte/pull/9000)   | Update connector fields title/description                                  |
| 0.2.9   | 2021-12-13 | [7975](https://github.com/airbytehq/airbyte/pull/7975)   | Updated JSON schemas                                                       |
| 0.2.8   | 2021-08-17 | [5481](https://github.com/airbytehq/airbyte/pull/5481)   | Remove date-time type from some fields                                     |
| 0.2.7   | 2021-08-03 | [5137](https://github.com/airbytehq/airbyte/pull/5137)   | Source Mailchimp: fix primary key for email activities                     |
| 0.2.6   | 2021-07-28 | [5024](https://github.com/airbytehq/airbyte/pull/5024)   | Source Mailchimp: handle records with no no "activity" field in response   |
| 0.2.5   | 2021-07-08 | [4621](https://github.com/airbytehq/airbyte/pull/4621)   | Mailchimp fix url-base                                                     |
| 0.2.4   | 2021-06-09 | [4285](https://github.com/airbytehq/airbyte/pull/4285)   | Use datacenter URL parameter from apikey                                   |
| 0.2.3   | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add AIRBYTE\_ENTRYPOINT for Kubernetes support                             |
| 0.2.2   | 2021-06-08 | [3415](https://github.com/airbytehq/airbyte/pull/3415)   | Get Members activities                                                     |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)   | Fix base connector versioning                                              |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Protocol allows future/unknown properties                                  |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046)   | Add connectors using an index YAML file                                    |
