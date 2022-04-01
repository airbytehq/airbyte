# Mailchimp

## Sync overview

### Output schema

The Mailchimp connector can be used to sync data for Mailchimp [Lists](https://mailchimp.com/developer/api/marketing/lists/get-list-info),
[Campaigns](https://mailchimp.com/developer/api/marketing/campaigns/get-campaign-info/),
and [Email Activity](https://mailchimp.com/developer/marketing/api/email-activity-reports/). 
The linked Mailchimp documentation contains a detailed description of the fields in each entity.

Please [create a Github issue](https://github.com/airbytehq/airbyte/issues/new/choose) to request support for syncing more Mailchimp entities.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `array` | `array` | the type of elements in the array is determined based on the mappings in this table |
| `date`, `time`, `datetime` | `string` |  |
| `int`, `float`, `number` | `number` |  |
| `object` | `object` | properties within objects are mapped based on the mappings in this table |
| `string` | `string` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- |:---------------------| :--- |
| Full Refresh Sync | Yes                  |  |
| Incremental Sync | Yes                  |  |
| Replicate Incremental Deletes | No                   |  |
| SSL connection | Yes                  | Enabled by default |
| Namespaces | No                   |  |

### Performance considerations

At the time of this writing, [Mailchimp does not impose rate limits](https://mailchimp.com/developer/guides/marketing-api-conventions/#throttling) 
on how much data is read from its API in a single sync process. However, Mailchimp enforces a maximum of 10 simultaneous 
connections to its API. This means that Airbyte will not be able to run more than 10 concurrent syncs from Mailchimp 
using API keys generated from the same account.

### Primary keys

There is `id` primary key for `Lists` and `Campaigns`. 
`Email Activity` hasn't primary key due to Mailchimp doesn't give it. 

### Incremental Deletes

We don't support Incremental Deletes for `Campaigns`, `Lists`, and `Email Activity` streams. 
Mailchimp doesn't give any information about deleted data in these streams.

## Getting started

### Requirements

For Apikey authorization:
* Mailchimp account 
* Mailchimp API key

For OAuth authorization:
* Mailchimp registered app
* Mailchimp client_id
* Mailchimp client_secret

### Setup guide

To start syncing Mailchimp data with Airbyte, you'll need to retrieve credentials. 
According to the requirements you can use an API key or OAuth2.0 application.

If you want to use an API key, please follow these Mailchimp steps:
* [Create account](https://mailchimp.com/developer/marketing/guides/quick-start/#create-an-account)
* [Generate API key](https://mailchimp.com/developer/marketing/guides/quick-start/#generate-your-api-key)

If you want to use [OAuth2.0](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/) creds, 
please [register your application](https://mailchimp.com/developer/marketing/guides/access-user-data-oauth-2/#register-your-application).

## Changelog

| Version | Date       | Pull Request | Subject                                                                  |
|:--------|:-----------| :--- |:-------------------------------------------------------------------------|
| 0.2.13  | 2022-03-23 | [11352](https://github.com/airbytehq/airbyte/pull/11352) | Update spec&docs                                                         |
| 0.2.12  | 2022-03-17 | [10975](https://github.com/airbytehq/airbyte/pull/10975) | Fix campaign's stream normalization                                      |
| 0.2.11  | 2021-12-24 | [7159](https://github.com/airbytehq/airbyte/pull/7159) | Add oauth2.0 support                                                     |
| 0.2.10  | 2021-12-21 | [9000](https://github.com/airbytehq/airbyte/pull/9000) | Update connector fields title/description                                |
| 0.2.9   | 2021-12-13 | [7975](https://github.com/airbytehq/airbyte/pull/7975) | Updated JSON schemas                                                     |
| 0.2.8   | 2021-08-17 | [5481](https://github.com/airbytehq/airbyte/pull/5481) | Remove date-time type from some fields                                   |
| 0.2.7   | 2021-08-03 | [5137](https://github.com/airbytehq/airbyte/pull/5137) | Source Mailchimp: fix primary key for email activities                   |
| 0.2.6   | 2021-07-28 | [5024](https://github.com/airbytehq/airbyte/pull/5024) | Source Mailchimp: handle records with no no "activity" field in response |
| 0.2.5   | 2021-07-08 | [4621](https://github.com/airbytehq/airbyte/pull/4621) | Mailchimp fix url-base                                                   |
| 0.2.4   | 2021-06-09 | [4285](https://github.com/airbytehq/airbyte/pull/4285) | Use datacenter URL parameter from apikey                                 |
| 0.2.3   | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE\_ENTRYPOINT for Kubernetes support                           |
| 0.2.2   | 2021-06-08 | [3415](https://github.com/airbytehq/airbyte/pull/3415) | Get Members activities                                                   |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning                                            |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties                                |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file                                  |

