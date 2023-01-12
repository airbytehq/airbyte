# Databend

## Overview

The Databend source allows you to sync your data from [Databend](https://www.databend.rs/). Only Full refresh is supported at the moment.

The connector is built on top of a pure Python [databend-py](https://pypi.org/project/databend-py/) and does not require additonal dependencies.

#### Resulting schema

The Databend source does not alter schema present in your database. Depending on the destination connected to this source, however, the result schema may be altered. See the destination's documentation for more details.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | No |  |

## Getting started

### Requirements

1. An existing AWS account


### Setup guide

1. Create a Databend Cloud account following the [guide](https://docs.databend.com/getting-started/quick-start#create-a-databend-cloud-account)

1. [Load data](https://docs.databend.com/Data-integration-and-transformation/)

1. You can follow the [Connecting to a Warehouse docs](https://docs.databend.com/using-databend-cloud/warehouses/connecting-a-warehouse) to get the user, password, host etc.

Or You can create such a user by running:

GRANT CREATE ON * TO airbyte_user;

Make sure the Databend user with the following permissions:

can create tables and write rows.
can create databases e.g:
You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

#### You should now have the following

1. An existing Databend account
1. Connection parameters handy
    1. Username
    1. Password
    1. Host
    1. Database 
    1. Table

You can now use the Airbyte Databend source.

## Changelog

| Version | Date       | Pull Request | Subject                |
| :--- |:-----------|:-------------|:-----------------------|
| 0.1.0 | 2023-01-xx | waiting      | Create Databend source |