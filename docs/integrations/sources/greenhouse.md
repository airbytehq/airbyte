# Greenhouse

## Overview

The Greenhouse source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

* [Applications](https://developers.greenhouse.io/harvest.html#applications)
* [Candidates](https://developers.greenhouse.io/harvest.html#candidates)
* [Close Reasons](https://developers.greenhouse.io/harvest.html#close-reasons)
* [Custom Fields](https://developers.greenhouse.io/harvest.html#custom-fields)
* [Degrees](https://developers.greenhouse.io/harvest.html#get-list-degrees)
* [Departments](https://developers.greenhouse.io/harvest.html#departments)
* [Job Posts](https://developers.greenhouse.io/harvest.html#job-posts)
* [Jobs](https://developers.greenhouse.io/harvest.html#jobs)
* [Offers](https://developers.greenhouse.io/harvest.html#offers)
* [Scorecards](https://developers.greenhouse.io/harvest.html#scorecards)
* [Users](https://developers.greenhouse.io/harvest.html#users)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Greenhouse connector should not run into Greenhouse API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Greenhouse API Key

### Setup guide

Please follow the [Greenhouse documentation for generating an API key](https://developers.greenhouse.io/harvest.html#authentication).

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.4   | 2021-09-15 | [6238](https://github.com/airbytehq/airbyte/pull/6238) | added identification of accessible streams for API keys with limited permissions |
