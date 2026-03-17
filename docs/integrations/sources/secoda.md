# Secoda API

## Sync overview

This source syncs data from the [Secoda API](https://docs.secoda.co/secoda-api). It supports both full refresh and incremental sync modes. Incremental syncs use client-side filtering on the `updated_at` (or `created_at`) cursor field, meaning all records are fetched from the API but only new or updated records are emitted to the destination.

## This Source Supports the Following Streams

- [collections](https://docs.secoda.co/secoda-api) - Workspace collections
- [tables](https://docs.secoda.co/secoda-api) - Tables from integrations
- [columns](https://docs.secoda.co/secoda-api) - Columns from integrations
- [terms](https://docs.secoda.co/secoda-api) - Glossary terms (via resource catalog)
- [integrations](https://docs.secoda.co/secoda-api) - Active integrations
- [documents](https://docs.secoda.co/secoda-api) - Documentation pages
- [tags](https://docs.secoda.co/secoda-api) - Custom tags
- [users](https://docs.secoda.co/secoda-api) - Workspace members
- [teams](https://docs.secoda.co/secoda-api) - Workspace teams
- [groups](https://docs.secoda.co/secoda-api) - User groups
- [questions](https://docs.secoda.co/secoda-api) - Questions and answers
- [monitors](https://docs.secoda.co/secoda-api) - Data monitors
- [incidents](https://docs.secoda.co/secoda-api) - Monitor incidents
- [lineage](https://docs.secoda.co/secoda-api) - Manual lineage relationships
- [dashboards](https://docs.secoda.co/secoda-api) - Dashboards from integrations
- [charts](https://docs.secoda.co/secoda-api) - Charts from integrations
- [ai_chat_metrics](https://docs.secoda.co/secoda-api) - Aggregate AI chat usage metrics
- [ai_chat_timeseries](https://docs.secoda.co/secoda-api) - AI chat usage over time
- [ai_chats](https://docs.secoda.co/secoda-api) - Detailed AI chat conversations
- [ai_rated_messages](https://docs.secoda.co/secoda-api) - AI chats with user feedback
- [ai_prompts_by_member](https://docs.secoda.co/secoda-api) - AI prompt counts per member

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  | Client-side filtering on `updated_at` or `created_at`. Streams `users`, `ai_chat_metrics`, and `ai_prompts_by_member` support full refresh only. |

### Performance considerations

Secoda enforces a rate limit of 30 calls/min on PUT/PATCH/POST requests. The connector handles 429 responses with automatic retry using the `Retry-After` header.

The resource catalog endpoint (`/api/v1/resource/catalog`) has a maximum limit of 10,000 resources across all pages. For workspaces exceeding this limit on the `terms` stream, consider using more specific filters.

## Getting started

### Requirements

- Secoda API Key ([how to generate](https://docs.secoda.co/secoda-api/authentication))

### Configuration

| Parameter | Required | Default | Description |
| :-------- | :------- | :------ | :---------- |
| `api_key` | Yes | | Your Secoda API access key. The key is case sensitive. |
| `api_host` | No | `api.secoda.co` | API host for your workspace region: `api.secoda.co` (US), `eapi.secoda.co` (EU), or `aapi.secoda.co` (APAC). |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                  |
| :------ | :--------- | :-------------------------------------------------------- | :--------------------------------------- |
| 0.3.0 | 2026-03-17 | [TBD](https://github.com/airbytehq/airbyte/pull/TBD) | Add 18 new streams, incremental sync, multi-region support, fix API paths, fix pagination, add rate limit retry. Breaking: `terms` stream migrated to resource catalog endpoint. |
| 0.2.25 | 2025-05-10 | [60140](https://github.com/airbytehq/airbyte/pull/60140) | Update dependencies |
| 0.2.24 | 2025-05-04 | [59624](https://github.com/airbytehq/airbyte/pull/59624) | Update dependencies |
| 0.2.23 | 2025-04-27 | [58987](https://github.com/airbytehq/airbyte/pull/58987) | Update dependencies |
| 0.2.22 | 2025-04-19 | [57454](https://github.com/airbytehq/airbyte/pull/57454) | Update dependencies |
| 0.2.21 | 2025-03-29 | [56768](https://github.com/airbytehq/airbyte/pull/56768) | Update dependencies |
| 0.2.20 | 2025-03-22 | [56234](https://github.com/airbytehq/airbyte/pull/56234) | Update dependencies |
| 0.2.19 | 2025-03-08 | [55516](https://github.com/airbytehq/airbyte/pull/55516) | Update dependencies |
| 0.2.18 | 2025-03-01 | [54996](https://github.com/airbytehq/airbyte/pull/54996) | Update dependencies |
| 0.2.17 | 2025-02-23 | [54606](https://github.com/airbytehq/airbyte/pull/54606) | Update dependencies |
| 0.2.16 | 2025-02-15 | [54017](https://github.com/airbytehq/airbyte/pull/54017) | Update dependencies |
| 0.2.15 | 2025-02-08 | [53486](https://github.com/airbytehq/airbyte/pull/53486) | Update dependencies |
| 0.2.14 | 2025-02-01 | [53024](https://github.com/airbytehq/airbyte/pull/53024) | Update dependencies |
| 0.2.13 | 2025-01-25 | [52488](https://github.com/airbytehq/airbyte/pull/52488) | Update dependencies |
| 0.2.12 | 2025-01-18 | [51870](https://github.com/airbytehq/airbyte/pull/51870) | Update dependencies |
| 0.2.11 | 2025-01-11 | [51322](https://github.com/airbytehq/airbyte/pull/51322) | Update dependencies |
| 0.2.10 | 2024-12-28 | [50692](https://github.com/airbytehq/airbyte/pull/50692) | Update dependencies |
| 0.2.9 | 2024-12-21 | [50271](https://github.com/airbytehq/airbyte/pull/50271) | Update dependencies |
| 0.2.8 | 2024-12-14 | [49691](https://github.com/airbytehq/airbyte/pull/49691) | Update dependencies |
| 0.2.7 | 2024-12-12 | [49362](https://github.com/airbytehq/airbyte/pull/49362) | Update dependencies |
| 0.2.6 | 2024-12-11 | [49076](https://github.com/airbytehq/airbyte/pull/49076) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.5 | 2024-11-05 | [48360](https://github.com/airbytehq/airbyte/pull/48360) | Revert to source-declarative-manifest v5.17.0 |
| 0.2.4 | 2024-11-05 | [48337](https://github.com/airbytehq/airbyte/pull/48337) | Update dependencies |
| 0.2.3 | 2024-10-29 | [47908](https://github.com/airbytehq/airbyte/pull/47908) | Update dependencies |
| 0.2.2 | 2024-10-28 | [47566](https://github.com/airbytehq/airbyte/pull/47566) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-14 | [44074](https://github.com/airbytehq/airbyte/pull/44074) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43864](https://github.com/airbytehq/airbyte/pull/43864) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43631](https://github.com/airbytehq/airbyte/pull/43631) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43097](https://github.com/airbytehq/airbyte/pull/43097) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42829](https://github.com/airbytehq/airbyte/pull/42829) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42189](https://github.com/airbytehq/airbyte/pull/42189) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41723](https://github.com/airbytehq/airbyte/pull/41723) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41459](https://github.com/airbytehq/airbyte/pull/41459) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41202](https://github.com/airbytehq/airbyte/pull/41202) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40848](https://github.com/airbytehq/airbyte/pull/40848) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40266](https://github.com/airbytehq/airbyte/pull/40266) | Update dependencies |
| 0.1.4 | 2024-06-22 | [39983](https://github.com/airbytehq/airbyte/pull/39983) | Update dependencies |
| 0.1.3 | 2024-06-05 | [38932](https://github.com/airbytehq/airbyte/pull/38932) | Make connector compatible with builder |
| 0.1.2 | 2024-06-04 | [38957](https://github.com/airbytehq/airbyte/pull/38957) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.1 | 2024-05-21 | [38530](https://github.com/airbytehq/airbyte/pull/38530) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-27 | [#18378](https://github.com/airbytehq/airbyte/pull/18378) | 🎉 New Source: Secoda API [low-code CDK] |

</details>
