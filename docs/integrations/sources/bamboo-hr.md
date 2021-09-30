# Bamboo HR

## Overview

The BambooHr source supports Full Refresh sync. You can choose if this connector will overwrite the old records or duplicate old ones.

### Output schema

This connector outputs the following streams:

* [Employees](https://documentation.bamboohr.com/reference#get-employees-directory-1)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

BambooHR has the [rate limits](https://documentation.bamboohr.com/docs/api-details), but the connector should not run into API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* BambooHr Account
* BambooHr [Api key](https://documentation.bamboohr.com/docs)

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-08-27 | [5054](https://github.com/airbytehq/airbyte/pull/5054) | Initial release with Employees API |
