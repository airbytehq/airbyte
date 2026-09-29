# September 2022

## Airbyte [v0.40.4](https://github.com/airbytehq/airbyte/releases/tag/v0.40.4) to [v0.40.6](https://github.com/airbytehq/airbyte/releases/tag/v0.40.6)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

### New features

- Added the low-code connector development kit (early access). This low-code framework is a declarative approach based on YAML with the goal of significantly reducing the time and complexity of building and maintaining connectors. [#11582](https://github.com/airbytehq/airbyte/issues/11582)
  - Added a [guide](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview/) for using the low-code framework. [#17534](https://github.com/airbytehq/airbyte/pull/17534)
- Added support for large schema discovery. [#17394](https://github.com/airbytehq/airbyte/pull/17394)

### Improvements

- Improved `airbyte-metrics` support in the Helm chart. [#16166](https://github.com/airbytehq/airbyte/pull/16166)
- Improved the visibility button behavior for the password input field. This ensures that passwords are always submitted as sensitive fields. [#16011](https://github.com/airbytehq/airbyte/pull/16011)
- Improved Sync History page performance by adding the **Load more** button, which you can click to display previous syncs. [#15938](https://github.com/airbytehq/airbyte/pull/15938)
- Improved the validation error that displays when submitting an incomplete ServiceForm. [#15625](https://github.com/airbytehq/airbyte/pull/15625)
- Improved the source-defined cursor and primary key by adding a tooltip, which displays the full cursor or primary key when you hover over them. [#16116](https://github.com/airbytehq/airbyte/pull/16116)
- Improved Airbyte Cloud’s method of updating source and destination definitions by using `airbyte-cron` to schedule updates. This allows us to keep connectors updated as the catalog changes. [#16438](https://github.com/airbytehq/airbyte/pull/16438)
- Improved the speed that workspace connections are listed. [#17004](https://github.com/airbytehq/airbyte/pull/17004)

## Bugs

- Fixed an issue where the Helm chart templates did not correctly render `extraContainers` values. [#17084](https://github.com/airbytehq/airbyte/pull/17084)
