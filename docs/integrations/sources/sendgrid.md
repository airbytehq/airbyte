# Sendgrid

## Overview

The Sendgrid source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source (campaigns, lists)
### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Sendgrid connector should not run into Sendgrid API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

### Performance considerations

The connector is restricted by normal Sendgrid [requests limitation](https://sendgrid.com/docs/API_Reference/Web_API_v3/How_To_Use_The_Web_API_v3/rate_limits.html).

## Getting started

### Requirements

* Sendgrid Account
* Api credentials

### Setup guide

Log into Sendgrid and go to Settings -&gt; API Keys. If you already have an api key you can use that. Otherwise generated a new one.

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.
