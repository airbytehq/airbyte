# GitHub

## Overview

The GitHub source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This connector outputs the following full refresh streams:

* [Assignees](https://docs.github.com/en/rest/reference/issues#list-assignees)
* [Branches](https://docs.github.com/en/rest/reference/repos#list-branches)
* [Collaborators](https://docs.github.com/en/rest/reference/repos#list-repository-collaborators)
* [Commit comment reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-a-commit-comment)
* [Issue comment reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-an-issue-comment)
* [Issue labels](https://docs.github.com/en/free-pro-team@latest/rest/reference/issues#list-labels-for-a-repository)
* [Issue reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-an-issue)
* [Organizations](https://docs.github.com/en/rest/reference/orgs#get-an-organization)
* [Pull request comment reactions](https://docs.github.com/en/rest/reference/reactions#list-reactions-for-a-pull-request-review-comment)
* [Pull request stats](https://docs.github.com/en/rest/reference/pulls#get-a-pull-request)
* [Repositories](https://docs.github.com/en/rest/reference/repos#list-organization-repositories)
* [Reviews](https://docs.github.com/en/rest/reference/pulls#list-reviews-for-a-pull-request)
* [Tags](https://docs.github.com/en/rest/reference/repos#list-repository-tags)
* [Teams](https://docs.github.com/en/rest/reference/teams#list-teams)
* [Users](https://docs.github.com/en/rest/reference/orgs#list-organization-members)

This connector outputs the following incremental streams:

* [Comments](https://docs.github.com/en/rest/reference/issues#list-issue-comments-for-a-repository)
* [Commits](https://docs.github.com/en/rest/reference/repos#list-commits)
* [Commit comments](https://docs.github.com/en/rest/reference/repos#list-commit-comments-for-a-repository)
* [Events](https://docs.github.com/en/rest/reference/activity#list-repository-events)
* [Issues](https://docs.github.com/en/rest/reference/issues#list-repository-issues)
* [Issue events](https://docs.github.com/en/rest/reference/issues#list-issue-events-for-a-repository)
* [Issue milestones](https://docs.github.com/en/rest/reference/issues#list-milestones)
* [Projects](https://docs.github.com/en/rest/reference/projects#list-repository-projects)
* [Pull requests](https://docs.github.com/en/rest/reference/pulls#list-pull-requests)
* [Releases](https://docs.github.com/en/rest/reference/repos#list-releases)
* [Review comments](https://docs.github.com/en/rest/reference/pulls#list-review-comments-in-a-repository)
* [Stargazers](https://docs.github.com/en/rest/reference/activity#list-stargazers)

### Notes

1. Only 3 streams from above 12 incremental streams \(`comments`, `commits` and `issues`\) are pure incremental meaning that they:
   * read only new records;
   * output only new records.

     Other 8 incremental streams are also incremental but with one difference, they:

   * read all records;
   * output only new records.

     Please, consider this behaviour when using those 8 incremental streams because it may affect you API call limits.
2. We are passing few parameters \(`since`, `sort` and `direction`\) to GitHub in order to filter records and sometimes for large streams specifying very distant `start_date` in the past may result in keep on getting error from GitHub instead of records \(respective `WARN` log message will be outputted\). In this case Specifying more recent `start_date` may help.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Github connector should not run into Github API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Github Account;
* `access_token` - Github Personal Access Token wih the necessary permissions \(described below\);
* `start_date` - start date for 3 incremental streams: `comments`, `commits` and `issues`;
* `repository` - Space-delimited list of GitHub repositories/organizations which looks like `<owner>/<repo> <organization>/* <organization_new>/* <owner_new>/<repo_new>`.

**Note**: if you want to specify the organization to receive data from all its repositories, then you should specify it according to the following pattern: `<organization>/*`

### Setup guide

Log into Github and then generate a [personal access token](https://github.com/settings/tokens).

Your token should have at least the `repo` scope. Depending on which streams you want to sync, the user generating the token needs more permissions:

* For syncing Collaborators, the user which generates the personal access token must be a collaborator. To become a collaborator, they must be invited by an owner. If there are no collaborators, no records will be synced. Read more about access permissions [here](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/access-permissions-on-github).
* Syncing [Teams](https://docs.github.com/en/free-pro-team@latest/github/setting-up-and-managing-organizations-and-teams/about-teams) is only available to authenticated members of a team's [organization](https://docs.github.com/en/free-pro-team@latest/rest/reference/orgs). [Personal user accounts](https://docs.github.com/en/free-pro-team@latest/github/getting-started-with-github/types-of-github-accounts) and repositories belonging to them don't have access to Teams features. In this case no records will be synced.
* To sync the Projects stream, the repository must have the Projects feature enabled.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.2.9 | 2021-12-29 | [9179](https://github.com/airbytehq/airbyte/pull/9179) | Use default retry delays on server error responses |
| 0.2.8 | 2021-12-07 | [8524](https://github.com/airbytehq/airbyte/pull/8524) | Update connector fields title/description |
| 0.2.7 | 2021-12-06 | [8518](https://github.com/airbytehq/airbyte/pull/8518) | Add connection retry with Github |
| 0.2.6 | 2021-11-24 | [8030](https://github.com/airbytehq/airbyte/pull/8030) | Support start date property for PullRequestStats and Reviews streams |
| 0.2.5 | 2021-11-21 | [8170](https://github.com/airbytehq/airbyte/pull/8170) | Fix slow check connection for organizations with a lot of repos |
| 0.2.4 | 2021-11-11 | [7856](https://github.com/airbytehq/airbyte/pull/7856) | Resolve $ref fields in some stream schemas |
| 0.2.3 | 2021-10-06 | [6833](https://github.com/airbytehq/airbyte/pull/6833) | Fix config backward compatability |
| 0.2.2 | 2021-10-05 | [6761](https://github.com/airbytehq/airbyte/pull/6761) | Add oauth worflow specification |
| 0.2.1 | 2021-09-22 | [6223](https://github.com/airbytehq/airbyte/pull/6223) | Add option to pull commits from user-specified branches |
| 0.2.0 | 2021-09-19 | [5898](https://github.com/airbytehq/airbyte/pull/5898) and [6227](https://github.com/airbytehq/airbyte/pull/6227) | Don't minimize any output fields & add better error handling |
| 0.1.11 | 2021-09-15 | [5949](https://github.com/airbytehq/airbyte/pull/5949) | Add caching for all streams |
| 0.1.10 | 2021-09-09 | [5860](https://github.com/airbytehq/airbyte/pull/5860) | Add reaction streams |
| 0.1.9 | 2021-09-02 | [5788](https://github.com/airbytehq/airbyte/pull/5788) | Handling empty repository, check method using RepositoryStats stream |
| 0.1.8 | 2021-09-01 | [5757](https://github.com/airbytehq/airbyte/pull/5757) | Add more streams |
| 0.1.7 | 2021-08-27 | [5696](https://github.com/airbytehq/airbyte/pull/5696) | Handle negative backoff values |
| 0.1.6 | 2021-08-18 | [5456](https://github.com/airbytehq/airbyte/pull/5223) | Add MultipleTokenAuthenticator |
| 0.1.5 | 2021-08-18 | [5456](https://github.com/airbytehq/airbyte/pull/5456) | Fix set up validation |
| 0.1.4 | 2021-08-13 | [5136](https://github.com/airbytehq/airbyte/pull/5136) | Support syncing multiple repositories/organizations |
| 0.1.3 | 2021-08-03 | [5156](https://github.com/airbytehq/airbyte/pull/5156) | Extended existing schemas with `users` property for certain streams |
| 0.1.2 | 2021-07-13 | [4708](https://github.com/airbytehq/airbyte/pull/4708) | Fix bug with IssueEvents stream and add handling for rate limiting |
| 0.1.1 | 2021-07-07 | [4590](https://github.com/airbytehq/airbyte/pull/4590) | Fix schema in the `pull_request` stream |
| 0.1.0 | 2021-07-06 | [4174](https://github.com/airbytehq/airbyte/pull/4174) | New Source: GitHub |

