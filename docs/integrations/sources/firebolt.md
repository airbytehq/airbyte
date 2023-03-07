# Firebolt

## Overview

The Firebolt source allows you to sync your data from [Firebolt](https://www.firebolt.io/). Only Full refresh is supported at the moment.

The connector is built on top of a pure Python [firebolt-sdk](https://pypi.org/project/firebolt-sdk/) and does not require additonal dependencies.

#### Resulting schema

The Firebolt source does not alter schema present in your database. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | No |  |

## Getting started

### Requirements

1. An existing AWS account


### Setup guide

1. Create a Firebolt account following the [guide](https://docs.firebolt.io/managing-your-account/creating-an-account.html)

1. Follow the getting started [tutorial](https://docs.firebolt.io/getting-started.html) to setup a database

1. [Load data](https://docs.firebolt.io/loading-data/loading-data.html)

1. Create an Analytics (read-only) engine as described in [here](https://docs.firebolt.io/working-with-engines/working-with-engines-using-the-firebolt-manager.html)


#### You should now have the following

1. An existing Firebolt account
1. Connection parameters handy
    1. Username
    1. Password
    1. Account, in case of a multi-account setup (Optional)
    1. Host (Optional)
    1. Engine (Optional), preferably Analytics/read-only
1. A running engine (if an engine is stopped or booting up you won't be able to connect to it)
1. Your data in either [Fact or Dimension](https://docs.firebolt.io/working-with-tables.html#fact-and-dimension-tables) tables.

You can now use the Airbyte Firebolt source.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.0 | 2022-09-09 | https://github.com/airbytehq/airbyte/pull/16583 | Reading from views |
| 0.1.0 | 2022-04-28 | https://github.com/airbytehq/airbyte/pull/13874 | Create Firebolt source |