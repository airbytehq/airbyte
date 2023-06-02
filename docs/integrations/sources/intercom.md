# Intercom

This page guides you through the process of setting up the Intercom source connector.

## Set up the Intercom connector 

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**. 
3. On the Set up the source page, select **Intercom** from the Source type dropdown.
4. Enter a name for your source.
5. For **Start date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
6. For Airbyte Cloud, click **Authenticate your Intercom account** to sign in with Intercom and authorize your account. 
   For Airbyte Open Source, enter your [Access Token](https://developers.intercom.com/building-apps/docs/authentication-types#section-how-to-get-your-access-token) to authenticate your account.
7. Click **Set up source**.

## Supported sync modes

The Intercom source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

 - Full Refresh
 - Incremental

## Supported Streams

The Intercom source connector supports the following streams:

* [Admins](https://developers.intercom.com/intercom-api-reference/reference#list-admins) \(Full table\)
* [Companies](https://developers.intercom.com/intercom-api-reference/reference#list-companies) \(Incremental\)
  * [Company Segments](https://developers.intercom.com/intercom-api-reference/reference#list-attached-segments-1) \(Incremental\)
* [Conversations](https://developers.intercom.com/intercom-api-reference/reference#list-conversations) \(Incremental\)
  * [Conversation Parts](https://developers.intercom.com/intercom-api-reference/reference#get-a-single-conversation) \(Incremental\)
* [Data Attributes](https://developers.intercom.com/intercom-api-reference/reference#data-attributes) \(Full table\)
  * [Customer Attributes](https://developers.intercom.com/intercom-api-reference/reference#list-customer-data-attributes) \(Full table\)
  * [Company Attributes](https://developers.intercom.com/intercom-api-reference/reference#list-company-data-attributes) \(Full table\)
* [Contacts](https://developers.intercom.com/intercom-api-reference/reference#list-contacts) \(Incremental\)
* [Segments](https://developers.intercom.com/intercom-api-reference/reference#list-segments) \(Incremental\)
* [Tags](https://developers.intercom.com/intercom-api-reference/reference#list-tags-for-an-app) \(Full table\)
* [Teams](https://developers.intercom.com/intercom-api-reference/reference#list-teams) \(Full table\)


## Performance considerations

The connector is restricted by normal Intercom [requests limitation](https://developers.intercom.com/intercom-api-reference/reference#rate-limiting).

The Intercom connector should not run into Intercom API limitations under normal usage. [Create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                       |
|:--------| :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------- |
| 0.2.1   | 2023-05-25 | [26571](https://github.com/airbytehq/airbyte/pull/26571) | Remove authSpecification from spec.json in favour of advancedAuth                             |
| 0.2.0   | 2023-04-05 | [23013](https://github.com/airbytehq/airbyte/pull/23013) | Migrated to Low-code (YAML Frramework)                                                        |
| 0.1.33  | 2023-03-20 | [22980](https://github.com/airbytehq/airbyte/pull/22980) | Specified date formatting in specification                                                    |
| 0.1.32  | 2023-02-27 | [22095](https://github.com/airbytehq/airbyte/pull/22095) | Extended `Contacts` schema adding `opted_out_subscription_types` property                     |
| 0.1.31  | 2023-02-17 | [23152](https://github.com/airbytehq/airbyte/pull/23152) | Add `TypeTransformer` to stream `companies`                                                   |
| 0.1.30  | 2023-01-27 | [22010](https://github.com/airbytehq/airbyte/pull/22010) | Set `AvailabilityStrategy` for streams explicitly to `None`                                   |
| 0.1.29  | 2022-10-31 | [18681](https://github.com/airbytehq/airbyte/pull/18681) | Define correct version for airbyte-cdk~=0.2                                                   |
| 0.1.28  | 2022-10-20 | [18216](https://github.com/airbytehq/airbyte/pull/18216) | Use airbyte-cdk~=0.2.0 with SQLite caching                                                    |
| 0.1.27  | 2022-08-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                 |
| 0.1.26  | 2022-08-18 | [16540](https://github.com/airbytehq/airbyte/pull/16540) | Fix JSON schema                                                                               |
| 0.1.25  | 2022-08-18 | [15681](https://github.com/airbytehq/airbyte/pull/15681) | Update Intercom API to v 2.5                                                                  |
| 0.1.24  | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas                                              |
| 0.1.23  | 2022-07-19 | [14830](https://github.com/airbytehq/airbyte/pull/14830) | Added `checkpoint_interval` for Incremental streams                                           |
| 0.1.22  | 2022-07-09 | [14554](https://github.com/airbytehq/airbyte/pull/14554) | Fixed `conversation_parts` stream schema definition                                           |
| 0.1.21  | 2022-07-05 | [14403](https://github.com/airbytehq/airbyte/pull/14403) | Refactored  `Conversations`, `Conversation Parts`, `Company Segments` to increase performance |
| 0.1.20  | 2022-06-24 | [14099](https://github.com/airbytehq/airbyte/pull/14099) | Extended `Contacts` stream schema with `sms_consent`,`unsubscribe_from_sms` properties        |
| 0.1.19  | 2022-05-25 | [13204](https://github.com/airbytehq/airbyte/pull/13204) | Fixed `conversation_parts` stream schema definition                                           |
| 0.1.18  | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                               |
| 0.1.17  | 2022-04-29 | [12374](https://github.com/airbytehq/airbyte/pull/12374) | Fixed filtering of conversation_parts                                                         |
| 0.1.16  | 2022-03-23 | [11206](https://github.com/airbytehq/airbyte/pull/11206) | Added conversation_id field to conversation_part records                                      |
| 0.1.15  | 2022-03-22 | [11176](https://github.com/airbytehq/airbyte/pull/11176) | Correct `check_connection` URL                                                                |
| 0.1.14  | 2022-03-16 | [11208](https://github.com/airbytehq/airbyte/pull/11208) | Improve 'conversations' incremental sync speed                                                |
| 0.1.13  | 2022-01-14 | [9513](https://github.com/airbytehq/airbyte/pull/9513)   | Added handling of scroll param when it expired                                                |
| 0.1.12  | 2021-12-14 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Updated fields and descriptions                                                               |
| 0.1.11  | 2021-12-13 | [8685](https://github.com/airbytehq/airbyte/pull/8685)   | Remove time.sleep for rate limit                                                              |
| 0.1.10  | 2021-12-10 | [8637](https://github.com/airbytehq/airbyte/pull/8637)   | Fix 'conversations' order and sorting. Correction of the companies stream                     |
| 0.1.9   | 2021-12-03 | [8395](https://github.com/airbytehq/airbyte/pull/8395)   | Fix backoff of 'companies' stream                                                             |
| 0.1.8   | 2021-11-09 | [7060](https://github.com/airbytehq/airbyte/pull/7060)   | Added oauth support                                                                           |
| 0.1.7   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                               |
| 0.1.6   | 2021-10-07 | [6879](https://github.com/airbytehq/airbyte/pull/6879)   | Corrected pagination for contacts                                                             |
| 0.1.5   | 2021-09-28 | [6082](https://github.com/airbytehq/airbyte/pull/6082)   | Corrected android\_last\_seen\_at field data type in schemas                                  |
| 0.1.4   | 2021-09-20 | [6087](https://github.com/airbytehq/airbyte/pull/6087)   | Corrected updated\_at field data type in schemas                                              |
| 0.1.3   | 2021-09-08 | [5908](https://github.com/airbytehq/airbyte/pull/5908)   | Corrected timestamp and arrays in schemas                                                     |
| 0.1.2   | 2021-08-19 | [5531](https://github.com/airbytehq/airbyte/pull/5531)   | Corrected pagination                                                                          |
| 0.1.1   | 2021-07-31 | [5123](https://github.com/airbytehq/airbyte/pull/5123)   | Corrected rate limit                                                                          |
| 0.1.0   | 2021-07-19 | [4676](https://github.com/airbytehq/airbyte/pull/4676)   | Release Intercom CDK Connector                                                                |
