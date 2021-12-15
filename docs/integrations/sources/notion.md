# Notion

## Sync overview

This source can sync data for the [Notion API](https://developers.notion.com/reference/intro). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Users](https://developers.notion.com/reference/get-users)
* [Databases](https://developers.notion.com/reference/post-search) \(Incremental\)
* [Pages](https://developers.notion.com/reference/post-search) \(Incremental\)
* [Blocks](https://developers.notion.com/reference/get-block-children) \(Incremental\)

The `Databases` and `Pages` streams are using same `Search` endpoint.

Notion stores `Blocks` in hierarchical structure, so we use recursive request to get list of blocks.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `integer` | `integer` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Notion [rate limits and size limits](https://developers.notion.com/reference/errors#request-limits).

The Notion connector should not run into Notion API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Notion account
* An internal integration in Notion workspace
* Notion internal integration access key

### Setup guide

Please register on Notion and follow this [docs](https://developers.notion.com/docs#getting-started) to create an integration, and then grant pages or databases permission to that integration so that API can access their data.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-10-17 | [7092](https://github.com/airbytehq/airbyte/pull/7092) | Initial Release |


