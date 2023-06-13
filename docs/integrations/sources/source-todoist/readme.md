# Todoist

## Overview

The Todoist source supports only `Full Refresh` syncs.

### Output schema

Two output streams are available from this source. A list of these streams can be found below in the [Streams](todoist.md#streams) section.

### Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Getting started

### Requirements

* Todoist API token

You can find your personal token in the [integrations settings view](https://todoist.com/prefs/integrations) of the Todoist web app and replace the token value in the samples.


### Set up the Todoist connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account or navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Todoist** from the Source type dropdown.
4. Enter the name for the Todoist connector.
5. For **Token**, enter the [Todoist personal token](https://todoist.com/app/settings/integrations/).
6. Click **Set up source**.

## Streams

List of available streams:

* [Tasks](https://developer.todoist.com/rest/v2/#tasks)
* [Projects](https://developer.todoist.com/rest/v2/#projects)

## Changelog

| Version | Date       | Pull Request                                               | Subject                                         |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------|
| 0.1.0   | 2022-12-03 | [20046](https://github.com/airbytehq/airbyte/pull/20046)   | 🎉 New Source: todoist                           |
