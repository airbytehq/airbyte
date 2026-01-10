# GitHub Projects v2

## Sync overview

This source syncs data from the [GitHub Projects v2 GraphQL API](https://docs.github.com/en/graphql/reference/objects#projectv2). It extracts project items (issues/PRs linked to projects) and their field values (Status, Priority, custom fields, etc.) for GitHub organizations.

## This Source Supports the Following Streams

- projects_v2: Project metadata (id, title, description, url, timestamps)
- projects_v2_fields: Field definitions for each project
- projects_v2_field_options: SingleSelect and Iteration fields with their options
- projects_v2_item_field_values: Normalized field values (one record per field value)
- projects_v2_items: Items (issues/PRs/drafts) linked to projects

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  | On projects_v2_items stream using item_updated_at |

### Performance considerations

The connector uses the GitHub GraphQL API which has rate limits. For authenticated requests, the limit is 5,000 points per hour. Each query consumes points based on complexity.

## Getting started

### Requirements

- GitHub account with access to the organization's projects
- GitHub Personal Access Token with `read:project` scope

### Setup guide

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with `read:project` scope
   - Copy the token value

2. Configure the connector:
   - Enter your GitHub organization name
   - Enter the Personal Access Token

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0 | 2025-12-23 | [71032](https://github.com/airbytehq/airbyte/pull/71032) | Initial release |

</details>
