# JSONPlaceholder

This page contains the setup guide and reference information for the [JSONPlaceholder](https://jsonplaceholder.typicode.com/) source connector.

## Overview

JSONPlaceholder is a free online REST API that you can use for testing, prototyping, and learning. It provides fake data for common resources like posts, comments, albums, photos, todos, and users.

## Prerequisites

No prerequisites are required. JSONPlaceholder is a free, public API that does not require authentication.

## Setup guide

### Set up the JSONPlaceholder connector in Airbyte

1. Log into your Airbyte account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **JSONPlaceholder** from the list of available sources.
4. Enter a **Name** for the connector.
5. Click **Set up source**.

No additional configuration is needed because this is a public API.

## Supported sync modes

The JSONPlaceholder source connector supports the following sync modes:

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported streams

The JSONPlaceholder source connector supports the following streams:

- [Posts](https://jsonplaceholder.typicode.com/posts) - 100 posts
- [Comments](https://jsonplaceholder.typicode.com/comments) - 500 comments
- [Albums](https://jsonplaceholder.typicode.com/albums) - 100 albums
- [Photos](https://jsonplaceholder.typicode.com/photos) - 5,000 photos
- [Todos](https://jsonplaceholder.typicode.com/todos) - 200 todos
- [Users](https://jsonplaceholder.typicode.com/users) - 10 users

## Limitations and troubleshooting

- JSONPlaceholder is a read-only API with fake data intended for testing and prototyping.
- The data is static and does not change, so incremental sync is not supported.
- All records for each resource are returned in a single response. There is no pagination.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                              |
| :------ | :--------- | :----------- | :----------------------------------- |
| 0.1.0   | 2026-03-18 | TBD          | Initial release of JSONPlaceholder source connector |

</details>

## Reference

The connector configuration does not require any parameters because JSONPlaceholder is a public API with no authentication.
