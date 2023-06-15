# GitLab

This page contains the setup guide and reference information for the Gitlab Source connector.

## Prerequisites

- Gitlab instance or an account at [Gitlab](https://gitlab.com)
- Start date
- GitLab Groups (Optional)
- GitLab Projects (Optional)

<!-- env:cloud -->
**For Airbyte Cloud:**

- Personal Access Token (see [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html))
- OAuth
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

- Personal Access Token (see [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html))
<!-- /env:oss -->

## Setup guide

### Step 1: Set up GitLab

Create a [GitLab Account](https://gitlab.com) or set up a local instance of GitLab.

<!-- env:oss -->
**Airbyte Open Source additional setup steps**

Log into [GitLab](https://gitlab.com) and then generate a [personal access token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html). Your token should have the `read_api` scope, that Grants read access to the API, including all groups and projects, the container registry, and the package registry.
<!-- /env:oss -->

<!-- env:cloud -->
### Step 2: Set up the GitLab connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **GitLab** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your GitLab account` by selecting Oauth or Personal Access Token for Authentication.
5. Log in and Authorize to the GitLab account.
6. **Start date** - The date from which you'd like to replicate data for streams.
7. **API URL** - The URL to access you self-hosted GitLab instance or `gitlab.com` (default).
8. **Groups (Optional)** - Space-delimited list of GitLab group IDs, e.g. `airbytehq` for single group, `airbytehq another-repo` for multiple groups.
9. **Projects (Optional)** - Space-delimited list of GitLab projects to pull data for, e.g. `airbytehq/airbyte`.
10. Click **Set up source**.

**Note:** You can specify either Group IDs or Project IDs in the source configuration. If both fields are blank, the connector will retrieve a list of all the groups that are accessible to the configured token and ingest as normal.

<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Authenticate with **Personal Access Token**.
<!-- /env:oss -->

## Supported sync modes

The Gitlab Source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

This connector outputs the following streams:

* [Branches](https://docs.gitlab.com/ee/api/branches.html)
* [Commits](https://docs.gitlab.com/ee/api/commits.html) \(Incremental\)
* [Issues](https://docs.gitlab.com/ee/api/issues.html) \(Incremental\)
* [Group Issue Boards](https://docs.gitlab.com/ee/api/group_boards.html)
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

## Additional information

GitLab source works with GitLab API v4. It can also work with self-hosted GitLab API v4.

## Performance considerations

Gitlab has the [rate limits](https://docs.gitlab.com/ee/user/gitlab_com/index.html#gitlabcom-specific-rate-limits), but the Gitlab connector should not run into Gitlab API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                    |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------|
| 1.4.2   | 2023-06-15 | [27346](https://github.com/airbytehq/airbyte/pull/27346) | Partially revert changes made in version 1.0.4, disallow http calls in cloud.              |
| 1.4.1   | 2023-06-13 | [27351](https://github.com/airbytehq/airbyte/pull/27351) | Fix OAuth token expiry date.                                                               |
| 1.4.0   | 2023-06-12 | [27234](https://github.com/airbytehq/airbyte/pull/27234) | Skip stream slices on 403/404 errors, do not fail syncs.                                   |
| 1.3.1   | 2023-06-08 | [27147](https://github.com/airbytehq/airbyte/pull/27147) | Improve connectivity check for connections with no projects/groups                         |
| 1.3.0   | 2023-06-08 | [27150](https://github.com/airbytehq/airbyte/pull/27150) | Update stream schemas                                                                      |
| 1.2.1   | 2023-06-02 | [26947](https://github.com/airbytehq/airbyte/pull/26947) | New field `name` added to `Pipelines` and `PipelinesExtended` stream schema                |
| 1.2.0   | 2023-05-17 | [22293](https://github.com/airbytehq/airbyte/pull/22293) | Preserve data in records with flattened keys                                               |
| 1.1.1   | 2023-05-23 | [26422](https://github.com/airbytehq/airbyte/pull/26422) | Fix error `404 Repository Not Found` when syncing project with Repository feature disabled |
| 1.1.0   | 2023-05-10 | [25948](https://github.com/airbytehq/airbyte/pull/25948) | Introduce two new fields in the `Projects` stream schema                                   |
| 1.0.4   | 2023-04-20 | [21373](https://github.com/airbytehq/airbyte/pull/21373) | Accept api_url with or without scheme                                                      |
| 1.0.3   | 2023-02-14 | [22992](https://github.com/airbytehq/airbyte/pull/22992) | Specified date formatting in specification                                                 |
| 1.0.2   | 2023-01-27 | [22001](https://github.com/airbytehq/airbyte/pull/22001) | Set `AvailabilityStrategy` for streams explicitly to `None`                                |
| 1.0.1   | 2023-01-23 | [21713](https://github.com/airbytehq/airbyte/pull/21713) | Fix missing data issue                                                                     |
| 1.0.0   | 2022-12-05 | [7506](https://github.com/airbytehq/airbyte/pull/7506)   | Add `OAuth2.0` authentication option                                                       |
| 0.1.12  | 2022-12-15 | [20542](https://github.com/airbytehq/airbyte/pull/20542) | Revert HttpAvailability changes, run on cdk 0.15.0                                         |
| 0.1.11  | 2022-12-14 | [20479](https://github.com/airbytehq/airbyte/pull/20479) | Use HttpAvailabilityStrategy + add unit tests                                              |
| 0.1.10  | 2022-12-12 | [20384](https://github.com/airbytehq/airbyte/pull/20384) | Fetch groups along with their subgroups                                                    |
| 0.1.9   | 2022-12-11 | [20348](https://github.com/airbytehq/airbyte/pull/20348) | Fix 403 error when syncing `EpicIssues` stream                                             |
| 0.1.8   | 2022-12-02 | [20023](https://github.com/airbytehq/airbyte/pull/20023) | Fix duplicated records issue for `Projects` stream                                         |
| 0.1.7   | 2022-12-01 | [19986](https://github.com/airbytehq/airbyte/pull/19986) | Fix `GroupMilestones` stream schema                                                        |
| 0.1.6   | 2022-06-23 | [13252](https://github.com/airbytehq/airbyte/pull/13252) | Add GroupIssueBoards stream                                                                |
| 0.1.5   | 2022-05-02 | [11907](https://github.com/airbytehq/airbyte/pull/11907) | Fix null projects param and `container_expiration_policy`                                  |
| 0.1.4   | 2022-03-23 | [11140](https://github.com/airbytehq/airbyte/pull/11140) | Ingest All Accessible Groups if not Specified in Config                                    |
| 0.1.3   | 2021-12-21 | [8991](https://github.com/airbytehq/airbyte/pull/8991)   | Update connector fields title/description                                                  |
| 0.1.2   | 2021-10-18 | [7108](https://github.com/airbytehq/airbyte/pull/7108)   | Allow all domains to be used as `api_url`                                                  |
| 0.1.1   | 2021-10-12 | [6932](https://github.com/airbytehq/airbyte/pull/6932)   | Fix pattern field in spec file, remove unused fields from config files, use cache from CDK |
| 0.1.0   | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174)   | Initial Release                                                                            |
