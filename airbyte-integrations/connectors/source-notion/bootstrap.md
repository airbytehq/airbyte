# Notion

## Overview

Notion is an application that provides components such as notes, databases, kanban boards, wikis, calendars and reminders. Notion REST API allows a developer to retrieve pages, databases, blocks, and users on the Notion platform.

## Endpoints

Notion API consists of three endpoints which can be extracted data from:

1. **User**: The User object represents a user in a Notion workspace. Users include guests, full workspace members, and bots.
2. **Block**: A block object represents content within Notion. Blocks can be text, lists, media, and more. Page and database is also a type of block.
3. **Search**: This endpoint is used to get list of pages and databases.

## Quick Notes

- Notion stores content in hierarchy, each node is called a 'block'. Block is a generic term which can be text, lists, media, even page and database are also block.

- Due to this hierarchical structure, we use recursive request to get the full list of blocks.

- Pages and databases can be extracted from the `Search` endpoint separately, so they are excluded from the block list request.

- Airbyte CDK doesn't support recursive schema, so some elements of the block schema which can be recursive are replaced with empty objects.

- Page and database must grant permission to the internal integration, otherwise API cannot extract data from them. See [https://developers.notion.com/docs/authorization#authorizing-internal-integrations](https://developers.notion.com/docs/authorization#authorizing-internal-integrations)

- Rate limiting is a standard exponential backoff when a 429 HTTP status code returned. The rate limit for incoming requests is an average of 3 requests per second. Some bursts beyond the average rate are allowed. Notion API also has size limit, see [https://developers.notion.com/reference/errors#request-limits](https://developers.notion.com/reference/errors#request-limits)

## API Reference

The API reference documents: [https://developers.notion.com/reference/intro](https://developers.notion.com/reference)

