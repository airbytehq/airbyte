# Jira

## Overview

The Jira source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

* [Projects](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-group-projects)
* [Issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-group-issues)
* [Issue comments](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-group-issue-comments)
* [Resolutions](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-resolutions/#api-group-issue-resolutions)
* [Users](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-users/#api-group-users)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Jira connector should not run into Jira API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Jira API Token
* Jira Email
* Jira Domain

### Setup guide

Please follow the [Jira confluence for generating an API token](https://confluence.atlassian.com/cloud/api-tokens-938839638.html).
