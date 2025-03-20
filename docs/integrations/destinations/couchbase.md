# Couchbase

This page contains the setup guide and reference information for the Couchbase destination connector.

## Overview

The Couchbase destination connector allows you to sync data to Couchbase, a distributed NoSQL database. Each stream is written to a collection in Couchbase, with support for both local clusters and Couchbase Capella (cloud service).

### Output schema

Each stream will be output into a collection in Couchbase. The connector follows these rules for data mapping:

* Each record is stored as a JSON document in Couchbase
* Stream name is used as the collection name (sanitized to comply with Couchbase naming rules)
* Each document contains:
  * `id`: A unique identifier (UUID or composite key for deduplication)
  * `type`: Set to "airbyte_record"
  * `stream`: The source stream name
  * `data`: The actual record data

### Features

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync            | Yes        |
| Incremental - Append Sync    | Yes        |
| Incremental - Dedupe Sync    | Yes        |
| Namespaces                   | Yes        |

### Performance considerations

* The connector uses batch operations for better performance
* Primary indexes are automatically created for each collection
* For large datasets, consider using incremental sync modes
* Adjust the batch size if needed (default: 1000 documents)

## Getting started

### Requirements

#### For Local Cluster
1. Couchbase Server 7.0 or later installed
2. A bucket created in Couchbase
3. Username and password with appropriate permissions:
   * Data Reader (`data_reader`)
   * Data Writer (`data_writer`)
   * Query Manager (`query_manage_index`)

#### For Capella (Cloud)
1. A Couchbase Capella account
2. Database access credentials:
   * Database username
   * Database password
3. A bucket created in your Capella cluster
4. Allow list the IP addresses that Airbyte will connect from

### Setup guide

#### Local Cluster Setup

1. **Install Couchbase Server**
   * Download and install [Couchbase Server Community or Enterprise](https://www.couchbase.com/downloads/)
   * Follow the installation wizard for your platform
   * Access the web console at `http://localhost:8091`

2. **Create Resources**
   * In the Couchbase Web Console, go to "Buckets" and click "Add Bucket"
   * Enter the bucket details:
      * Name: mybucket
      * Memory Quota: Set appropriate size (e.g. 100 MB)
      * Bucket Type: Couchbase
      * Click "Add Bucket" to create

3. **Configure in Airbyte**
   * Connection String: Enter your Couchbase connection string (e.g. `couchbase://localhost`)
   * Username: Enter your database username (e.g. `airbyte_user`)
   * Password: Enter your database password (e.g. `your_secure_password`)
   * Bucket: Enter your bucket name (e.g. `my_bucket`)
   * Scope: Enter your scope name (defaults to `_default`)

#### Capella Setup

1. **Create Capella Resources**
   * Log in to [Couchbase Capella](https://cloud.couchbase.com)
   * Create a new database or use an existing one
   * Create a bucket for your data

2. **Create Database Credentials**
   * In Capella, go to "Security → Database Access"
   * Click "Create Database Credential"
   * Save the username and password

3. **Allow List IP Addresses**
   * In Capella, go to "Security → Network Security"
   * Add the IP addresses that Airbyte will connect from
   * [Get the IPs from Airbyte documentation](https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#allowlist-ip-addresses)

4. **Get Connection Details**
   * In Capella, go to "Connect"
   * Copy the connection string

5. **Configure in Airbyte**
   * Connection String: Your Capella connection string
   * Username: Database username
   * Password: Database password
   * Bucket: Your bucket name
   * Scope: `_default` (or your custom scope)

### Connection Configuration

| Parameter        | Description                                                                                     | Example                                            |
|:----------------|:------------------------------------------------------------------------------------------------|:--------------------------------------------------|
| Connection String| The connection string to your Couchbase cluster                                                  | `couchbase://localhost` or Capella connection string|
| Username        | Database username with required permissions                                                       | `airbyte`                                          |
| Password        | Database password                                                                                | `password`                                         |
| Bucket          | The name of the bucket to sync data to                                                          | `mybucket`                                         |
| Scope           | The scope within the bucket (optional, defaults to `_default`)                                   | `_default`                                         |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                 |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------------------|
| 0.1.1 | 2025-03-08 | [55354](https://github.com/airbytehq/airbyte/pull/55354) | Update dependencies |
| 0.1.0   | 2024-01-20 | [#xxxxx](https://github.com/airbytehq/airbyte/pull/xxxxx) | Initial release of the Couchbase destination connector                   |
