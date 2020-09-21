# Source Documentation Template

## Sync overview

### Output schema

Is the output schema fixed \(e.g., for an API like Stripe\)? If so, point to the source’s schema \(e.g., link to Stripe’s documentation\) or include it here directly.

Describe how the source schema is mapped to Airbyte concepts. An example description might be: “MagicDB tables become Airbyte Streams and MagicDB columns become Airbyte Fields. In addition, an extracted\_at column is appended to each row being read.”

### Data type mapping

This section should contain a table mapping each of the source's data types to Airbyte types. At the moment, Airbyte uses the same types used by Singer.

| Source Type | Airbyte Type | Notes |
| :--- | :--- | :--- |


Currently, Airbyte uses the same types as Singer: `string`, `int`, `number`, `boolean`, `object`.

### Features

This section should contain a table with the following format:

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync |  |  |
| Incremental Sync |  |  |
| Replicate deletes |  |  |
| For databases, WAL/Logical replication |  |  |
| SSL connection |  |  |
| SSH Tunnel Support |  |  |
| \(Any other source-specific features\) |  |  |

### Performance considerations

Could this source hurt the user's data source or put too much strain on it in certain circumstances? For example, if there are a lot of tables or rows in a table? What is the breaking point \(e.g., 100mm&gt; records\)? What can the user do to prevent this \(e.g., use a read-only replica, or schedule frequent syncs, etc.\)?

## Getting started

### Requirements

* What versions of this source does this implementation support \(e.g., `postgres v3.14 and above`\)? 
* What configurations, if any, are required on the source \(e.g., `buffer_size > 1024`\)?
* Network accessibility requirements.
* Credentials/authentication requirements \(e.g., a DB user with read permissions on certain tables\). 

### Setup guide

For each of the above high-level requirements as appropriate, add or point to a follow-along guide. See the Postgres source guide for an example.

For each major cloud provider we support, also add a follow-along guide for setting up Airbyte to connect to that destination. See the Postgres destination guide for an example of what this should look like.

