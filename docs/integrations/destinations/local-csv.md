# Local CSV

## Overview

This destination writes data to a directory on the _local_ filesystem on the host running Dataline. By default, data is written to `/tmp/dataline_local`. To change this location, modify the `LOCAL_ROOT` environment variable for Dataline.

### Sync Overview
#### Output schema
This destination outputs files with the name of the stream and a timestamp. Each row will be written as a new line in the output CSV file.

#### Data Type Mapping
As the output is CSV, the only output type is `String`. All input fields with be converted to their `String` value.

| Dataline Type | Destination Type | Notes
| :--- | :--- | :--- |
| `string` | string |  |
| `number` | string |  |
| `int` | string |  |
| `boolean` | string |  |
| `object` | string | Objects will be serialized as json |

#### Features
This section should contain a table with the following format:

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |

#### Performance considerations
This integration will be constrained by the speed at which your filesystem accepts writes.

## Getting Started

### Requirements:
* The `destination_path` field in the configuration _must_ point to a directory that _already_ exists on the filesystem. This path will be concatenated onto the `LOCAL_ROOT`. e.g. If `LOCAL_ROOT = /tmp/dataline_local` and the user provides the value `cars/models`, then the directory `/tmp/dataline_local/cars/models` must already be created for this destination to work as intended.
