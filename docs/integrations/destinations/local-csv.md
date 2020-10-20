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

* The `destination_path` must start with `/local`. Any directory nesting within local will be mapped onto the local mount. By default, the local mount is mounted onto `/tmp/airbyte_local`. This is controlled by the `LOCAL_ROOT` env variable in the `.env` file. If `destination_path` is set to `/local/cars/models` and the local mount is using the `/tmp/airbyte_local` default, then data will be written to `/tmp/airbyte_local/cars/models` directory.

