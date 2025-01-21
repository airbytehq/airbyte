# GitLab

This page contains the setup guide and reference information for the Gitlab Source connector.

## Prerequisites

- Gitlab instance or an account at [Gitlab](https://gitlab.com)

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
6. **API URL (Optional)** - The URL to access your self-hosted GitLab instance or `gitlab.com` (default).
7. **Start date (Optional)** - The date from which you'd like to replicate data for streams.
8. **Groups (Optional)** - List of GitLab group IDs, e.g. `airbytehq` for single group, `airbytehq another-repo` for multiple groups.
9. **Projects (Optional)** - List of GitLab projects to pull data for, e.g. `airbytehq/airbyte`.
10. Click **Set up source**.

**Note:** You can specify either Group IDs or Project IDs in the source configuration. If both fields are blank, the connector will retrieve a list of all the groups that are accessible to the configured token and ingest as normal.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Authenticate with **Personal Access Token**.
<!-- /env:oss -->

## Supported sync modes

The Gitlab Source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following streams:

- [Branches](https://docs.gitlab.com/ee/api/branches.html)
- [Commits](https://docs.gitlab.com/ee/api/commits.html) \(Incremental\)
- [Issues](https://docs.gitlab.com/ee/api/issues.html) \(Incremental\)
- [Group Issue Boards](https://docs.gitlab.com/ee/api/group_boards.html)
- [Pipelines](https://docs.gitlab.com/ee/api/pipelines.html) \(Incremental\)
- [Jobs](https://docs.gitlab.com/ee/api/jobs.html)
- [Projects](https://docs.gitlab.com/ee/api/projects.html)
- [Project Milestones](https://docs.gitlab.com/ee/api/milestones.html)
- [Project Merge Requests](https://docs.gitlab.com/ee/api/merge_requests.html) \(Incremental\)
- [Users](https://docs.gitlab.com/ee/api/users.html)
- [Groups](https://docs.gitlab.com/ee/api/groups.html)
- [Group Milestones](https://docs.gitlab.com/ee/api/group_milestones.html)
- [Group and Project members](https://docs.gitlab.com/ee/api/members.html)
- [Tags](https://docs.gitlab.com/ee/api/tags.html)
- [Releases](https://docs.gitlab.com/ee/api/releases/index.html)
- [Deployments](https://docs.gitlab.com/ee/api/deployments/index.html)
- [Group Labels](https://docs.gitlab.com/ee/api/group_labels.html)
- [Project Labels](https://docs.gitlab.com/ee/api/labels.html)
- [Epics](https://docs.gitlab.com/ee/api/epics.html) \(only available for GitLab Ultimate and GitLab.com Gold accounts. Stream Epics uses iid field as primary key for more convenient search and matching with UI. Iid is the internal ID of the epic, number of Epic on UI.\)
- [Epic Issues](https://docs.gitlab.com/ee/api/epic_issues.html) \(only available for GitLab Ultimate and GitLab.com Gold accounts\)

## Additional information

GitLab source works with GitLab API v4. It can also work with self-hosted GitLab API v4.

## Performance considerations

Gitlab has the [rate limits](https://docs.gitlab.com/ee/user/gitlab_com/index.html#gitlabcom-specific-rate-limits), but the Gitlab connector should not run into Gitlab API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                            |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 4.3.4 | 2025-01-11 | [44671](https://github.com/airbytehq/airbyte/pull/44671) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 4.3.3 | 2024-08-17 | [44207](https://github.com/airbytehq/airbyte/pull/44207) | Update dependencies |
| 4.3.2 | 2024-08-12 | [43856](https://github.com/airbytehq/airbyte/pull/43856) | Update dependencies |
| 4.3.1 | 2024-08-03 | [43058](https://github.com/airbytehq/airbyte/pull/43058) | Update dependencies |
| 4.3.0 | 2024-07-31 | [42920](https://github.com/airbytehq/airbyte/pull/42920) | Migrate to CDK v4.1.0 |
| 4.2.2 | 2024-07-27 | [42601](https://github.com/airbytehq/airbyte/pull/42601) | Update dependencies |
| 4.2.1 | 2024-07-20 | [42295](https://github.com/airbytehq/airbyte/pull/42295) | Update dependencies |
| 4.2.0 | 2024-07-17 | [42085](https://github.com/airbytehq/airbyte/pull/42085) | Migrate to CDK v2.4.0 |
| 4.1.0 | 2024-07-17 | [42021](https://github.com/airbytehq/airbyte/pull/42021) | Migrate to CDK v1.8.0 |
| 4.0.8 | 2024-07-13 | [41835](https://github.com/airbytehq/airbyte/pull/41835) | Update dependencies |
| 4.0.7 | 2024-07-10 | [41470](https://github.com/airbytehq/airbyte/pull/41470) | Update dependencies |
| 4.0.6 | 2024-07-09 | [41100](https://github.com/airbytehq/airbyte/pull/41100) | Update dependencies |
| 4.0.5 | 2024-07-06 | [40894](https://github.com/airbytehq/airbyte/pull/40894) | Update dependencies |
| 4.0.4 | 2024-06-25 | [40417](https://github.com/airbytehq/airbyte/pull/40417) | Update dependencies |
| 4.0.3 | 2024-06-22 | [40102](https://github.com/airbytehq/airbyte/pull/40102) | Update dependencies |
| 4.0.2 | 2024-04-24 | [36637](https://github.com/airbytehq/airbyte/pull/36637) | Schema descriptions and CDK 0.80.0 |
| 4.0.1 | 2024-04-23 | [37505](https://github.com/airbytehq/airbyte/pull/37505) | Set error code `500` as retryable |
| 4.0.0 | 2024-03-25 | [35989](https://github.com/airbytehq/airbyte/pull/35989) | Migrate to low-code |
| 3.0.0 | 2024-01-25 | [34548](https://github.com/airbytehq/airbyte/pull/34548) | Fix merge_request_commits stream to return commits for each merge request |
| 2.1.2 | 2024-02-12 | [35167](https://github.com/airbytehq/airbyte/pull/35167) | Manage dependencies with Poetry. |
| 2.1.1 | 2024-01-12 | [34203](https://github.com/airbytehq/airbyte/pull/34203) | prepare for airbyte-lib |
| 2.1.0 | 2023-12-20 | [33676](https://github.com/airbytehq/airbyte/pull/33676) | Add fields to Commits (extended_trailers), Groups (emails_enabled, service_access_tokens_expiration_enforced) and Projects (code_suggestions, model_registry_access_level) streams |
| 2.0.0 | 2023-10-23 | [31700](https://github.com/airbytehq/airbyte/pull/31700) | Add correct date-time format for Deployments, Projects and Groups Members streams |
| 1.8.4 | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 1.8.3 | 2023-10-18 | [31547](https://github.com/airbytehq/airbyte/pull/31547) | Add validation for invalid `groups_list` and/or `projects_list` |
| 1.8.2 | 2023-10-17 | [31492](https://github.com/airbytehq/airbyte/pull/31492) | Expand list of possible error status codes when handling expired `access_token` |
| 1.8.1 | 2023-10-12 | [31375](https://github.com/airbytehq/airbyte/pull/31375) | Mark `start_date` as optional, migrate `groups` and `projects` to array |
| 1.8.0 | 2023-10-12 | [31339](https://github.com/airbytehq/airbyte/pull/31339) | Add undeclared fields to streams schemas, validate date/date-time format in stream schemas |
| 1.7.1 | 2023-10-10 | [31210](https://github.com/airbytehq/airbyte/pull/31210) | Added expired `access_token` handling, while checking the connection |
| 1.7.0   | 2023-08-08 | [27869](https://github.com/airbytehq/airbyte/pull/29203) | Add Deployments stream                                                                                                                                                             |
| 1.6.0   | 2023-06-30 | [27869](https://github.com/airbytehq/airbyte/pull/27869) | Add `shared_runners_setting` field to groups                                                                                                                                       |
| 1.5.1   | 2023-06-24 | [27679](https://github.com/airbytehq/airbyte/pull/27679) | Fix formatting                                                                                                                                                                     |
| 1.5.0   | 2023-06-15 | [27392](https://github.com/airbytehq/airbyte/pull/27392) | Make API URL an optional parameter in spec.                                                                                                                                        |
| 1.4.2   | 2023-06-15 | [27346](https://github.com/airbytehq/airbyte/pull/27346) | Partially revert changes made in version 1.0.4, disallow http calls in cloud.                                                                                                      |
| 1.4.1   | 2023-06-13 | [27351](https://github.com/airbytehq/airbyte/pull/27351) | Fix OAuth token expiry date.                                                                                                                                                       |
| 1.4.0   | 2023-06-12 | [27234](https://github.com/airbytehq/airbyte/pull/27234) | Skip stream slices on 403/404 errors, do not fail syncs.                                                                                                                           |
| 1.3.1   | 2023-06-08 | [27147](https://github.com/airbytehq/airbyte/pull/27147) | Improve connectivity check for connections with no projects/groups                                                                                                                 |
| 1.3.0   | 2023-06-08 | [27150](https://github.com/airbytehq/airbyte/pull/27150) | Update stream schemas                                                                                                                                                              |
| 1.2.1   | 2023-06-02 | [26947](https://github.com/airbytehq/airbyte/pull/26947) | New field `name` added to `Pipelines` and `PipelinesExtended` stream schema                                                                                                        |
| 1.2.0   | 2023-05-17 | [22293](https://github.com/airbytehq/airbyte/pull/22293) | Preserve data in records with flattened keys                                                                                                                                       |
| 1.1.1   | 2023-05-23 | [26422](https://github.com/airbytehq/airbyte/pull/26422) | Fix error `404 Repository Not Found` when syncing project with Repository feature disabled                                                                                         |
| 1.1.0   | 2023-05-10 | [25948](https://github.com/airbytehq/airbyte/pull/25948) | Introduce two new fields in the `Projects` stream schema                                                                                                                           |
| 1.0.4   | 2023-04-20 | [21373](https://github.com/airbytehq/airbyte/pull/21373) | Accept api_url with or without scheme                                                                                                                                              |
| 1.0.3   | 2023-02-14 | [22992](https://github.com/airbytehq/airbyte/pull/22992) | Specified date formatting in specification                                                                                                                                         |
| 1.0.2   | 2023-01-27 | [22001](https://github.com/airbytehq/airbyte/pull/22001) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                                        |
| 1.0.1   | 2023-01-23 | [21713](https://github.com/airbytehq/airbyte/pull/21713) | Fix missing data issue                                                                                                                                                             |
| 1.0.0   | 2022-12-05 | [7506](https://github.com/airbytehq/airbyte/pull/7506)   | Add `OAuth2.0` authentication option                                                                                                                                               |
| 0.1.12  | 2022-12-15 | [20542](https://github.com/airbytehq/airbyte/pull/20542) | Revert HttpAvailability changes, run on cdk 0.15.0                                                                                                                                 |
| 0.1.11  | 2022-12-14 | [20479](https://github.com/airbytehq/airbyte/pull/20479) | Use HttpAvailabilityStrategy + add unit tests                                                                                                                                      |
| 0.1.10  | 2022-12-12 | [20384](https://github.com/airbytehq/airbyte/pull/20384) | Fetch groups along with their subgroups                                                                                                                                            |
| 0.1.9   | 2022-12-11 | [20348](https://github.com/airbytehq/airbyte/pull/20348) | Fix 403 error when syncing `EpicIssues` stream                                                                                                                                     |
| 0.1.8   | 2022-12-02 | [20023](https://github.com/airbytehq/airbyte/pull/20023) | Fix duplicated records issue for `Projects` stream                                                                                                                                 |
| 0.1.7   | 2022-12-01 | [19986](https://github.com/airbytehq/airbyte/pull/19986) | Fix `GroupMilestones` stream schema                                                                                                                                                |
| 0.1.6   | 2022-06-23 | [13252](https://github.com/airbytehq/airbyte/pull/13252) | Add GroupIssueBoards stream                                                                                                                                                        |
| 0.1.5   | 2022-05-02 | [11907](https://github.com/airbytehq/airbyte/pull/11907) | Fix null projects param and `container_expiration_policy`                                                                                                                          |
| 0.1.4   | 2022-03-23 | [11140](https://github.com/airbytehq/airbyte/pull/11140) | Ingest All Accessible Groups if not Specified in Config                                                                                                                            |
| 0.1.3   | 2021-12-21 | [8991](https://github.com/airbytehq/airbyte/pull/8991)   | Update connector fields title/description                                                                                                                                          |
| 0.1.2   | 2021-10-18 | [7108](https://github.com/airbytehq/airbyte/pull/7108)   | Allow all domains to be used as `api_url`                                                                                                                                          |
| 0.1.1   | 2021-10-12 | [6932](https://github.com/airbytehq/airbyte/pull/6932)   | Fix pattern field in spec file, remove unused fields from config files, use cache from CDK                                                                                         |
| 0.1.0   | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174)   | Initial Release                                                                                                                                                                    |

</details>
