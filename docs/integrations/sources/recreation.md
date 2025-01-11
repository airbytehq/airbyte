# Recreation.gov API

## Sync overview

**Recreation Information Database - RIDB**
RIDB is a part of the Recreation One Stop (R1S) program,
which oversees the operation of Recreation.gov -- a user-friendly, web-based
resource to citizens, offering a single point of access to information about
recreational opportunities nationwide. The website represents an authoritative
source of information and services for millions of visitors to federal lands,
historic sites, museums, waterways and other activities and destinations.

This source retrieves data from the [Recreation API](https://ridb.recreation.gov/landing).

### Output schema

This source is capable of syncing the following streams:

- Activities
- Campsites
- Events
- Facilities
- Facility Addresses
- Links
- Media
- Organizations
- Permit Entrances
- Recreation Areas
- Recreation Area Addresses
- Tours

### Features

| Feature           | Supported? \(Yes/No\) | Notes |
| :---------------- | :-------------------- | :---- |
| Full Refresh Sync | Yes                   |       |
| Incremental Sync  | No                    |       |

### Performance considerations

The Recreation API has a rate limit of 50 requests per minute.

## Getting started

### Requirements

1. A Recreation API key. You can get one by signing up [here](https://www.recreation.gov/).
2. Find your key by signing in to the API docs portal and clicking on your name in the top right corner.

### Setup guide

The following fields are required fields for the connector to work:

- `api_key`: Your Recreation API key.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.8 | 2025-01-11 | [51359](https://github.com/airbytehq/airbyte/pull/51359) | Update dependencies |
| 0.2.7 | 2024-12-28 | [50742](https://github.com/airbytehq/airbyte/pull/50742) | Update dependencies |
| 0.2.6 | 2024-12-21 | [50269](https://github.com/airbytehq/airbyte/pull/50269) | Update dependencies |
| 0.2.5 | 2024-12-14 | [49657](https://github.com/airbytehq/airbyte/pull/49657) | Update dependencies |
| 0.2.4 | 2024-12-12 | [48286](https://github.com/airbytehq/airbyte/pull/48286) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47881](https://github.com/airbytehq/airbyte/pull/47881) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47524](https://github.com/airbytehq/airbyte/pull/47524) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44080](https://github.com/airbytehq/airbyte/pull/44080) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-10 | [43621](https://github.com/airbytehq/airbyte/pull/43621) | Update dependencies |
| 0.1.14 | 2024-08-03 | [43109](https://github.com/airbytehq/airbyte/pull/43109) | Update dependencies |
| 0.1.13 | 2024-07-27 | [42709](https://github.com/airbytehq/airbyte/pull/42709) | Update dependencies |
| 0.1.12 | 2024-07-20 | [42250](https://github.com/airbytehq/airbyte/pull/42250) | Update dependencies |
| 0.1.11 | 2024-07-13 | [41782](https://github.com/airbytehq/airbyte/pull/41782) | Update dependencies |
| 0.1.10 | 2024-07-10 | [41533](https://github.com/airbytehq/airbyte/pull/41533) | Update dependencies |
| 0.1.9 | 2024-07-09 | [41276](https://github.com/airbytehq/airbyte/pull/41276) | Update dependencies |
| 0.1.8 | 2024-07-06 | [40899](https://github.com/airbytehq/airbyte/pull/40899) | Update dependencies |
| 0.1.7 | 2024-06-25 | [40465](https://github.com/airbytehq/airbyte/pull/40465) | Update dependencies |
| 0.1.6 | 2024-06-22 | [40143](https://github.com/airbytehq/airbyte/pull/40143) | Update dependencies |
| 0.1.5 | 2024-05-31 | [38733](https://github.com/airbytehq/airbyte/pull/38733) | Make compatible with builder |
| 0.1.4 | 2024-06-04 | [38950](https://github.com/airbytehq/airbyte/pull/38950) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-04-19 | [37244](https://github.com/airbytehq/airbyte/pull/37244) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.1.2 | 2024-04-15 | [37244](https://github.com/airbytehq/airbyte/pull/37244) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1 | 2024-04-12 | [37244](https://github.com/airbytehq/airbyte/pull/37244) | Schema descriptions |
| 0.1.0   | 2022-11-02 | TBA                                                      | First Commit                                                                    |

</details>
