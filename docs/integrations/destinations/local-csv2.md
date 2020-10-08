# Local CSV

## Overview

This destination writes data to a directory on the _local_ filesystem on the host running Airbyte. By default, data is written to `/tmp/airbyte_local`. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

### Sync Overview

#### Output schema

This destination outputs files with the name of the stream. Each row will be written as a new line in the output CSV file. 

#### Data Type Mapping

The output file will have a single column called `data` which will be populated by the full record as a json blob.

#### Features

This section should contain a table with the following format:

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |

#### Performance considerations

This integration will be constrained by the speed at which your filesystem accepts writes.

## Getting Started

### Requirements:

* The `destination_path` field must start with `/local` which is the name of the local mount that points to `LOCAL_ROOT`. Any other directories in this path will be placed inside the `LOCAL_ROOT`. By default, the value of `LOCAL_ROOT` is `/tmp/airbyte_local`. e.g. if `destination_path` is `/local/my/data`, the output will be written to `/tmp/airbyte_local/my/data`.  

