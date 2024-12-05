# Local JSON

:::danger

This destination is meant to be used on a local workstation and won't work on Kubernetes

:::

## Overview

This destination writes data to a directory on the _local_ filesystem on the host running Airbyte. By default, data is written to `/tmp/airbyte_local`. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

### Sync Overview

#### Output schema

Each stream will be output into its own file. Each file will a collections of `json` objects containing 3 fields:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the extracted data.

#### Features

| Feature                        | Supported |     |
| :----------------------------- | :-------- | :-- |
| Full Refresh Sync              | Yes       |     |
| Incremental - Append Sync      | Yes       |     |
| Incremental - Append + Deduped | No        |     |
| Namespaces                     | No        |     |

#### Performance considerations

This integration will be constrained by the speed at which your filesystem accepts writes.

## Getting Started

The `destination_path` will always start with `/local` whether it is specified by the user or not. Any directory nesting within local will be mapped onto the local mount.

By default, the `LOCAL_ROOT` env variable in the `.env` file is set `/tmp/airbyte_local`.

The local mount is mounted by Docker onto `LOCAL_ROOT`. This means the `/local` is substituted by `/tmp/airbyte_local` by default.

:::caution

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::

### Example:

- If `destination_path` is set to `/local/cars/models`
- the local mount is using the `/tmp/airbyte_local` default
- then all data will be written to `/tmp/airbyte_local/cars/models` directory.

## Access Replicated Data Files

If your Airbyte instance is running on the same computer that you are navigating with, you can open your browser and enter [file:///tmp/airbyte_local](file:///tmp/airbyte_local) to look at the replicated data locally. If the first approach fails or if your Airbyte instance is running on a remote server, follow the following steps to access the replicated files:

1. Access the scheduler container using `docker exec -it airbyte-server bash`
2. Navigate to the default local mount using `cd /tmp/airbyte_local`
3. Navigate to the replicated file directory you specified when you created the destination, using `cd /{destination_path}`
4. List files containing the replicated data using `ls`
5. Execute `cat {filename}` to display the data in a particular file

You can also copy the output file to your host machine, the following command will copy the file to the current working directory you are using:

```text
docker cp airbyte-server:/tmp/airbyte_local/{destination_path}/{filename}.jsonl .
```

Note: If you are running Airbyte on Windows with Docker backed by WSL2, you have to use similar step as above or refer to this [link](/integrations/locating-files-local-destination.md) for an alternative approach.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                      |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------- |
| 0.2.11  | 2022-02-14 | [14641](https://github.com/airbytehq/airbyte/pull/14641) | Include lifecycle management |

</details>