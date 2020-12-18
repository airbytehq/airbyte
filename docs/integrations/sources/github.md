# Github

## Overview

The Github source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Github source wraps the [Singer Github Tap](https://github.com/singer-io/tap-github).

### Output schema

Several output streams are available from this source \(commits, issues, pull\_requests, etc.\) For a comprehensive output schema [look at the Singer tap schema files](https://github.com/singer-io/tap-github/tree/master/tap_github/schemas).

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Github connector should not run into Github API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Github Account
* Github Personal Access Token.

### Setup guide

Log into Github and then generate a [personal access token](https://github.com/settings/tokens).

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

