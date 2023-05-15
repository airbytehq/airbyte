# Local CSV

:::danger

This destination is meant to be used on a local workstation and won't work on Kubernetes

:::

## Overview

This destination writes data to a directory on the _local_ filesystem on the host running Airbyte. By default, data is written to `/tmp/airbyte_local`. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

:::caution

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::

### Sync Overview

#### Output schema

Each stream will be output into its own file. Each file will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
* `_airbyte_data`: a json blob representing with the event data.

#### Features

| Feature | Supported |  |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | No | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | No |  |

#### Performance considerations

This integration will be constrained by the speed at which your filesystem accepts writes.

## Getting Started

The `destination_path` will always start with `/local` whether it is specified by the user or not. Any directory nesting within local will be mapped onto the local mount.

By default, the `LOCAL_ROOT` env variable in the `.env` file is set `/tmp/airbyte_local`.

The local mount is mounted by Docker onto `LOCAL_ROOT`. This means the `/local` is substituted by `/tmp/airbyte_local` by default.

### Example:

* If `destination_path` is set to `/local/cars/models`
* the local mount is using the `/tmp/airbyte_local` default
* then all data will be written to `/tmp/airbyte_local/cars/models` directory.

## Access Replicated Data Files

If your Airbyte instance is running on the same computer that you are navigating with, you can open your browser and enter [file:///tmp/airbyte\_local](file:///tmp/airbyte_local) to look at the replicated data locally. If the first approach fails or if your Airbyte instance is running on a remote server, follow the following steps to access the replicated files:

1. Access the scheduler container using `docker exec -it airbyte-server bash`
2. Navigate to the default local mount using `cd /tmp/airbyte_local`
3. Navigate to the replicated file directory you specified when you created the destination, using `cd /{destination_path}`
4. List files containing the replicated data using `ls`
5. Execute `cat {filename}` to display the data in a particular file

You can also copy the output file to your host machine, the following command will copy the file to the current working directory you are using:

```text
docker cp airbyte-server:/tmp/airbyte_local/{destination_path}/{filename}.csv .
```

Note: If you are running Airbyte on Windows with Docker backed by WSL2, you have to use similar step as above or refer to this [link](../../operator-guides/locating-files-local-destination.md) for an alternative approach.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------|
| 1.0.0   | 2022-12-20 | [17998](https://github.com/airbytehq/airbyte/pull/17998) | Breaking changes: non backwards compatible. Adds delimiter dropdown.            |
| 0.2.10  | 2022-06-20 | [13932](https://github.com/airbytehq/airbyte/pull/13932) | Merging published connector changes                                             |
| 0.2.9   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add ExitOnOutOfMemoryError to java connectors and bump versions                 |
| 0.2.8   | 2021-07-21 | [3555](https://github.com/airbytehq/airbyte/pull/3555)   | Checkpointing: Partial Success in BufferedStreamConsumer (Destination)          |
| 0.2.7   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | add AIRBYTE_ENTRYPOINT for kubernetes support                                   |
| 0.2.6   | 2021-05-25 | [3290](https://github.com/airbytehq/airbyte/pull/3290)   | Checkpointing: Worker use destination (instead of source) for state             |
| 0.2.5   | 2021-05-10 | [3327](https://github.com/airbytehq/airbyte/pull/3327)   | don't split lines on LSEP unicode characters when reading lines in destinations |
| 0.2.4   | 2021-05-10 | [3289](https://github.com/airbytehq/airbyte/pull/3289)   | bump all destination versions to support outputting messages                    |
| 0.2.3   | 2021-03-31 | [2668](https://github.com/airbytehq/airbyte/pull/2668)   | Add SupportedDestinationSyncModes to destination specs objects                  |
| 0.2.2   | 2021-03-19 | [2460](https://github.com/airbytehq/airbyte/pull/2460)   | Destinations supports destination sync mode                                     |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Upgrade all connectors (0.2.0) so protocol allows future / unknown properties   |
| 0.1.8   | 2021-01-29 | [1882](https://github.com/airbytehq/airbyte/pull/1882)   | Local File Destinations UX change with destination paths                        |
| 0.1.7   | 2021-01-20 | [1737](https://github.com/airbytehq/airbyte/pull/1737)   | Rename destination tables                                                       |
| 0.1.6   | 2021-01-19 | [1708](https://github.com/airbytehq/airbyte/pull/1708)   | Add metadata prefix to destination internal columns                             |
| 0.1.5   | 2020-12-12 | [1294](https://github.com/airbytehq/airbyte/pull/1294)   | Incremental CSV destination                                                     |
| 0.1.4   | 2020-11-30 | [1038](https://github.com/airbytehq/airbyte/pull/1038)   | Change jdbc sources to discover more than standard schemas                      |
| 0.1.3   | 2020-11-20 | [1021](https://github.com/airbytehq/airbyte/pull/1021)   | Incremental Docs and Data Model Update                                          |
| 0.1.2   | 2020-11-18 | [998](https://github.com/airbytehq/airbyte/pull/998)     | Adding incremental to the data model                                            |
| 0.1.1   | 2020-11-10 | [895](https://github.com/airbytehq/airbyte/pull/895)     | bump versions: all destinations and source exchange rate                        |
| 0.1.0   | 2020-10-21 | [676](https://github.com/airbytehq/airbyte/pull/676)     | Integrations Reorganization: Connectors                                         |

