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

**Note:** You can specify either Group IDs or Project IDs in the source configuration. If both fields are blank, the connector will retrieve a list of all the groups that are accessible to the configured token and ingest as normal.

## Additional information

GitLab source is working with GitLab API v4. It can also work with self-hosted GitLab API v4.

## Changelog

| Version | Date       | Pull Request                                             | Subject |
|:--------|:-----------|:---------------------------------------------------------| :--- |
| 0.1.6   | 2022-06-23 | [13252](https://github.com/airbytehq/airbyte/pull/13252) | Add GroupIssueBoards stream |
| 0.1.5   | 2022-05-02 | [11907](https://github.com/airbytehq/airbyte/pull/11907) | Fix null projects param and `container_expiration_policy` |
| 0.1.4   | 2022-03-23 | [11140](https://github.com/airbytehq/airbyte/pull/11140) | Ingest All Accessible Groups if not Specified in Config |
| 0.1.3   | 2021-12-21 | [8991](https://github.com/airbytehq/airbyte/pull/8991)   | Update connector fields title/description |
| 0.1.2   | 2021-10-18 | [7108](https://github.com/airbytehq/airbyte/pull/7108)   | Allow all domains to be used as `api_url` |
| 0.1.1   | 2021-10-12 | [6932](https://github.com/airbytehq/airbyte/pull/6932)   | Fix pattern field in spec file, remove unused fields from config files, use cache from CDK |
| 0.1.0   | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174)   | Initial Release |

