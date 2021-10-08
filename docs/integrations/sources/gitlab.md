# GitLab

## Overview

The Gitlab source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This connector outputs the following streams:

* [Branches](https://docs.gitlab.com/ee/api/branches.html)
* [Commits](https://docs.gitlab.com/ee/api/commits.html) \(Incremental\)
* [Issues](https://docs.gitlab.com/ee/api/issues.html) \(Incremental\)
* [Pipelines](https://docs.gitlab.com/ee/api/pipelines.html) \(Incremental\)
* [Jobs](https://docs.gitlab.com/ee/api/jobs.html)
* [Projects](https://docs.gitlab.com/ee/api/projects.html)
* [Project Milestones](https://docs.gitlab.com/ee/api/milestones.html)
* [Project Merge Requests](https://docs.gitlab.com/ee/api/merge_requests.html) \(Incremental\)
* [Users](https://docs.gitlab.com/ee/api/users.html)
* [Groups](https://docs.gitlab.com/ee/api/groups.html)
* [Group Milestones](https://docs.gitlab.com/ee/api/group_milestones.html)
* [Group and Project members](https://docs.gitlab.com/ee/api/members.html)
* [Tags](https://docs.gitlab.com/ee/api/tags.html)
* [Releases](https://docs.gitlab.com/ee/api/releases/index.html)
* [Group Labels](https://docs.gitlab.com/ee/api/group_labels.html)
* [Project Labels](https://docs.gitlab.com/ee/api/labels.html)
* [Epics](https://docs.gitlab.com/ee/api/epics.html) \(only available for GitLab Ultimate and GitLab.com Gold accounts\)
* [Epic Issues](https://docs.gitlab.com/ee/api/epic_issues.html) \(only available for GitLab Ultimate and GitLab.com Gold accounts\)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Partially \(not all streams\) |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

Gitlab has the [rate limits](https://docs.gitlab.com/ee/user/gitlab_com/index.html#gitlabcom-specific-rate-limits), but the Gitlab connector should not run into Gitlab API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Gitlab Account
* Gitlab Personal Access Token wih the necessary permissions \(described below\)

### Setup guide

Log into Gitlab and then generate a [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

Your token should have the `read_api` scope, that Grants read access to the API, including all groups and projects, the container registry, and the package registry.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174) | Initial Release |

