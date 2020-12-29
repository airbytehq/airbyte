# Github

## Overview

The GitHub source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Github source wraps the [Singer Github Tap](https://github.com/singer-io/tap-github).

### Output schema

This connector outputs the following streams: 
  * [Assignees](https://developer.github.com/v3/issues/assignees/#list-assignees)
  * [Collaborators](https://developer.github.com/v3/repos/collaborators/#list-collaborators)
  * [Commits](https://developer.github.com/v3/repos/commits/#list-commits-on-a-repository)
  * [Issues](https://developer.github.com/v3/issues/#list-issues-for-a-repository)
  * [Pull Requests](https://developer.github.com/v3/pulls/#list-pull-requests)
  * [Comments](https://developer.github.com/v3/issues/comments/#list-comments-in-a-repository)
  * [Reviews](https://developer.github.com/v3/pulls/reviews/#list-reviews-on-a-pull-request)
  * [Review Comments](https://developer.github.com/v3/pulls/comments)
  * [Stargazers](https://developer.github.com/v3/activity/starring/#list-stargazers)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | yes |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Github connector should not run into Github API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Github Account
* Github Personal Access Token.

### Setup guide

Log into Github and then generate a [personal access token](https://github.com/settings/tokens).

We recommend creating a restricted key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

