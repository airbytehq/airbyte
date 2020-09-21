# Local CSV

## Overview

This destination writes data to a directory on the _local_ filesystem on the host running Airbyte. By default, data is written to `/tmp/airbyte_local`. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

### Sync Overview

#### Output schema

This destination outputs files with the name of the stream and a timestamp. Each row will be written as a new line in the output CSV file.

#### Data Type Mapping

As the output is CSV, the only output type is `String`. All input fields with be converted to their `String` value.

| Airbyte Type | Destination Type | Notes |
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

* The `destination_path` field will be appended to `LOCAL_ROOT`. e.g. If `LOCAL_ROOT = /tmp/airbyte_local` and the user provides the value `cars/models`, then data will be written to `/tmp/airbyte_local/cars/models`. By default `LOCAL_ROOT = /tmp/airbyte_local`.

