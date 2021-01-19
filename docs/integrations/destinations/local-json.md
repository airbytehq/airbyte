# Local JSON

{% hint style="danger" %}
This destination is meant to be used on a local workstation and won't work on Kubernetes
{% endhint %}

## Overview

This destination writes data to a directory on the _local_ filesystem on the host running Airbyte. By default, data is written to [/tmp/airbyte_local](file:///tmp/airbyte_local/). To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

### Sync Overview

#### Output schema

Each stream will be output into its own file. Each file will a collections of `json` objects containing 3 fields:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
* `_airbyte_data`: a json blob representing with the extracted data.

#### Features

| Feature | Supported |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |

#### Performance considerations

This integration will be constrained by the speed at which your filesystem accepts writes.

