# GitHub (Beta, Gen-2)

<HideInUI>

This page contains the setup guide and reference information for the GitHub (Beta, Gen-2) source connector.

</HideInUI>

This connector is a clean-slate rewrite of the [GitHub](https://docs.airbyte.com/integrations/sources/github) source. It emits strongly typed, normalized records intended to land cleanly in Parquet and Iceberg destinations: nested GitHub entities are replaced by the scalar keys needed to join them, and repeated fields carry either primitives or fully declared objects.

It is **not** backwards compatible with `source-github`. Stream names, field names and field types differ, and there is no migration path. Use it alongside the Gen-1 connector, not as a drop-in replacement.

## Prerequisites

- A list of GitHub repositories in `owner/repo` form, and access to them if they are private.
- A GitHub [personal access token](https://github.com/settings/tokens) with the `repo` scope.

## Setup guide

1. In Airbyte, create a new **GitHub (Beta, Gen-2)** source.
2. Paste your personal access token into **Personal Access Token**.
3. Add one entry per repository under **Repositories**, in `owner/repo` form.
4. Optionally set **Start Date** to limit how far back incremental streams read.
5. For GitHub Enterprise Server, set **API URL** to the full base URL of your instance's REST API, including the path prefix — for example `https://github.example.com/api/v3`.

## Supported sync modes

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Supported streams

| Stream | Incremental | Cursor |
| --- | --- | --- |
| [branches](https://docs.github.com/en/rest/branches/branches) | No | |
| [comments](https://docs.github.com/en/rest/issues/comments) | Yes | `updated_at` |
| [commits](https://docs.github.com/en/rest/commits/commits) | Yes | `commit_committer_date` |
| [issues](https://docs.github.com/en/rest/issues/issues) | Yes | `updated_at` |
| [pull_requests](https://docs.github.com/en/rest/pulls/pulls) | Yes | `updated_at` |
| [releases](https://docs.github.com/en/rest/releases/releases) | Yes | `updated_at` |
| [repositories](https://docs.github.com/en/rest/repos/repos) | No | |
| [review_comments](https://docs.github.com/en/rest/pulls/comments) | Yes | `updated_at` |
| [reviews](https://docs.github.com/en/rest/pulls/reviews) | No | |
| [stargazers](https://docs.github.com/en/rest/activity/starring) | Yes | `starred_at` |
| [tags](https://docs.github.com/en/rest/repos/repos) | No | |
| [workflow_jobs](https://docs.github.com/en/rest/actions/workflow-jobs) | No | |
| [workflow_runs](https://docs.github.com/en/rest/actions/workflow-runs) | Yes | `updated_at` |
| [workflows](https://docs.github.com/en/rest/actions/workflows) | Yes | `updated_at` |

The `issues` stream includes pull requests, matching the underlying API. Use `is_pull_request` and `pull_request_number` to join or exclude them.

## Data model

Records are normalized rather than passed through:

- Referenced entities are carried as keys, not embedded objects — `user_id` / `user_login` / `user_type` instead of a `user` object, `repository` / `repository_id` instead of a repository object.
- Labels, assignees and requested reviewers are emitted as arrays of objects holding the key tuple, such as `labels` with `id`, `name` and `description`. Each also has a projection column of plain strings — `label_names`, `assignee_logins`, `requested_reviewer_logins` — which is the simplest access path for most queries.
- Every record carries its own `api_url` and `html_url`; content-download URLs (`diff_url`, `patch_url`, `tarball_url`, `zipball_url`) are preserved. Links to referenced collections are dropped.
- Timestamps are typed as `timestamp_with_timezone`, and IDs, counts and positions are integers.

The full rationale is documented in the connector's [CONTRIBUTING.md](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-github-gen2/CONTRIBUTING.md).

## Limitations

- Authentication is by personal access token only. OAuth, GitHub Apps and multi-token rotation are not supported yet.
- Streams that require the GraphQL API — reaction counts, pull request stats, Projects V2 — are not implemented.
- There is no `users` stream; user IDs and logins are carried on the records that reference them.

## Performance considerations

The connector honors GitHub's REST rate limits for a single token. `releases`, `stargazers`, `workflows` and `workflow_runs` filter incrementally on the client because their endpoints have no `since` parameter, so those streams re-read the full collection on every sync.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| --- | --- | --- | --- |
| 0.1.0 | 2026-07-31 | [80343](https://github.com/airbytehq/airbyte/pull/80343) | Initial release |

</details>
