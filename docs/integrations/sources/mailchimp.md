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

