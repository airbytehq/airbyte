# GitHub
This page contains the setup guide and reference information for the GitHub source connector.

## Prerequisites
* Start date
* GitHub Repositories
* Branch (Optional)
* Page size for large streams (Optional)

For Airbyte Cloud:
* Access Token

For Airbyte OSS:
* Personal Access Token

## Setup guide
### Step 1: Set up GitHub

Create a [GitHub Account](https://github.com).

### Airbyte Open Source additional setup steps

Log into [GitHub](https://github.com) and then generate a [personal access token](https://github.com/settings/tokens). To load balance your API quota consumption across multiple API tokens, input multiple tokens separated with `,`.

### Step 2: Set up the GitHub connector in Airbyte
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **GitHub** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your GitHub account`.
5. Log in and Authorize to the GitHub account.
6. **Start date** - The date from which you'd like to replicate data for streams: `comments`, `commit_comment_reactions`, `commit_comments`, `commits`, `deployments`, `events`, `issue_comment_reactions`, `issue_events`, `issue_milestones`, `issue_reactions`, `issues`, `project_cards`, `project_columns`, `projects`, `pull_request_comment_reactions`, `pull_requests`, `pull_requeststats`, `releases`, `review_comments`, `reviews`, `stargazers`, `workflow_runs`, `workflows`.
7. **GitHub Repositories** - Space-delimited list of GitHub organizations/repositories, e.g. `airbytehq/airbyte` for single repository, `airbytehq/airbyte airbytehq/another-repo` for multiple repositories. If you want to specify the organization to receive data from all its repositories, then you should specify it according to the following example: `airbytehq/*`.
8. **Branch (Optional)** - Space-delimited list of GitHub repository branches to pull commits for, e.g. `airbytehq/airbyte/master`. If no branches are specified for a repository, the default branch will be pulled. (e.g. `airbytehq/airbyte/master airbytehq/airbyte/my-branch`).
9. **Page size for large streams (Optional)** - The GitHub connector contains several streams with a large load. The page size of such streams depends on the size of your repository. Recommended to specify values between 10 and 30.

**For Airbyte OSS:**
1. Authenticate with **Personal Access Token**.

## Supported sync modes

The GitHub source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

## Supported Streams

This connector outputs the following full refresh streams:

* [Assignees](https://docs.github.com/en/rest/reference/issues#list-assignees)
* [Branches](https://docs.github.com/en/rest/reference/repos#list-branches)
* [Collaborators](https://docs.github.com/en/rest/reference/repos#list-repository-collaborators)
* [Issue labels](https://docs.github.com/en/rest/issues/labels#list-labels-for-a-repository)
* [Organizations](https://docs.github.com/en/rest/reference/orgs#get-an-organization)
* [Pull request commits](https://docs.github.com/en/rest/reference/pulls#list-commits-on-a-pull-request)
* [Tags](https://docs.github.com/en/rest/reference/repos#list-repository-tags)
* [TeamMembers](https://docs.github.com/en/rest/teams/members#list-team-members)
* [TeamMemberships](https://docs.github.com/en/rest/reference/teams#get-team-membership-for-a-user)
* [Teams](https://docs.github.com/en/rest/reference/teams#list-teams)
* [Users](https://docs.github.com/en/rest/reference/orgs#list-organization-members)

This connector outputs the following incremental streams:

* [Comments](https://docs.github.com/en/rest/reference/issues#list-issue-comments-for-a-repository)
* [Commit comment reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-a-commit-comment)
* [Commit comments](https://docs.github.com/en/rest/reference/repos#list-commit-comments-for-a-repository)
* [Commits](https://docs.github.com/en/rest/reference/repos#list-commits)
* [Deployments](https://docs.github.com/en/rest/reference/deployments#list-deployments)
* [Events](https://docs.github.com/en/rest/reference/activity#list-repository-events)
* [Issue comment reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-an-issue-comment)
* [Issue events](https://docs.github.com/en/rest/reference/issues#list-issue-events-for-a-repository)
* [Issue milestones](https://docs.github.com/en/rest/reference/issues#list-milestones)
* [Issue reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-an-issue)
* [Issues](https://docs.github.com/en/rest/reference/issues#list-repository-issues)
* [Project cards](https://docs.github.com/en/rest/reference/projects#list-project-cards)
* [Project columns](https://docs.github.com/en/rest/reference/projects#list-project-columns)
* [Projects](https://docs.github.com/en/rest/reference/projects#list-repository-projects)
* [Pull request comment reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-a-pull-request-review-comment)
* [Pull request stats](https://docs.github.com/en/rest/reference/pulls#get-a-pull-request)
* [Pull requests](https://docs.github.com/en/rest/reference/pulls#list-pull-requests)
* [Releases](https://docs.github.com/en/rest/reference/repos#list-releases)
* [Repositories](https://docs.github.com/en/rest/reference/repos#list-organization-repositories)
* [Review comments](https://docs.github.com/en/rest/reference/pulls#list-review-comments-in-a-repository)
* [Reviews](https://docs.github.com/en/rest/reference/pulls#list-reviews-for-a-pull-request)
* [Stargazers](https://docs.github.com/en/rest/reference/activity#list-stargazers)
* [WorkflowRuns](https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-repository)
* [Workflows](https://docs.github.com/en/rest/reference/actions#workflows)

### Notes

1. Only 4 streams \(`comments`, `commits`, `issues` and `review comments`\) from the above 24 incremental streams are pure incremental meaning that they:
   * read only new records;
   * output only new records.

2. Stream `workflow_runs` is almost pure incremental:
   * read new records and some portion of old records (in past 30 days) [docs](https://docs.github.com/en/actions/managing-workflow-runs/re-running-workflows-and-jobs);
   * output only new records.

3. Other 19 incremental streams are also incremental but with one difference, they:
   * read all records;
   * output only new records.
   Please, consider this behaviour when using those 19 incremental streams because it may affect you API call limits.

4. We are passing few parameters \(`since`, `sort` and `direction`\) to GitHub in order to filter records and sometimes for large streams specifying very distant `start_date` in the past may result in keep on getting error from GitHub instead of records \(respective `WARN` log message will be outputted\). In this case Specifying more recent `start_date` may help.
**The "Start date" configuration option does not apply to the streams below, because the GitHub API does not include dates which can be used for filtering:**

* `assignees`
* `branches`
* `collaborators`
* `issue_labels`
* `organizations`
* `pull_request_commits`
* `pull_request_stats`
* `repositories`
* `tags`
* `teams`
* `users`

### Permissions and scopes

If you use OAuth authentication method, the oauth2.0 application requests the next list of [scopes](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes): **repo**, **read:org**, **read:repo_hook**, **read:user**, **read:discussion**, **workflow**. For [personal access token](https://github.com/settings/tokens) it need to manually select needed scopes.

Your token should have at least the `repo` scope. Depending on which streams you want to sync, the user generating the token needs more permissions:

* For syncing Collaborators, the user which generates the personal access token must be a collaborator. To become a collaborator, they must be invited by an owner. If there are no collaborators, no records will be synced. Read more about access permissions [here](https://docs.github.com/en/get-started/learning-about-github/access-permissions-on-github).
* Syncing [Teams](https://docs.github.com/en/organizations/organizing-members-into-teams/about-teams) is only available to authenticated members of a team's [organization](https://docs.github.com/en/rest/orgs). [Personal user accounts](https://docs.github.com/en/get-started/learning-about-github/types-of-github-accounts) and repositories belonging to them don't have access to Teams features. In this case no records will be synced.
* To sync the Projects stream, the repository must have the Projects feature enabled.

### Performance considerations

The GitHub connector should not run into GitHub API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request | Subject                                                                                                      |
|:--------|:-----------| :--- |:-------------------------------------------------------------------------------------------------------------|
| 0.2.39  | 2022-06-30 | [14274](https://github.com/airbytehq/airbyte/pull/14274) | Rename field `mergeable` to `is_mergeable`                                                                   |
| 0.2.38  | 2022-06-27 | [13989](https://github.com/airbytehq/airbyte/pull/13989) | Use GraphQL for `reviews` stream                                                                           |
| 0.2.37  | 2022-06-21 | [13955](https://github.com/airbytehq/airbyte/pull/13955) | Fix "secondary rate limit" not retrying                                                                    |
| 0.2.36  | 2022-06-20 | [13926](https://github.com/airbytehq/airbyte/pull/13926) | Break point added for `workflows_runs` stream                                                              |
| 0.2.35  | 2022-06-16 | [13763](https://github.com/airbytehq/airbyte/pull/13763) | Use GraphQL for `pull_request_stats` stream                                                                |
| 0.2.34  | 2022-06-14 | [13707](https://github.com/airbytehq/airbyte/pull/13707) | Fix API sorting, fix `get_starting_point` caching                                                          |
| 0.2.33  | 2022-06-08 | [13558](https://github.com/airbytehq/airbyte/pull/13558) | Enable caching only for parent streams                                                                     |
| 0.2.32  | 2022-06-07 | [13531](https://github.com/airbytehq/airbyte/pull/13531) | Fix different result from `get_starting_point` when reading by pages                                       |
| 0.2.31  | 2022-05-24 | [13115](https://github.com/airbytehq/airbyte/pull/13115) | Add incremental support for streams `WorkflowRuns`                                                         |
| 0.2.30  | 2022-05-09 | [12294](https://github.com/airbytehq/airbyte/pull/12294) | Add incremental support for streams `CommitCommentReactions`, `IssueCommentReactions`, `IssueReactions`, `PullRequestCommentReactions`, `Repositories`, `Workflows` |
| 0.2.29  | 2022-05-04 | [\#12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy |
| 0.2.28  | 2022-04-21 | [11893](https://github.com/airbytehq/airbyte/pull/11893) | Add new streams `TeamMembers`, `TeamMemberships`                                                           |
| 0.2.27  | 2022-04-02 | [11678](https://github.com/airbytehq/airbyte/pull/11678) | Fix "PAT Credentials" in spec                                                                              |
| 0.2.26  | 2022-03-31 | [11623](https://github.com/airbytehq/airbyte/pull/11623) | Re-factored incremental sync for `Reviews` stream                                                          |
| 0.2.25  | 2022-03-31 | [11567](https://github.com/airbytehq/airbyte/pull/11567) | Improve code for better error handling                                                                     |
| 0.2.24  | 2022-03-30 | [9251](https://github.com/airbytehq/airbyte/pull/9251) | Add Streams Workflow and WorkflowRuns                                                                        |
| 0.2.23  | 2022-03-17 | [11212](https://github.com/airbytehq/airbyte/pull/11212) | Improve documentation and spec for Beta                                                                    |
| 0.2.22  | 2022-03-10 | [10878](https://github.com/airbytehq/airbyte/pull/10878) | Fix error handling for unavailable streams with 404 status code                                            |
| 0.2.21  | 2022-03-04 | [10749](https://github.com/airbytehq/airbyte/pull/10749) | Add new stream `ProjectCards`                                                                              |
| 0.2.20  | 2022-02-16 | [10385](https://github.com/airbytehq/airbyte/pull/10385) | Add new stream `Deployments`, `ProjectColumns`, `PullRequestCommits`                                       |
| 0.2.19  | 2022-02-07 | [10211](https://github.com/airbytehq/airbyte/pull/10211) | Add human-readable error in case of incorrect organization or repo name                                    |
| 0.2.18  | 2021-02-09 | [10193](https://github.com/airbytehq/airbyte/pull/10193) | Add handling secondary rate limits                                                                         |
| 0.2.17  | 2021-02-02 | [9999](https://github.com/airbytehq/airbyte/pull/9999) | Remove BAD_GATEWAY code from backoff_time                                                                    |
| 0.2.16  | 2021-02-02 | [9868](https://github.com/airbytehq/airbyte/pull/9868) | Add log message for streams that are restricted for OAuth. Update oauth scopes.                              |
| 0.2.15  | 2021-01-26 | [9802](https://github.com/airbytehq/airbyte/pull/9802) | Add missing fields for auto_merge in pull request stream                                                     |
| 0.2.14  | 2021-01-21 | [9664](https://github.com/airbytehq/airbyte/pull/9664) | Add custom pagination size for large streams                                                                 |
| 0.2.13  | 2021-01-20 | [9619](https://github.com/airbytehq/airbyte/pull/9619) | Fix logging for function `should_retry`                                                                      |
| 0.2.11  | 2021-01-17 | [9492](https://github.com/airbytehq/airbyte/pull/9492) | Remove optional parameter `Accept` for reaction`s streams to fix error with 502 HTTP status code in response |
| 0.2.10  | 2021-01-03 | [7250](https://github.com/airbytehq/airbyte/pull/7250) | Use CDK caching and convert PR-related streams to incremental                                                |
| 0.2.9   | 2021-12-29 | [9179](https://github.com/airbytehq/airbyte/pull/9179) | Use default retry delays on server error responses                                                           |
| 0.2.8   | 2021-12-07 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description                                                                    |
| 0.2.7   | 2021-12-06 | [8518](https://github.com/airbytehq/airbyte/pull/8518) | Add connection retry with GitHub                                                                             |
| 0.2.6   | 2021-11-24 | [8030](https://github.com/airbytehq/airbyte/pull/8030) | Support start date property for PullRequestStats and Reviews streams                                         |
| 0.2.5   | 2021-11-21 | [8170](https://github.com/airbytehq/airbyte/pull/8170) | Fix slow check connection for organizations with a lot of repos                                              |
| 0.2.4   | 2021-11-11 | [7856](https://github.com/airbytehq/airbyte/pull/7856) | Resolve $ref fields in some stream schemas                                                                   |
| 0.2.3   | 2021-10-06 | [6833](https://github.com/airbytehq/airbyte/pull/6833) | Fix config backward compatability                                                                            |
| 0.2.2   | 2021-10-05 | [6761](https://github.com/airbytehq/airbyte/pull/6761) | Add oauth worflow specification                                                                              |
| 0.2.1   | 2021-09-22 | [6223](https://github.com/airbytehq/airbyte/pull/6223) | Add option to pull commits from user-specified branches                                                      |
| 0.2.0   | 2021-09-19 | [5898](https://github.com/airbytehq/airbyte/pull/5898) and [6227](https://github.com/airbytehq/airbyte/pull/6227) | Don't minimize any output fields & add better error handling                                                 |
| 0.1.11  | 2021-09-15 | [5949](https://github.com/airbytehq/airbyte/pull/5949) | Add caching for all streams                                                                                  |
| 0.1.10  | 2021-09-09 | [5860](https://github.com/airbytehq/airbyte/pull/5860) | Add reaction streams                                                                                         |
| 0.1.9   | 2021-09-02 | [5788](https://github.com/airbytehq/airbyte/pull/5788) | Handling empty repository, check method using RepositoryStats stream                                         |
| 0.1.8   | 2021-09-01 | [5757](https://github.com/airbytehq/airbyte/pull/5757) | Add more streams                                                                                             |
| 0.1.7   | 2021-08-27 | [5696](https://github.com/airbytehq/airbyte/pull/5696) | Handle negative backoff values                                                                               |
| 0.1.6   | 2021-08-18 | [5456](https://github.com/airbytehq/airbyte/pull/5223) | Add MultipleTokenAuthenticator                                                                               |
| 0.1.5   | 2021-08-18 | [5456](https://github.com/airbytehq/airbyte/pull/5456) | Fix set up validation                                                                                        |
| 0.1.4   | 2021-08-13 | [5136](https://github.com/airbytehq/airbyte/pull/5136) | Support syncing multiple repositories/organizations                                                          |
| 0.1.3   | 2021-08-03 | [5156](https://github.com/airbytehq/airbyte/pull/5156) | Extended existing schemas with `users` property for certain streams                                          |
| 0.1.2   | 2021-07-13 | [4708](https://github.com/airbytehq/airbyte/pull/4708) | Fix bug with IssueEvents stream and add handling for rate limiting                                           |
| 0.1.1   | 2021-07-07 | [4590](https://github.com/airbytehq/airbyte/pull/4590) | Fix schema in the `pull_request` stream                                                                      |
| 0.1.0   | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174) | New Source: GitHub                                                                                           |

