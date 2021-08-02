# HDFS

## Overview

This destination writes data to a file on an HDFS cluster.

Presently this destination is only able to connect to local clusters accessible over HTTP.

### Sync Overview

#### Output schema

Each stream will be output into its own file.
Each file will contain a collection of `json` objects which correspond directly with the data supplied by the source.

#### Features

| Feature | Supported |  |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

#### Performance considerations

This integration will be constrained by the write speed on the HDFS cluster.

## Getting Started

The `destination_path` can refer to any path that the associated account has write permissions to on the cluster.

The `user` is the "effective user" that will be used when writing the files to the cluster.

### Example:

If `destination_path` is set to `/myfolder/files` and the stream is named `mystream`, the resulting file will be `/myfolder/files/airbyte_json_mystream.jsonl`.

These files can then be seen in the HDFS Web UI or by launching an HDFS client on the cluster.