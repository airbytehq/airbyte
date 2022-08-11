# MongoDB

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | Yes |  |

## Prerequisites
- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your MongoDB connector to version `0.1.6` or newer


## Output Schema for `destination-mongodb`

Each stream will be output into its own collection in MongoDB. Each collection will contain 3 fields:

* `_id`: an identifier assigned to each document that is processed. The filed type in MongoDB is `String`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The field type in MongoDB is `Timestamp`.
* `_airbyte_data`: a json blob representing with the event data. The field type in MongoDB is `Object`.

## Getting Started \(Airbyte Cloud\)

Airbyte Cloud only supports connecting to your MongoDB instance with TLS encryption. Other than that, you can proceed with the open-source instructions below.

## Getting Started \(Airbyte Open-Source\)

#### Requirements

To use the MongoDB destination, you'll need:

* A MongoDB server

#### **Permissions**

You need a MongoDB user that can create collections and write documents. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the MongoDB destination in Airbyte

You should now have all the requirements needed to configure MongoDB as a destination in the UI. You'll need the following information to configure the MongoDB destination:

* **Standalone MongoDb instance**
  * Host: URL of the database
  * Port: Port to use for connecting to the database
  * TLS: indicates whether to create encrypted connection
* **Replica Set**
  * Server addresses: the members of a replica set
  * Replica Set: A replica set name
* **MongoDb Atlas Cluster**
  * Cluster URL: URL of a cluster to connect to
* **Database**
* **Username**
* **Password**

For more information regarding configuration parameters, please see [MongoDb Documentation](https://docs.mongodb.com/drivers/java/sync/v4.3/fundamentals/connection/).

## Naming Conventions

The following information comes from the [MongoDB Limits and Thresholds](https://docs.mongodb.com/manual/reference/limits/) documentation.

#### Database Name Case Sensitivity

Since database names are case insensitive in MongoDB, database names cannot differ only by the case of the characters.

#### Restrictions on Database Names for Windows

For MongoDB deployments running on Windows, database names cannot contain any of the following characters: /. "$_&lt;&gt;:\|?_

Also database names cannot contain the null character.

#### Restrictions on Database Names for Unix and Linux Systems

For MongoDB deployments running on Unix and Linux systems, database names cannot contain any of the following characters: /. "$

Also database names cannot contain the null character.

#### Length of Database Names

Database names cannot be empty and must have fewer than 64 characters.

#### Restriction on Collection Names

Collection names should begin with an underscore or a letter character, and cannot:

* contain the $.
* be an empty string \(e.g. ""\).
* contain the null character.
* begin with the system. prefix. \(Reserved for internal use.\)

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.6 | 2022-08-02 | [15211](https://github.com/airbytehq/airbyte/pull/15211) | Fix standard mode |
| 0.1.5 | 2022-07-27 | [14561](https://github.com/airbytehq/airbyte/pull/14561) | Change Airbyte Id from MD5 to SHA256 |
| 0.1.4 | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | (unpublished) Add `-XX:+ExitOnOutOfMemoryError` JVM option |
| 0.1.3 | 2021-12-30 | [8809](https://github.com/airbytehq/airbyte/pull/8809) | Update connector fields title/description |
| 0.1.2 | 2021-10-18 | [6945](https://github.com/airbytehq/airbyte/pull/6945) | Create a secure-only MongoDb destination |
| 0.1.1 | 2021-09-29 | [6536](https://github.com/airbytehq/airbyte/pull/6536) | Destination MongoDb: added support via TLS/SSL |

