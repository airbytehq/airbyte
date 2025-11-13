## Prerequisites

- List of GitHub Repositories (and access for them in case they are private)
- 
# GitHub

<HideInUI>

This page contains the setup guide and reference information for the [GitHub](https://www.github.com) source connector.

</HideInUI>


<!-- env:cloud -->
**For Airbyte Cloud:**

- OAuth
- Personal Access Token (see [Permissions and scopes](https://docs.airbyte.com/integrations/sources/github#permissions-and-scopes))
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

- Personal Access Token (see [Permissions and scopes](https://docs.airbyte.com/integrations/sources/github#permissions-and-scopes))
<!-- /env:oss -->

### Step 1: Set up GitHub

## Setup guide

Create a [GitHub Account](https://github.com).

<!-- env:oss -->
**Airbyte Open Source additional setup steps**

Log into [GitHub](https://github.com) and then generate a [personal access token](https://github.com/settings/tokens). To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.
<!-- /env:oss -->

### Step 2: Set up the GitHub connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**.
3. On the source selection page, select **GitHub** from the list of Sources.
4. Add a name for your GitHub connector.
5. To authenticate:
<!-- env:cloud -->

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

- [Users](https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#list-organization-members)

This connector outputs the following incremental streams:

- [Issues](https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#list-repository-issues)

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

## Changelog

| Version | Date       | Pull Request                                                                                                      | Subject                                                                                                                                                             |
|:--------|:-----------|:------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.5.5   | 2023-12-26 | [33783](https://github.com/airbytehq/airbyte/pull/33783)                                                          | Fix retry for 504 error in GraphQL based streams                                                                                                                    |

</HideInUI>