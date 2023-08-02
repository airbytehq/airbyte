
# DuckDB 

:::danger

This destination is meant to be used on a local workstation and won't work on Kubernetes

:::

## Overview

[DuckDB](https://duckdb.org/) is an in-process SQL OLAP database management system and this destination is meant to use locally if you have multiple smaller sources such as GitHub repos, some social media and local CSVs or files you want to run analytics workloads on.

This destination writes data to a file on the _local_ filesystem on the host running Airbyte. By default, data is written to `/tmp/airbyte_local`. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

### Sync Overview

#### Output schema

If you set [Normalization](https://docs.airbyte.com/understanding-airbyte/basic-normalization/), source data will be normalized to a tabular form. Let's say you have a source such as GitHub with nested JSONs; the Normalization ensures you end up with tables and columns. Suppose you have a many-to-many relationship between the users and commits. Normalization will create separate tables for it. The end state is the [third normal form](https://en.wikipedia.org/wiki/Third_normal_form) (3NF).

Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
* `_airbyte_data`: a json blob representing with the event data.

#### Features

| Feature | Supported |  |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No |  |
| Namespaces | No |  |

#### Performance consideration

This integration will be constrained by the speed at which your filesystem accepts writes.

## Getting Started

The `destination_path` will always start with `/local` whether it is specified by the user or not. Any directory nesting within local will be mapped onto the local mount.

By default, the `LOCAL_ROOT` env variable in the `.env` file is set `/tmp/airbyte_local`.

The local mount is mounted by Docker onto `LOCAL_ROOT`. This means the `/local` is substituted by `/tmp/airbyte_local` by default.

:::caution

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::


### Example:

* If `destination_path` is set to `/local/destination.duckdb`
* the local mount is using the `/tmp/airbyte_local` default
* then all data will be written to `/tmp/airbyte_local/destination.duckdb`.

## Access Replicated Data Files

If your Airbyte instance is running on the same computer that you are navigating with, you can open your browser and enter [file:///tmp/airbyte\_local](file:///tmp/airbyte_local) to look at the replicated data locally. If the first approach fails or if your Airbyte instance is running on a remote server, follow the following steps to access the replicated files:

1. Access the scheduler container using `docker exec -it airbyte-server bash`
2. Navigate to the default local mount using `cd /tmp/airbyte_local`
3. Navigate to the replicated file directory you specified when you created the destination, using `cd /{destination_path}`
4. Execute `duckdb {filename}` to access the data in a particular database file.

You can also copy the output file to your host machine, the following command will copy the file to the current working directory you are using:

```text
docker cp airbyte-server:/tmp/airbyte_local/{destination_path} .
```

Note: If you are running Airbyte on Windows with Docker backed by WSL2, you have to use similar step as above or refer to this [link](../../operator-guides/locating-files-local-destination.md) for an alternative approach.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-10-14 | [17494](https://github.com/airbytehq/airbyte/pull/17494) | New DuckDB destination |

