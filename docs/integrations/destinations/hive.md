# Apache Hive

This page guides you through the process of setting up the Apache Hive destination connector.

## Prerequisites

This Apache Hive destination connector has two replication strategies:

1. SQL: Replicates data via SQL INSERT queries. This leverages [Impyla](https://github.com/cloudera/impyla/tree/master/impala) to execute queries directly on Apache Hive [Engines](https://hive.apache.org). **Not recommended for production workloads as this does not scale well**.

2. S3: Replicates data by first uploading data to an S3 bucket, creating an External Table and writing into a final Raw Table. This is the recommended loading approach for large amounts of data. Requires an S3 bucket and credentials in addition to Apache Hive credentials.

Airbyte automatically picks an approach depending on the given configuration - if S3 configuration is present, Airbyte will use the S3 strategy.

For S3 strategy:

```
      "host": {
        "type": "string",
        "description": "Host name"
      },
      "port": {
        "type": "integer",
        "description": "Port number"
      },
      "auth_type": {
        "type": "string",
        "description": "LDAP, Kerberos"
      },
      "use_http_transport": {
        "type": "string",
        "description": "Use HTTP Transport"
      },
      "user": {
        "type": "string",
        "description": "User"
      },
      "password": {
        "type": "string",
        "description": "Password"
      },
      "use_ssl": {
        "type": "string",
        "description": "Use SSL"
      },
      "http_path": {
        "type": "string",
        "description": "HTTP path"
      },
```

## Setup guide

## Supported sync modes

The Apache Hive destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
- Full Refresh
- Incremental - Append Sync


## Connector-specific features & highlights


### Output schema

Each stream will be output into its own row in Apache Hive. Each table will contain 3 columns:

* `airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in Apache Hive is `STRING`.
* `airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in Apache Hive is `STRING`.
* `airbyte_data`: a json blob representing the event data. The column type in Apache Hive is `STRING` but can be be parsed with Hive's JSON functions.


## Changelog

| Version | Date       | Pull Request | Subject |
|:--------|:-----------| :-----       | :------ |
| 0.1.0  | 2022-10-18 | | New Destination: Apache Hive |
| 0.1.1  | 2022-11-29 | | Code Clean up and Public PR |

