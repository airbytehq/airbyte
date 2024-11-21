# GitHub

<HideInUI>

This page contains the setup guide and reference information for the [GitHub](https://www.github.com) source connector.

</HideInUI>

## Prerequisites

- List of GitHub Repositories (and access for them in case they are private)

<!-- env:cloud -->
**For Airbyte Cloud:**

- OAuth
- Personal Access Token (see [Permissions and scopes](https://docs.airbyte.com/integrations/sources/github#permissions-and-scopes))
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

- Personal Access Token (see [Permissions and scopes](https://docs.airbyte.com/integrations/sources/github#permissions-and-scopes))
<!-- /env:oss -->

## Setup guide

### Step 1: Set up GitHub

Create a [GitHub Account](https://github.com).

<!-- env:oss -->
**Airbyte Open Source additional setup steps**

Log into [GitHub](https://github.com) and then generate a [personal access token](https://github.com/settings/tokens). To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.
<!-- /env:oss -->

### Step 2: Set up the GitHub connector in Airbyte

<!-- env:cloud -->
## For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select GitHub from the Source type dropdown.
4. Enter a name for the GitHub connector.
4. Set start date if needed.
5. To authenticate:
<!-- env:cloud -->

<!-- env:oss -->
### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Set up start date.
<!-- /env:oss -->

  - **For Airbyte Cloud:** **Authenticate your GitHub account** to authorize your GitHub account. Airbyte will authenticate the GitHub account you are already logged in to. Please make sure you are logged into the right account.
<!-- /env:cloud -->
<!-- env:oss -->

   - **For Airbyte Open Source:** Authenticate with **Personal Access Token**. To generate a personal access token, log into [GitHub](https://github.com) and then generate a [personal access token](https://github.com/settings/tokens). Enter your GitHub personal access token. To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.
<!-- /env:oss -->

6. **GitHub Repositories** - Enter a list of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/airbyte airbytehq/another-repo` for multiple repositories. If you want to specify the organization to receive data from all its repositories, then you should specify it according to the following example: `airbytehq/*`.

:::caution
Repositories with the wrong name or repositories that do not exist or have the wrong name format will be skipped with `WARN` message in the logs.
:::

7. **Start date (Optional)** - The date from which you'd like to replicate data for streams. For streams which support this configuration, only data generated on or after the start date will be replicated.

- These streams will only sync records generated on or after the **Start Date**: `comments`, `commit_comment_reactions`, `commit_comments`, `commits`, `deployments`, `events`, `issue_comment_reactions`, `issue_events`, `issue_milestones`, `issue_reactions`, `issues`, `project_cards`, `project_columns`, `projects`, `pull_request_comment_reactions`, `pull_requests`, `pull_requeststats`, `releases`, `review_comments`, `reviews`, `stargazers`, `workflow_runs`, `workflows`.

- The **Start Date** does not apply to the streams below and all data will be synced for these streams: `assignees`, `branches`, `collaborators`, `issue_labels`, `organizations`, `pull_request_commits`, `pull_request_stats`, `repositories`,  `tags`,  `teams`, `users`

8. **Branch (Optional)** - List of GitHub repository branches to pull commits from, e.g. `airbytehq/airbyte/master`. If no branches are specified for a repository, the default branch will be pulled. (e.g. `airbytehq/airbyte/master airbytehq/airbyte/my-branch`).
9. **Max requests per hour (Optional)** - The GitHub API allows for a maximum of 5,000 requests per hour (15,000 for Github Enterprise). You can specify a lower value to limit your use of the API quota. Refer to GitHub article [Rate limits for the REST API](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api).

<HideInUI>

## Supported sync modes

The GitHub source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following full refresh streams:

- [Assignees](https://docs.github.com/en/rest/issues/assignees?apiVersion=2022-11-28#list-assignees)
- [Branches](https://docs.github.com/en/rest/branches/branches?apiVersion=2022-11-28#list-branches)
- [Contributor Activity](https://docs.github.com/en/rest/metrics/statistics?apiVersion=2022-11-28#get-all-contributor-commit-activity)
- [Collaborators](https://docs.github.com/en/rest/collaborators/collaborators?apiVersion=2022-11-28#list-repository-collaborators)
- [Issue labels](https://docs.github.com/en/rest/issues/labels?apiVersion=2022-11-28#list-labels-for-a-repository)
- [Organizations](https://docs.github.com/en/rest/orgs/orgs?apiVersion=2022-11-28#list-organizations)
- [Pull request commits](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-commits-on-a-pull-request)
- [Tags](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repository-tags)
- [TeamMembers](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#list-team-members)
- [TeamMemberships](https://docs.github.com/en/rest/teams/members?apiVersion=2022-11-28#get-team-membership-for-a-user)
- [Teams](https://docs.github.com/en/rest/teams/teams?apiVersion=2022-11-28#list-teams)
- [Users](https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-members)
- [Issue timeline events](https://docs.github.com/en/rest/issues/timeline?apiVersion=2022-11-28#list-timeline-events-for-an-issue)

This connector outputs the following incremental streams:

- [Comments](https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#list-issue-comments-for-a-repository)
- [Commit comment reactions](https://docs.github.com/en/rest/reference/reactions?apiVersion=2022-11-28#list-reactions-for-a-commit-comment)
- [Commit comments](https://docs.github.com/en/rest/commits/comments?apiVersion=2022-11-28#list-commit-comments-for-a-repository)
- [Commits](https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits)
- [Deployments](https://docs.github.com/en/rest/deployments/deployments?apiVersion=2022-11-28#list-deployments)
- [Events](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-repository-events)
- [Issue comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue-comment)
- [Issue events](https://docs.github.com/en/rest/issues/events?apiVersion=2022-11-28#list-issue-events-for-a-repository)
- [Issue milestones](https://docs.github.com/en/rest/issues/milestones?apiVersion=2022-11-28#list-milestones)
- [Issue reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue)
- [Issues](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues)
- [Project (Classic) cards](https://docs.github.com/en/rest/projects/cards?apiVersion=2022-11-28#list-project-cards)
- [Project (Classic) columns](https://docs.github.com/en/rest/projects/columns?apiVersion=2022-11-28#list-project-columns)
- [Projects (Classic)](https://docs.github.com/en/rest/projects/projects?apiVersion=2022-11-28#list-repository-projects)
- [ProjectsV2](https://docs.github.com/en/graphql/reference/objects#projectv2)
- [Pull request comment reactions](https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-a-pull-request-review-comment)
- [Pull request stats](https://docs.github.com/en/graphql/reference/objects#pullrequest)
- [Pull requests](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#list-pull-requests)
- [Releases](https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#list-releases)
- [Repositories](https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-organization-repositories)
- [Review comments](https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#list-review-comments-in-a-repository)
- [Reviews](https://docs.github.com/en/rest/pulls/reviews?apiVersion=2022-11-28#list-reviews-for-a-pull-request)
- [Stargazers](https://docs.github.com/en/rest/activity/starring?apiVersion=2022-11-28#list-stargazers)
- [WorkflowJobs](https://docs.github.com/pt/rest/actions/workflow-jobs?apiVersion=2022-11-28#list-jobs-for-a-workflow-run)
- [WorkflowRuns](https://docs.github.com/en/rest/actions/workflow-runs?apiVersion=2022-11-28#list-workflow-runs-for-a-repository)
- [Workflows](https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#list-repository-workflows)

### Notes

1. Only 4 streams \(`comments`, `commits`, `issues` and `review comments`\) from the listed above streams are pure incremental meaning that they:

   - read only new records;
   - output only new records.

2. Streams `workflow_runs` and `worflow_jobs` is almost pure incremental:

   - read new records and some portion of old records (in past 30 days) [docs](https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs);
   - the `workflow_jobs` depends on the `workflow_runs` to read the data, so they both follow the same logic [docs](https://docs.github.com/pt/rest/actions/workflow-jobs#list-jobs-for-a-workflow-run);
   - output only new records.

3. Other 19 incremental streams are also incremental but with one difference, they:

   - read all records;
   - output only new records.
     Please, consider this behaviour when using those 19 incremental streams because it may affect you API call limits.

4. Sometimes for large streams specifying very distant `start_date` in the past may result in keep on getting error from GitHub instead of records \(respective `WARN` log message will be outputted\). In this case Specifying more recent `start_date` may help.
   **The "Start date" configuration option does not apply to the streams below, because the GitHub API does not include dates which can be used for filtering:**

- `assignees`
- `branches`
- `collaborators`
- `issue_labels`
- `organizations`
- `pull_request_commits`
- `pull_request_stats`
- `repositories`
- `tags`
- `teams`
- `users`

## Limitations & Troubleshooting

<details>
<summary>
Expand to see details about GitHub connector limitations and troubleshooting.
</summary>

### Connector limitations

#### Rate limiting
The GitHub connector should not run into GitHub API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully. Refer to GitHub article [Rate limits for the REST API](https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api).

#### Permissions and scopes

If you use OAuth authentication method, the OAuth2.0 application requests the next list of [scopes](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes): **repo**, **read:org**, **read:repo_hook**, **read:user**, **read:discussion**, **workflow**. For [personal access token](https://github.com/settings/tokens) you need to manually select needed scopes.

Your token should have at least the `repo` scope. Depending on which streams you want to sync, the user generating the token needs more permissions:

- For syncing Collaborators, the user which generates the personal access token must be a collaborator. To become a collaborator, they must be invited by an owner. If there are no collaborators, no records will be synced. Read more about access permissions [here](https://docs.github.com/en/get-started/learning-about-github/access-permissions-on-github).
- Syncing [Teams](https://docs.github.com/en/organizations/organizing-members-into-teams/about-teams) is only available to authenticated members of a team's [organization](https://docs.github.com/en/rest/orgs). [Personal user accounts](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts) and repositories belonging to them don't have access to Teams features. In this case no records will be synced.
- To sync the Projects stream, the repository must have the Projects feature enabled.

### Troubleshooting

* Check out common troubleshooting issues for the GitHub source connector on our [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions)

</details>

### Tutorials

Now that you have set up the GitHub source connector, check out the following GitHub tutorials:

See github guidelines here.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                                                                      | Subject                                                                                                                                                             |
|:--------|:-----------|:------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.5.5   | 2023-12-26 | [33783](https://github.com/airbytehq/airbyte/pull/33783)                                                          | Fix retry for 504 error in GraphQL based streams                                                                                                                    |
| 1.5.4   | 2023-11-20 | [32679](https://github.com/airbytehq/airbyte/pull/32679)                                                          | Return AirbyteMessage if max retry exeeded for 202 status code                                                                                                      |
| 1.5.3   | 2023-10-23 | [31702](https://github.com/airbytehq/airbyte/pull/31702)                                                          | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                     |
| 1.5.2   | 2023-10-13 | [31386](https://github.com/airbytehq/airbyte/pull/31386)                                                          | Handle `ContributorActivity` continuous `ACCEPTED` response                                                                                                         |
| 1.5.1   | 2023-10-12 | [31307](https://github.com/airbytehq/airbyte/pull/31307)                                                          | Increase backoff_time for stream `ContributorActivity`                                                                                                              |
| 1.5.0   | 2023-10-11 | [31300](https://github.com/airbytehq/airbyte/pull/31300)                                                          | Update Schemas: Add date-time format to fields                                                                                                                      |
| 1.4.6   | 2023-10-04 | [31056](https://github.com/airbytehq/airbyte/pull/31056)                                                          | Migrate spec properties' `repository` and `branch` type to \<array\>                                                                                                |
| 1.4.5   | 2023-10-02 | [31023](https://github.com/airbytehq/airbyte/pull/31023)                                                          | Increase backoff for stream `Contributor Activity`                                                                                                                  |
| 1.4.4   | 2023-10-02 | [30971](https://github.com/airbytehq/airbyte/pull/30971)                                                          | Mark `start_date` as optional.                                                                                                                                      |
| 1.4.3   | 2023-10-02 | [30979](https://github.com/airbytehq/airbyte/pull/30979)                                                          | Fetch archived records in `Project Cards`                                                                                                                           |
| 1.4.2   | 2023-09-30 | [30927](https://github.com/airbytehq/airbyte/pull/30927)                                                          | Provide actionable user error messages                                                                                                                              |
| 1.4.1   | 2023-09-30 | [30839](https://github.com/airbytehq/airbyte/pull/30839)                                                          | Update CDK to Latest version                                                                                                                                        |
| 1.4.0   | 2023-09-29 | [30823](https://github.com/airbytehq/airbyte/pull/30823)                                                          | Add new stream `issue Timeline Events`                                                                                                                              |
| 1.3.1   | 2023-09-28 | [30824](https://github.com/airbytehq/airbyte/pull/30824)                                                          | Handle empty response in stream `ContributorActivity`                                                                                                               |
| 1.3.0   | 2023-09-25 | [30731](https://github.com/airbytehq/airbyte/pull/30731)                                                          | Add new stream `ProjectsV2`                                                                                                                                         |
| 1.2.1   | 2023-09-22 | [30693](https://github.com/airbytehq/airbyte/pull/30693)                                                          | Handle 404 error in `TeamMemberShips`                                                                                                                               |
| 1.2.0   | 2023-09-22 | [30647](https://github.com/airbytehq/airbyte/pull/30647)                                                          | Add support for self-hosted GitHub instances                                                                                                                        |
| 1.1.1   | 2023-09-21 | [30654](https://github.com/airbytehq/airbyte/pull/30654)                                                          | Rewrite source connection error messages                                                                                                                            |
| 1.1.0   | 2023-08-03 | [30615](https://github.com/airbytehq/airbyte/pull/30615)                                                          | Add new stream `Contributor Activity`                                                                                                                               |
| 1.0.4   | 2023-08-03 | [29031](https://github.com/airbytehq/airbyte/pull/29031)                                                          | Reverted `advancedAuth` spec changes                                                                                                                                |
| 1.0.3   | 2023-08-01 | [28910](https://github.com/airbytehq/airbyte/pull/28910)                                                          | Updated `advancedAuth` broken references                                                                                                                            |
| 1.0.2   | 2023-07-11 | [28144](https://github.com/airbytehq/airbyte/pull/28144)                                                          | Add `archived_at` property to `Organizations` schema parameter                                                                                                      |
| 1.0.1   | 2023-05-22 | [25838](https://github.com/airbytehq/airbyte/pull/25838)                                                          | Deprecate "page size" input parameter                                                                                                                               |
| 1.0.0   | 2023-05-19 | [25778](https://github.com/airbytehq/airbyte/pull/25778)                                                          | Improve repo(s) name validation on UI                                                                                                                               |
| 0.5.0   | 2023-05-16 | [25793](https://github.com/airbytehq/airbyte/pull/25793)                                                          | Implement client-side throttling of requests                                                                                                                        |
| 0.4.11  | 2023-05-12 | [26025](https://github.com/airbytehq/airbyte/pull/26025)                                                          | Added more transparent depiction of the personal access token expired                                                                                               |
| 0.4.10  | 2023-05-15 | [26075](https://github.com/airbytehq/airbyte/pull/26075)                                                          | Add more specific error message description for no repos case.                                                                                                      |
| 0.4.9   | 2023-05-01 | [24523](https://github.com/airbytehq/airbyte/pull/24523)                                                          | Add undeclared columns to spec                                                                                                                                      |
| 0.4.8   | 2023-04-19 | [00000](https://github.com/airbytehq/airbyte/pull/25312)                                                          | Fix repo name validation                                                                                                                                            |
| 0.4.7   | 2023-03-24 | [24457](https://github.com/airbytehq/airbyte/pull/24457)                                                          | Add validation and transformation for repositories config                                                                                                           |
| 0.4.6   | 2023-03-24 | [24398](https://github.com/airbytehq/airbyte/pull/24398)                                                          | Fix caching for `get_starting_point` in stream "Commits"                                                                                                            |
| 0.4.5   | 2023-03-23 | [24417](https://github.com/airbytehq/airbyte/pull/24417)                                                          | Add pattern_descriptors to fields with an expected format                                                                                                           |
| 0.4.4   | 2023-03-17 | [24255](https://github.com/airbytehq/airbyte/pull/24255)                                                          | Add field groups and titles to improve display of connector setup form                                                                                              |
| 0.4.3   | 2023-03-04 | [22993](https://github.com/airbytehq/airbyte/pull/22993)                                                          | Specified date formatting in specification                                                                                                                          |
| 0.4.2   | 2023-03-03 | [23467](https://github.com/airbytehq/airbyte/pull/23467)                                                          | added user friendly messages, added AirbyteTracedException config_error, updated SAT                                                                                |
| 0.4.1   | 2023-01-27 | [22039](https://github.com/airbytehq/airbyte/pull/22039)                                                          | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                         |
| 0.4.0   | 2023-01-20 | [21457](https://github.com/airbytehq/airbyte/pull/21457)                                                          | Use GraphQL for `issue_reactions` stream                                                                                                                            |
| 0.3.12  | 2023-01-18 | [21481](https://github.com/airbytehq/airbyte/pull/21481)                                                          | Handle 502 Bad Gateway error with proper log message                                                                                                                |
| 0.3.11  | 2023-01-06 | [21084](https://github.com/airbytehq/airbyte/pull/21084)                                                          | Raise Error if no organizations or repos are available during read                                                                                                  |
| 0.3.10  | 2022-12-15 | [20523](https://github.com/airbytehq/airbyte/pull/20523)                                                          | Revert changes from 0.3.9                                                                                                                                           |
| 0.3.9   | 2022-12-14 | [19978](https://github.com/airbytehq/airbyte/pull/19978)                                                          | Update CDK dependency; move custom HTTPError handling into `AvailabilityStrategy` classes                                                                           |
| 0.3.8   | 2022-11-10 | [19299](https://github.com/airbytehq/airbyte/pull/19299)                                                          | Fix events and workflow_runs datetimes                                                                                                                              |
| 0.3.7   | 2022-10-20 | [18213](https://github.com/airbytehq/airbyte/pull/18213)                                                          | Skip retry on HTTP 200                                                                                                                                              |
| 0.3.6   | 2022-10-11 | [17852](https://github.com/airbytehq/airbyte/pull/17852)                                                          | Use default behaviour, retry on 429 and all 5XX errors                                                                                                              |
| 0.3.5   | 2022-10-07 | [17715](https://github.com/airbytehq/airbyte/pull/17715)                                                          | Improve 502 handling for `comments` stream                                                                                                                          |
| 0.3.4   | 2022-10-04 | [17555](https://github.com/airbytehq/airbyte/pull/17555)                                                          | Skip repository if got HTTP 500 for WorkflowRuns stream                                                                                                             |
| 0.3.3   | 2022-09-28 | [17287](https://github.com/airbytehq/airbyte/pull/17287)                                                          | Fix problem with "null" `cursor_field` for WorkflowJobs stream                                                                                                      |
| 0.3.2   | 2022-09-28 | [17304](https://github.com/airbytehq/airbyte/pull/17304)                                                          | Migrate to per-stream state.                                                                                                                                        |
| 0.3.1   | 2022-09-21 | [16947](https://github.com/airbytehq/airbyte/pull/16947)                                                          | Improve error logging when handling HTTP 500 error                                                                                                                  |
| 0.3.0   | 2022-09-09 | [16534](https://github.com/airbytehq/airbyte/pull/16534)                                                          | Add new stream `WorkflowJobs`                                                                                                                                       |
| 0.2.46  | 2022-08-17 | [15730](https://github.com/airbytehq/airbyte/pull/15730)                                                          | Validate input organizations and repositories                                                                                                                       |
| 0.2.45  | 2022-08-11 | [15420](https://github.com/airbytehq/airbyte/pull/15420)                                                          | "User" object can be "null"                                                                                                                                         |
| 0.2.44  | 2022-08-01 | [14795](https://github.com/airbytehq/airbyte/pull/14795)                                                          | Use GraphQL for `pull_request_comment_reactions` stream                                                                                                             |
| 0.2.43  | 2022-07-26 | [15049](https://github.com/airbytehq/airbyte/pull/15049)                                                          | Bugfix schemas for streams `deployments`, `workflow_runs`, `teams`                                                                                                  |
| 0.2.42  | 2022-07-12 | [14613](https://github.com/airbytehq/airbyte/pull/14613)                                                          | Improve schema for stream `pull_request_commits` added "null"                                                                                                       |
| 0.2.41  | 2022-07-03 | [14376](https://github.com/airbytehq/airbyte/pull/14376)                                                          | Add Retry for GraphQL API Resource limitations                                                                                                                      |
| 0.2.40  | 2022-07-01 | [14338](https://github.com/airbytehq/airbyte/pull/14338)                                                          | Revert: "Rename field `mergeable` to `is_mergeable`"                                                                                                                |
| 0.2.39  | 2022-06-30 | [14274](https://github.com/airbytehq/airbyte/pull/14274)                                                          | Rename field `mergeable` to `is_mergeable`                                                                                                                          |
| 0.2.38  | 2022-06-27 | [13989](https://github.com/airbytehq/airbyte/pull/13989)                                                          | Use GraphQL for `reviews` stream                                                                                                                                    |
| 0.2.37  | 2022-06-21 | [13955](https://github.com/airbytehq/airbyte/pull/13955)                                                          | Fix "secondary rate limit" not retrying                                                                                                                             |
| 0.2.36  | 2022-06-20 | [13926](https://github.com/airbytehq/airbyte/pull/13926)                                                          | Break point added for `workflows_runs` stream                                                                                                                       |
| 0.2.35  | 2022-06-16 | [13763](https://github.com/airbytehq/airbyte/pull/13763)                                                          | Use GraphQL for `pull_request_stats` stream                                                                                                                         |
| 0.2.34  | 2022-06-14 | [13707](https://github.com/airbytehq/airbyte/pull/13707)                                                          | Fix API sorting, fix `get_starting_point` caching                                                                                                                   |
| 0.2.33  | 2022-06-08 | [13558](https://github.com/airbytehq/airbyte/pull/13558)                                                          | Enable caching only for parent streams                                                                                                                              |
| 0.2.32  | 2022-06-07 | [13531](https://github.com/airbytehq/airbyte/pull/13531)                                                          | Fix different result from `get_starting_point` when reading by pages                                                                                                |
| 0.2.31  | 2022-05-24 | [13115](https://github.com/airbytehq/airbyte/pull/13115)                                                          | Add incremental support for streams `WorkflowRuns`                                                                                                                  |
| 0.2.30  | 2022-05-09 | [12294](https://github.com/airbytehq/airbyte/pull/12294)                                                          | Add incremental support for streams `CommitCommentReactions`, `IssueCommentReactions`, `IssueReactions`, `PullRequestCommentReactions`, `Repositories`, `Workflows` |
| 0.2.29  | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482)                                                          | Update input configuration copy                                                                                                                                     |
| 0.2.28  | 2022-04-21 | [11893](https://github.com/airbytehq/airbyte/pull/11893)                                                          | Add new streams `TeamMembers`, `TeamMemberships`                                                                                                                    |
| 0.2.27  | 2022-04-02 | [11678](https://github.com/airbytehq/airbyte/pull/11678)                                                          | Fix "PAT Credentials" in spec                                                                                                                                       |
| 0.2.26  | 2022-03-31 | [11623](https://github.com/airbytehq/airbyte/pull/11623)                                                          | Re-factored incremental sync for `Reviews` stream                                                                                                                   |
| 0.2.25  | 2022-03-31 | [11567](https://github.com/airbytehq/airbyte/pull/11567)                                                          | Improve code for better error handling                                                                                                                              |
| 0.2.24  | 2022-03-30 | [9251](https://github.com/airbytehq/airbyte/pull/9251)                                                            | Add Streams Workflow and WorkflowRuns                                                                                                                               |
| 0.2.23  | 2022-03-17 | [11212](https://github.com/airbytehq/airbyte/pull/11212)                                                          | Improve documentation and spec for Beta                                                                                                                             |
| 0.2.22  | 2022-03-10 | [10878](https://github.com/airbytehq/airbyte/pull/10878)                                                          | Fix error handling for unavailable streams with 404 status code                                                                                                     |
| 0.2.21  | 2022-03-04 | [10749](https://github.com/airbytehq/airbyte/pull/10749)                                                          | Add new stream `ProjectCards`                                                                                                                                       |
| 0.2.20  | 2022-02-16 | [10385](https://github.com/airbytehq/airbyte/pull/10385)                                                          | Add new stream `Deployments`, `ProjectColumns`, `PullRequestCommits`                                                                                                |
| 0.2.19  | 2022-02-07 | [10211](https://github.com/airbytehq/airbyte/pull/10211)                                                          | Add human-readable error in case of incorrect organization or repo name                                                                                             |
| 0.2.18  | 2021-02-09 | [10193](https://github.com/airbytehq/airbyte/pull/10193)                                                          | Add handling secondary rate limits                                                                                                                                  |
| 0.2.17  | 2021-02-02 | [9999](https://github.com/airbytehq/airbyte/pull/9999)                                                            | Remove BAD_GATEWAY code from backoff_time                                                                                                                           |
| 0.2.16  | 2021-02-02 | [9868](https://github.com/airbytehq/airbyte/pull/9868)                                                            | Add log message for streams that are restricted for OAuth. Update oauth scopes.                                                                                     |
| 0.2.15  | 2021-01-26 | [9802](https://github.com/airbytehq/airbyte/pull/9802)                                                            | Add missing fields for auto_merge in pull request stream                                                                                                            |
| 0.2.14  | 2021-01-21 | [9664](https://github.com/airbytehq/airbyte/pull/9664)                                                            | Add custom pagination size for large streams                                                                                                                        |
| 0.2.13  | 2021-01-20 | [9619](https://github.com/airbytehq/airbyte/pull/9619)                                                            | Fix logging for function `should_retry`                                                                                                                             |
| 0.2.11  | 2021-01-17 | [9492](https://github.com/airbytehq/airbyte/pull/9492)                                                            | Remove optional parameter `Accept` for reaction`s streams to fix error with 502 HTTP status code in response                                                        |
| 0.2.10  | 2021-01-03 | [7250](https://github.com/airbytehq/airbyte/pull/7250)                                                            | Use CDK caching and convert PR-related streams to incremental                                                                                                       |
| 0.2.9   | 2021-12-29 | [9179](https://github.com/airbytehq/airbyte/pull/9179)                                                            | Use default retry delays on server error responses                                                                                                                  |
| 0.2.8   | 2021-12-07 | [8524](https://github.com/airbytehq/airbyte/pull/8524)                                                            | Update connector fields title/description                                                                                                                           |
| 0.2.7   | 2021-12-06 | [8518](https://github.com/airbytehq/airbyte/pull/8518)                                                            | Add connection retry with GitHub                                                                                                                                    |
| 0.2.6   | 2021-11-24 | [8030](https://github.com/airbytehq/airbyte/pull/8030)                                                            | Support start date property for PullRequestStats and Reviews streams                                                                                                |
| 0.2.5   | 2021-11-21 | [8170](https://github.com/airbytehq/airbyte/pull/8170)                                                            | Fix slow check connection for organizations with a lot of repos                                                                                                     |
| 0.2.4   | 2021-11-11 | [7856](https://github.com/airbytehq/airbyte/pull/7856)                                                            | Resolve $ref fields in some stream schemas                                                                                                                          |
| 0.2.3   | 2021-10-06 | [6833](https://github.com/airbytehq/airbyte/pull/6833)                                                            | Fix config backward compatability                                                                                                                                   |
| 0.2.2   | 2021-10-05 | [6761](https://github.com/airbytehq/airbyte/pull/6761)                                                            | Add oauth worflow specification                                                                                                                                     |
| 0.2.1   | 2021-09-22 | [6223](https://github.com/airbytehq/airbyte/pull/6223)                                                            | Add option to pull commits from user-specified branches                                                                                                             |
| 0.2.0   | 2021-09-19 | [5898](https://github.com/airbytehq/airbyte/pull/5898) and [6227](https://github.com/airbytehq/airbyte/pull/6227) | Don't minimize any output fields & add better error handling                                                                                                        |
| 0.1.11  | 2021-09-15 | [5949](https://github.com/airbytehq/airbyte/pull/5949)                                                            | Add caching for all streams                                                                                                                                         |
| 0.1.10  | 2021-09-09 | [5860](https://github.com/airbytehq/airbyte/pull/5860)                                                            | Add reaction streams                                                                                                                                                |
| 0.1.9   | 2021-09-02 | [5788](https://github.com/airbytehq/airbyte/pull/5788)                                                            | Handling empty repository, check method using RepositoryStats stream                                                                                                |
| 0.1.8   | 2021-09-01 | [5757](https://github.com/airbytehq/airbyte/pull/5757)                                                            | Add more streams                                                                                                                                                    |
| 0.1.7   | 2021-08-27 | [5696](https://github.com/airbytehq/airbyte/pull/5696)                                                            | Handle negative backoff values                                                                                                                                      |
| 0.1.6   | 2021-08-18 | [5456](https://github.com/airbytehq/airbyte/pull/5223)                                                            | Add MultipleTokenAuthenticator                                                                                                                                      |
| 0.1.5   | 2021-08-18 | [5456](https://github.com/airbytehq/airbyte/pull/5456)                                                            | Fix set up validation                                                                                                                                               |
| 0.1.4   | 2021-08-13 | [5136](https://github.com/airbytehq/airbyte/pull/5136)                                                            | Support syncing multiple repositories/organizations                                                                                                                 |
| 0.1.3   | 2021-08-03 | [5156](https://github.com/airbytehq/airbyte/pull/5156)                                                            | Extended existing schemas with `users` property for certain streams                                                                                                 |
| 0.1.2   | 2021-07-13 | [4708](https://github.com/airbytehq/airbyte/pull/4708)                                                            | Fix bug with IssueEvents stream and add handling for rate limiting                                                                                                  |
| 0.1.1   | 2021-07-07 | [4590](https://github.com/airbytehq/airbyte/pull/4590)                                                            | Fix schema in the `pull_request` stream                                                                                                                             |
| 0.1.0   | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174)                                                            | New Source: GitHub                                                                                                                                                  |

</details>

</HideInUI>