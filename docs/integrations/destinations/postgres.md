# Postgres

## Overview

The Airbyte Postgres destination allows you to sync data to Postgres.

This Postgres destination is based on the [Singer Postgres Target](https://github.com/datamill-co/target-postgres).

### Sync overview

#### Output schema

Each stream will be output into its own table in Postgres. Each table will contain 3 columns:

* `ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Postgres is `VARCHAR`.
* `emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Postgres is `TIMESTAMP WITH TIME ZONE`.
* `data`: a json blob representing with the event data. The column type in BigQuery is `JSONB`.

#### Features

This section should contain a table with the following format:

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |

## Getting started

### Requirements

To use the Postgres destination, you'll need:

* A Postgres server version 9.4 or above

### Setup guide

#### Network Access

Make sure your Postgres database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a Postgres user that can create tables and write rows. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the Postgres destination in Airbyte

You should now have all the requirements needed to configure Postgres as a destination in the UI. You'll need the following information to configure the Postgres destination:

* **Host**
* **Port**
* **Username**
* **Password**
* **Schema**
* **Database**
  * This database needs to exist within the schema provided.

