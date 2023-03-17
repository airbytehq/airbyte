# Simple Analytics

## Requirements

- [Simple Analytics account](https://simpleanalytics.com)
- [Simple Analytics API key](https://simpleanalytics.com/account)

## Supported sync modes

| Feature           | Supported?\(Yes/No\) | Notes                                                                                          |
| :---------------- | :------------------- | :--------------------------------------------------------------------------------------------- |
| Full Refresh Sync | Yes                  | [Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite) |
| Incremental Sync  | No                   |                                                                                                |

## Supported Streams

- [Export](https://docs.simpleanalytics.com/api/export-data-points)

### Notes

Plausible is a privacy-first analytics service. Still it provides raw data export capabilities.

Thus, this source connector retrieves [all possible dimension and metrics](https://docs.simpleanalytics.com/api/export-data-points) on a daily grain, for all days with some website activity.

## Changelog

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-10-30 | [18657](https://github.com/airbytehq/airbyte/pull/18657) | Initial commit |
