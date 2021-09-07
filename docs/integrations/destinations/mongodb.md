# Mongodb

## Overview

The Airbyte MongoDB destination allows you to sync data to MongoDB.

## Sync overview

### Output schema of `destination-mongodb`

Each stream will be output into its own collection in MongoDB. Each collection will contain 3 fields:

* `_id`: an identifier assigned to each document that is processed. The filed type in MongoDB is `String`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The field type in MongoDB is `Timestamp`.
* `_airbyte_data`: a json blob representing with the event data. The field type in MongoDB is `Object`.
* 
#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

## Getting started

### Requirements

To use the MongoDB destination, you'll need:

* A MongoDB server

### Setup guide

#### **Permissions**

You need a MongoDB user that can create collections and write documents. We highly recommend creating an Airbyte-specific user for this purpose.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Setup the MongoDB destination in Airbyte

You should now have all the requirements needed to configure MongoDB as a destination in the UI. You'll need the following information to configure the MongoDB destination:

* **Host**
* **Port**
* **Database**
* **Username**
* **Password**

## Notes about MongoDB Naming Conventions

From [MongoDB Identifiers syntax](https://docs.mongodb.com/manual/reference/limits/):

#### Database Name Case Sensitivity

Since database names are case insensitive in MongoDB, database names cannot differ only by the case of the characters.

#### Restrictions on Database Names for Windows

For MongoDB deployments running on Windows, database names cannot contain any of the following characters: /\. "$*<>:|?*

Also database names cannot contain the null character.

#### Restrictions on Database Names for Unix and Linux Systems
For MongoDB deployments running on Unix and Linux systems, database names cannot contain any of the following characters: /\. "$

Also database names cannot contain the null character.

#### Length of Database Names

Database names cannot be empty and must have fewer than 64 characters.

#### Restriction on Collection Names

Collection names should begin with an underscore or a letter character, and cannot:

* contain the $.
* be an empty string (e.g. "").
* contain the null character.
* begin with the system. prefix. (Reserved for internal use.)