# Mixpanel

## Overview

The Mixpanel source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

This Hubspot source wraps the [Singer Mixpanel Tap](https://github.com/singer-io/tap-mixpanel).

### Output schema

Several output streams are available from this source:

* [Export](https://developer.mixpanel.com/docs/exporting-raw-data#section-export-api-reference)
* [Engage](https://developer.mixpanel.com/docs/data-export-api#section-engage)
* [Funnels](https://developer.mixpanel.com/docs/data-export-api#section-funnels)
* [Revenue](https://developer.mixpanel.com/docs/data-export-api#section-hr-span-style-font-family-courier-revenue-span)
* [Annotations](https://developer.mixpanel.com/docs/data-export-api#section-annotations)
* [Cohorts](https://developer.mixpanel.com/docs/cohorts#section-list-cohorts)
* [Cohort Members](https://developer.mixpanel.com/docs/data-export-api#section-engage)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Mixpanel connector should not run into Mixpanel API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Mixpanel API Secret

### Setup guide

Please read [Find API Secret](https://help.mixpanel.com/hc/en-us/articles/115004502806-Find-Project-Token-).

