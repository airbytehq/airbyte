# Hubspot

## Overview

The Hubspot source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Hubspot source wraps the [Singer Hubspot Tap](https://github.com/singer-io/tap-hubspot).

### Output schema

Several output streams are available from this source \(campaigns, contacts, deals, etc.\) For a comprehensive output schema [look at the Singer tap schema files](https://github.com/singer-io/tap-hubspot/tree/master/tap_hubspot/schemas).

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
*There are two ways of performing auth with hubspot (api key and oauth):
    * For api key auth, in Hubspot, for the account to go settings -> integrations (under the account banner) -> api key. If you already have an api key you can use that. Otherwise generated a new one.
        * Note: The Hubspot [docs](https://legacydocs.hubspot.com/docs/methods/auth/oauth-overview) recommends that api key auth is only used for testing purposes.
    * For oauth follow the [oauth instruction](https://developers.hubspot.com/docs/api/oauth-quickstart-guide) in Hubspot to get client_id, client_secret, redirect_uri, and refresh_token.
