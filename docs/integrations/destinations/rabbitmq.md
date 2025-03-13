# RabbitMQ

## Overview

The RabbitMQ destination allows you to send/stream data to a RabbitMQ routing key. RabbitMQ is one
of the most popular open source message brokers.

### Sync overview

#### Output schema

Each stream will be output a RabbitMQ message with properties. The message properties will be

- `content_type`: set as `application/json`
- `headers`: message headers, which include:
  - `stream`: the name of stream where the data is coming from
  - `namespace`: namespace if available from the stream
  - `emitted_at`: timestamp the `AirbyteRecord` was emitted at.

The `AirbyteRecord` data will be serialized as JSON and set as the RabbitMQ message body.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | Yes                  |       |

## Getting started

### Requirements

To use the RabbitMQ destination, you'll need:

- A RabbitMQ host and credentials (username/password) to publish messages, if required.
- A RabbitMQ routing key.
- RabbitMQ exchange is optional. If specified, a binding between exchange and routing key is
  required.
- RabbitMQ port is optional (it defaults to 5672).
- RabbitMQ virtual host is also optional.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date             | Pull Request                                              | Subject                                         |
|:--------| :--------------- | :-------------------------------------------------------- | :---------------------------------------------- |
| 0.1.36 | 2025-03-08 | [55350](https://github.com/airbytehq/airbyte/pull/55350) | Update dependencies |
| 0.1.35 | 2025-03-01 | [54857](https://github.com/airbytehq/airbyte/pull/54857) | Update dependencies |
| 0.1.34 | 2025-02-22 | [54261](https://github.com/airbytehq/airbyte/pull/54261) | Update dependencies |
| 0.1.33 | 2025-02-15 | [53921](https://github.com/airbytehq/airbyte/pull/53921) | Update dependencies |
| 0.1.32 | 2025-02-01 | [52952](https://github.com/airbytehq/airbyte/pull/52952) | Update dependencies |
| 0.1.31 | 2025-01-25 | [52176](https://github.com/airbytehq/airbyte/pull/52176) | Update dependencies |
| 0.1.30 | 2025-01-18 | [51287](https://github.com/airbytehq/airbyte/pull/51287) | Update dependencies |
| 0.1.29 | 2024-12-28 | [50506](https://github.com/airbytehq/airbyte/pull/50506) | Update dependencies |
| 0.1.28 | 2024-12-21 | [50180](https://github.com/airbytehq/airbyte/pull/50180) | Update dependencies |
| 0.1.27 | 2024-12-14 | [49305](https://github.com/airbytehq/airbyte/pull/49305) | Update dependencies |
| 0.1.26 | 2024-11-25 | [48642](https://github.com/airbytehq/airbyte/pull/48642) | Update dependencies |
| 0.1.25 | 2024-10-29 | [47101](https://github.com/airbytehq/airbyte/pull/47101) | Update dependencies |
| 0.1.24 | 2024-10-12 | [46859](https://github.com/airbytehq/airbyte/pull/46859) | Update dependencies |
| 0.1.23 | 2024-10-05 | [46437](https://github.com/airbytehq/airbyte/pull/46437) | Update dependencies |
| 0.1.22 | 2024-09-28 | [46139](https://github.com/airbytehq/airbyte/pull/46139) | Update dependencies |
| 0.1.21 | 2024-09-21 | [45814](https://github.com/airbytehq/airbyte/pull/45814) | Update dependencies |
| 0.1.20 | 2024-09-14 | [45293](https://github.com/airbytehq/airbyte/pull/45293) | Update dependencies |
| 0.1.19 | 2024-08-31 | [44988](https://github.com/airbytehq/airbyte/pull/44988) | Update dependencies |
| 0.1.18 | 2024-08-24 | [44726](https://github.com/airbytehq/airbyte/pull/44726) | Update dependencies |
| 0.1.17 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.1.16 | 2024-08-17 | [44336](https://github.com/airbytehq/airbyte/pull/44336) | Update dependencies |
| 0.1.15 | 2024-08-10 | [43622](https://github.com/airbytehq/airbyte/pull/43622) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43078](https://github.com/airbytehq/airbyte/pull/43078) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42759](https://github.com/airbytehq/airbyte/pull/42759) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42222](https://github.com/airbytehq/airbyte/pull/42222) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41689](https://github.com/airbytehq/airbyte/pull/41689) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41279](https://github.com/airbytehq/airbyte/pull/41279) | Update dependencies |
| 0.1.9 | 2024-07-06 | [40991](https://github.com/airbytehq/airbyte/pull/40991) | Update dependencies |
| 0.1.8 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.1.7 | 2024-06-25 | [40348](https://github.com/airbytehq/airbyte/pull/40348) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40101](https://github.com/airbytehq/airbyte/pull/40101) | Update dependencies |
| 0.1.5 | 2024-06-06 | [39300](https://github.com/airbytehq/airbyte/pull/39300) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.4 | 2024-05-21 | [38532](https://github.com/airbytehq/airbyte/pull/38532) | [autopull] base image + poetry + up_to_date |
| 0.1.3   | 2024-04-02       | [#36749](https://github.com/airbytehq/airbyte/pull/36749) | Un-archive connector (again)                    |
| 0.1.2   | 2024-03-05       | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector                            |
| 0.1.1   | 2022-09-09       | [16528](https://github.com/airbytehq/airbyte/pull/16528)  | Marked password field in spec as airbyte_secret |
| 0.1.0   | October 29, 2021 | [\#7560](https://github.com/airbytehq/airbyte/pull/7560)  | Initial release                                 |

</details>
