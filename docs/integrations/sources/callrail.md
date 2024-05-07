# CallRail

## Overview

The CailRail source supports Full Refresh and Incremental syncs.

### Output schema

This Source is capable of syncing the following core Streams:

- [Calls](https://apidocs.callrail.com/#calls)
- [Companies](https://apidocs.callrail.com/#companies)
- [Text Messages](https://apidocs.callrail.com/#text-messages)
- [Users](https://apidocs.callrail.com/#users)

### Features

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Incremental - Dedupe Sync | Yes        |
| SSL connection            | No         |
| Namespaces                | No         |

## Getting started

### Requirements

- CallRail Account
- CallRail API Token

## Changelog

| Version | Date       | Pull Request                                             | Subject                 |
| :------ | :--------- | :------------------------------------------------------- | :---------------------- |
| 0.1.0   | 2022-10-31 | [18739](https://github.com/airbytehq/airbyte/pull/18739) | 🎉 New Source: CallRail |
