# Todoist

## Overview

The Todoist source supports only `Full Refresh` syncs.

### Output schema

Two output streams are available from this source. A list of these streams can be found below in the [Streams](outreach.md#streams) section.

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Getting started

### Requirements

* Token API

### Setup guide

Getting a Token API requires an account, and you must generate a personal token.Check out [here](https://todoist.com/app/settings/integrations/).

## Streams

List of available streams:

* Tasks
* Projects

## Changelog

| Version | Date       | Pull Request                                               | Subject                                         |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-12-03 | [20046](https://github.com/airbytehq/airbyte/pull/20046)   | 🎉 New Source: todoist                           |
