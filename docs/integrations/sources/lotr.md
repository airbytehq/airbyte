# LOTR API

## Sync overview

This source can sync data from the [LOTR API](https://lotrapi.co/). This connector supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. The API is public and requires no authentication.

## This Source Supports the Following Streams

- books
- films  
- characters
- species
- races
- realms
- groups

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

## Getting started

### Requirements

No authentication required - the LOTR API is completely public.

## Changelog

| Version | Date       | Pull Request                                              | Subject                                   |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------- |
| 0.1.0   | 2025-08-08 | [64561](https://github.com/airbytehq/airbyte/pull/64561) | 🎉 New Source: LOTR API [manifest-only]  |
