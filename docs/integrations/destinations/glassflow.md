# GlassFlow

## Overview

The GlassFlow destination allows you to send/stream data to a GlassFlow pipeline. GlassFlow is 
a serverless, Python-centric data streaming platform that transforms data in real-time for 
end-to-end data pipelines.

### Sync overview

#### Output schema

Each stream will be output a GlassFlow message. The message properties will be

- `stream`: the name of stream where the data is coming from.
- `namespace`: namespace if available from the stream.
- `emitted_at`: timestamp the `AirbyteRecord` was emitted at.
- `data`: `AirbyteRecord` data.

The message will be serialized as JSON.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | Yes                  |       |

## Getting started

### Requirements

To use the GlassFlow destination, you'll need:

- A GlassFlow pipeline_id and pipeline_access_token to publish messages.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date              | Pull Request                                              | Subject                                         |
|:--------|:------------------| :-------------------------------------------------------- | :---------------------------------------------- |
| 0.1.7 | 2025-05-17 | [59862](https://github.com/airbytehq/airbyte/pull/59862) | Update dependencies |
| 0.1.6 | 2025-05-03 | [59349](https://github.com/airbytehq/airbyte/pull/59349) | Update dependencies |
| 0.1.5 | 2025-04-26 | [58697](https://github.com/airbytehq/airbyte/pull/58697) | Update dependencies |
| 0.1.4 | 2025-04-19 | [58260](https://github.com/airbytehq/airbyte/pull/58260) | Update dependencies |
| 0.1.3 | 2025-04-12 | [57645](https://github.com/airbytehq/airbyte/pull/57645) | Update dependencies |
| 0.1.2 | 2025-04-05 | [57127](https://github.com/airbytehq/airbyte/pull/57127) | Update dependencies |
| 0.1.1 | 2025-03-29 | [56578](https://github.com/airbytehq/airbyte/pull/56578) | Update dependencies |
| 0.1.0   | September 01, 2024 | [\#7560](https://github.com/airbytehq/airbyte/pull/7560)  | Initial release                                 |

</details>
