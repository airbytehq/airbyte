# Workday RAAS

## Overview

The Workday RAAS source currently supports Full Refresh syncs only. This means that all contents for all chosen streams will be replaced with every sync.

### Output schema

This Source is capable of syncing the following core Streams:

- 

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported? |     |
| :---------------------------- | :--------- | :-- |
| Full Refresh Sync             | Yes        |     |
| Incremental Sync              | No         |     |
| Replicate Incremental Deletes | No         |     |
| SSL connection                | Yes        |     |
| Namespaces                    | No         |     |

## Getting started

Workday RAAS facilitates resource planning. With it you can manage your employee's skills and schedule assignment of
your employees to the right projects.

### Requirements

- 

## CHANGELOG

| Version | Date       | Pull Request                                   | Subject                |
|:--------|:-----------|:-----------------------------------------------|:-----------------------|
| 0.1.0   | 2024-05-13 | [](https://github.com/airbytehq/airbyte/pull/) | Initial implementation |
