# JSONPlaceholder

[JSONPlaceholder](https://jsonplaceholder.typicode.com/) is a free fake REST API for testing and prototyping. It provides typical REST API endpoints for common resources like posts, comments, albums, photos, todos, and users.

## Prerequisites

No prerequisites are required. JSONPlaceholder is a public API that requires no authentication.

## Setup guide

1. Select **JSONPlaceholder** from the Source list.
2. Enter a **Source name** of your choosing.
3. Click **Set up source**.

No additional configuration is needed.

## Supported sync modes

The JSONPlaceholder source connector supports the following sync modes:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Supported streams

This source is capable of syncing the following streams:

- [Posts](https://jsonplaceholder.typicode.com/posts) - Blog posts with title and body content
- [Comments](https://jsonplaceholder.typicode.com/comments) - Comments on posts
- [Albums](https://jsonplaceholder.typicode.com/albums) - Photo albums
- [Photos](https://jsonplaceholder.typicode.com/photos) - Photos belonging to albums
- [Todos](https://jsonplaceholder.typicode.com/todos) - Todo items with completion status
- [Users](https://jsonplaceholder.typicode.com/users) - User profiles with address and company info

## Limitations and troubleshooting

- JSONPlaceholder returns a fixed dataset. Data does not change between syncs.
- All endpoints return the complete dataset in a single response. There is no pagination.
- Rate limiting may apply for excessive requests.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.1.0   | 2026-03-18 | TBD          | Initial release |

</details>
