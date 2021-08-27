# Mailchimp

## Sync overview

### Output schema

The Mailchimp connector can be used to sync data for Mailchimp [Lists](https://mailchimp.com/developer/api/marketing/lists/get-list-info) and [Campaigns](https://mailchimp.com/developer/api/marketing/campaigns/get-campaign-info/). The linked Mailchimp documentation contains detailed description on the fields in each entity.

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
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Coming soon |  |
| Replicate Incremental Deletes | Coming soon |  |
| SSL connection | Yes | Enabled by default |
| Namespaces | No |  |

### Performance considerations

At the time of this writing, [Mailchimp does not impose rate limits](https://mailchimp.com/developer/guides/marketing-api-conventions/#throttling) on how much data is read form its API in a single sync process. However, Mailchimp enforces a maximum of 10 simultaneous connections to its API. This means that Airbyte will not be able to run more than 10 concurrent syncs from Mailchimp using API keys generated from the same account.

## Getting started

### Requirements

* Mailchimp account 
* Mailchimp API key

### Setup guide

To start syncing Mailchimp data with Airbyte, you'll need two things:

1. Your Mailchimp username. Often this is just the email address or username you use to sign into Mailchimp. 
2. A Mailchimp API Key. Follow the [Mailchimp documentation for generating an API key](https://mailchimp.com/help/about-api-keys/).

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.8   | 2021-08-17 | [5481](https://github.com/airbytehq/airbyte/pull/5481) | Remove date-time type from some fields |
| 0.2.7   | 2021-08-03 | [5137](https://github.com/airbytehq/airbyte/pull/5137) | Source Mailchimp: fix primary key for email activities |
| 0.2.6   | 2021-07-28 | [5024](https://github.com/airbytehq/airbyte/pull/5024) | Source Mailchimp: handle records with no no "activity" field in response |
| 0.2.5   | 2021-07-08 | [4621](https://github.com/airbytehq/airbyte/pull/4621) | Mailchimp fix url-base |
| 0.2.4   | 2021-06-09 | [4285](https://github.com/airbytehq/airbyte/pull/4285) | Use datacenter URL parameter from apikey |
| 0.2.3   | 2021-06-08 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support  |
| 0.2.2   | 2021-06-08 | [3415](https://github.com/airbytehq/airbyte/pull/3415) | Get Members activities |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
