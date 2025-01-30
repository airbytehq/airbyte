# Todoist

## Overview

The Todoist source supports only `Full Refresh` syncs.

### Output schema

Two output streams are available from this source. A list of these streams can be found below in the [Streams](todoist.md#streams) section.

### Features

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Getting started

### Requirements

- Todoist API token

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

- [Tasks](https://developer.todoist.com/rest/v2/#tasks)
- [Projects](https://developer.todoist.com/rest/v2/#projects)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                    |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------- |
| 0.3.8 | 2025-01-25 | [52436](https://github.com/airbytehq/airbyte/pull/52436) | Update dependencies |
| 0.3.7 | 2025-01-18 | [51964](https://github.com/airbytehq/airbyte/pull/51964) | Update dependencies |
| 0.3.6 | 2025-01-11 | [51458](https://github.com/airbytehq/airbyte/pull/51458) | Update dependencies |
| 0.3.5 | 2024-12-28 | [50823](https://github.com/airbytehq/airbyte/pull/50823) | Update dependencies |
| 0.3.4 | 2024-12-21 | [49737](https://github.com/airbytehq/airbyte/pull/49737) | Update dependencies |
| 0.3.3 | 2024-12-12 | [49430](https://github.com/airbytehq/airbyte/pull/49430) | Update dependencies |
| 0.3.2 | 2024-10-29 | [47823](https://github.com/airbytehq/airbyte/pull/47823) | Update dependencies |
| 0.3.1 | 2024-10-22 | [47237](https://github.com/airbytehq/airbyte/pull/47237) | Update dependencies |
| 0.3.0 | 2024-08-26 | [44775](https://github.com/airbytehq/airbyte/pull/44775) | Refactor connector to manifest-only format |
| 0.2.18 | 2024-08-24 | [44675](https://github.com/airbytehq/airbyte/pull/44675) | Update dependencies |
| 0.2.17 | 2024-08-17 | [44255](https://github.com/airbytehq/airbyte/pull/44255) | Update dependencies |
| 0.2.16 | 2024-08-12 | [43926](https://github.com/airbytehq/airbyte/pull/43926) | Update dependencies |
| 0.2.15 | 2024-08-10 | [43669](https://github.com/airbytehq/airbyte/pull/43669) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43209](https://github.com/airbytehq/airbyte/pull/43209) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42760](https://github.com/airbytehq/airbyte/pull/42760) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42201](https://github.com/airbytehq/airbyte/pull/42201) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41915](https://github.com/airbytehq/airbyte/pull/41915) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41367](https://github.com/airbytehq/airbyte/pull/41367) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41121](https://github.com/airbytehq/airbyte/pull/41121) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40939](https://github.com/airbytehq/airbyte/pull/40939) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40351](https://github.com/airbytehq/airbyte/pull/40351) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40028](https://github.com/airbytehq/airbyte/pull/40028) | Update dependencies |
| 0.2.5 | 2024-06-05 | [38819](https://github.com/airbytehq/airbyte/pull/38819) | Make compatible with the builder |
| 0.2.4 | 2024-06-04 | [38936](https://github.com/airbytehq/airbyte/pull/38936) | [autopull] Upgrade base image to v1.2.1 |
| 0.2.3 | 2024-05-21 | [38524](https://github.com/airbytehq/airbyte/pull/38524) | [autopull] base image + poetry + up_to_date |
| 0.2.2 | 2024-04-19 | [37272](https://github.com/airbytehq/airbyte/pull/37272) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.2.1 | 2024-04-12 | [37272](https://github.com/airbytehq/airbyte/pull/37272) | schema descriptions |
| 0.2.0 | 2023-12-19 | [32690](https://github.com/airbytehq/airbyte/pull/32690) | Migrate to low-code |
| 0.1.0 | 2022-12-03 | [20046](https://github.com/airbytehq/airbyte/pull/20046) | 🎉 New Source: todoist |

</details>
