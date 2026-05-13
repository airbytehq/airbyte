# source-pingdom: Contributor notes

## Supported streams

This source syncs these core streams:

- `checks`
- `performance`

## Requirements

The connector requires:

- Pingdom API key
- Start date for incremental syncs

Optional configuration:

- Probes: comma-separated probe identifiers used to filter results.
- Resolution: interval size. Supported values are `hour`, `day`, and `week`. The default is `hour`.
