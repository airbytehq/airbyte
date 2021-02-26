# Hubspot

## Overview

The Hubspot connector can be used to sync your Hubspot data. It supports full refresh sync.

### Output schema

Several output streams are available from this source:
* Campaigns
* Companies
* Contact Lists
* Contacts
* Contacts by Company
* Deal Pipelines
* Deals
* Email Events
* Engagements
* Forms
* Line Items
* Owners
* Products
* Quotes
* Subscription Changes
* Tickets
* Workflows

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The connector is restricted by normal Hubspot [rate limitations](https://legacydocs.hubspot.com/apps/api_guidelines).

## Getting started

### Requirements

* Hubspot Account
* Api credentials

### Setup guide

\*There are two ways of performing auth with hubspot \(api key and oauth\):

* For api key auth, in Hubspot, for the account to go settings -&gt; integrations \(under the account banner\) -&gt; api key. If you already have an api key you can use that. Otherwise generated a new one.
  * Note: The Hubspot [docs](https://legacydocs.hubspot.com/docs/methods/auth/oauth-overview) recommends that api key auth is only used for testing purposes.
* For oauth follow the [oauth instruction](https://developers.hubspot.com/docs/api/oauth-quickstart-guide) in Hubspot to get client\_id, client\_secret, redirect\_uri, and refresh\_token.

