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

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.1.3   | 2024-04-19 | [37244](https://github.com/airbytehq/airbyte/pull/37244) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry.                      |
| 0.1.2   | 2024-04-15 | [37244](https://github.com/airbytehq/airbyte/pull/37244) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.1.1   | 2024-04-12 | [37244](https://github.com/airbytehq/airbyte/pull/37244) | schema descriptions                                                             |
| 0.1.0   | 2022-11-02 | TBA                                                      | First Commit                                                                    |
