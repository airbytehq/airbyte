# Vantage API

## Sync overview

This source can sync data from the [Vantage API](https://vantage.readme.io/reference/general). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- Providers: Providers are the highest level API Primitive. A Provider represents either cloud infrastructure provider or a cloud service provider. Some examples of Providers include AWS, GCP or Azure. Providers offer many Services, which is documented below.
- Services: Services are what Providers offer to their customers. A Service is always tied to a Provider. Some examples of Services are EC2 or S3 from a Provider of AWS. A Service has one or more Products offered, which is documented below.
- Products: Products are what Services ultimately price on. Using the example of a Provider of 'AWS' and a Service of 'EC2', Products would be the individual EC2 Instance Types available such as 'm5d.16xlarge' or 'c5.xlarge'. A Product has one or more Prices, which is documented below.
- Reports

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Vantage APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://vantage.readme.io/reference/rate-limiting)

## Getting started

### Requirements

- Vantage Access token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                   |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------- |
| 0.2.6 | 2025-01-11 | [51442](https://github.com/airbytehq/airbyte/pull/51442) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50785](https://github.com/airbytehq/airbyte/pull/50785) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50317](https://github.com/airbytehq/airbyte/pull/50317) | Update dependencies |
| 0.2.3 | 2024-12-14 | [48209](https://github.com/airbytehq/airbyte/pull/48209) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47657](https://github.com/airbytehq/airbyte/pull/47657) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44053](https://github.com/airbytehq/airbyte/pull/44053) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43784](https://github.com/airbytehq/airbyte/pull/43784) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43694](https://github.com/airbytehq/airbyte/pull/43694) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43049](https://github.com/airbytehq/airbyte/pull/43049) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42749](https://github.com/airbytehq/airbyte/pull/42749) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42271](https://github.com/airbytehq/airbyte/pull/42271) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41817](https://github.com/airbytehq/airbyte/pull/41817) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41588](https://github.com/airbytehq/airbyte/pull/41588) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41224](https://github.com/airbytehq/airbyte/pull/41224) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40901](https://github.com/airbytehq/airbyte/pull/40901) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40385](https://github.com/airbytehq/airbyte/pull/40385) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39993](https://github.com/airbytehq/airbyte/pull/39993) | Update dependencies |
| 0.1.3 | 2024-06-04 | [39081](https://github.com/airbytehq/airbyte/pull/39081) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-06-05 | [38839](https://github.com/airbytehq/airbyte/pull/38839) | Make compatible with builder |
| 0.1.1 | 2024-05-21 | [38490](https://github.com/airbytehq/airbyte/pull/38490) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-30 | [#18665](https://github.com/airbytehq/airbyte/pull/18665) | 🎉 New Source: Vantage API [low-code CDK] |

</details>
