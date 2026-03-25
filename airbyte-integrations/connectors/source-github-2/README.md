# Github 2 source connector

A manifest-only Airbyte connector that syncs data from a **GitHub organisation** into your destination. This connector is not a Python package, it runs inside the base `source-declarative-manifest` image.

## Configuration

| Field | Type | Required | Description |
|---|---|---|---|
| `organization` | string | Yes | The GitHub organisation slug |
| `access_token` | string | Yes | A GitHub Personal Access Token (PAT) with the scopes listed below |
| `start_date` | string | Yes | Earliest date to sync records from. ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ` |
| `end_date` | string | No | Latest date to sync records up to. ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`. **Leave blank for normal ongoing syncs.** Use only when running backfill batches. |

### Required Personal Access Token scopes

| Scope | Required for |
|---|---|
| `repo` | Reading repository data, commits, pull requests, deployments, workflow runs, issues |
| `read:org` | Reading organisation members and teams |
| `read:user` | Reading user profile data |

To generate a PAT: `GitHub` -> `Settings` -> `Developer settings` -> `Personal access tokens` -> `Tokens (classic)` -> `Generate new token`.

### Backfill strategy

When syncing historical data for the first time, do **not** run an open-ended sync. Use successive bounded batches by setting both `start_date` and `end_date` to a realistic window based on the data distribution, then advancing both dates forward for each batch:

```text
Batch 1: start_date=2026-01-01T00:00:00Z  end_date=2026-01-15T00:00:00Z
Batch 2: start_date=2026-01-15T00:00:00Z  end_date=2026-01-29T00:00:00Z
...
Daily:   start_date=<last cursor>           end_date=<leave blank>
```

Once caught up, remove `end_date` from the connection config entirely. The connector will run as a normal open-ended incremental sync from that point on.

## Streams

### Full-refresh streams

Synced in full on every run. No cursor field.

| Stream | GitHub API endpoint | Description |
|---|---|---|
| `teams` | `GET /orgs/{org}/teams` | Organisation teams |
| `users` | `GET /orgs/{org}/members` | Organisation members |
| `repositories` | `GET /orgs/{org}/repos` | All repositories in the organisation |
| `assignees` | `GET /repos/{org}/{repo}/assignees` | Available assignees per repo |
| `branches` | `GET /repos/{org}/{repo}/branches` | Branches per repo |
| `collaborators` | `GET /repos/{org}/{repo}/collaborators` | Collaborators per repo |
| `contributor_activity` | `GET /repos/{org}/{repo}/stats/contributors` | Contributor statistics per repo |
| `issue_labels` | `GET /repos/{org}/{repo}/labels` | Issue labels per repo |
| `tags` | `GET /repos/{org}/{repo}/tags` | Tags per repo |

### Incremental streams

Synced incrementally using a cursor field. Only records created or updated after the last sync cursor are fetched.

| Stream | Cursor field | GitHub API endpoint | Notes |
|---|---|---|---|
| `issues` | `updated_at` | `GET /repos/{org}/{repo}/issues` | Server-side `since` filter. Client-side upper bound via `is_client_side_incremental` (GitHub issues API has no `until` parameter) |
| `commits` | `committer_datetime` | `GET /repos/{org}/{repo}/commits` | Server-side `since` and `until` filters. Cursor uses committer date (not author date) to align with GitHub's API filter behaviour |
| `deployments` | `created_at` | `GET /repos/{org}/{repo}/deployments` | Client-side filtering with pagination stop condition |
| `pull_requests` | `updated_at` | `GET /repos/{org}/{repo}/pulls` | Sorted `created` descending. Pagination stop condition on `created_at` |
| `reviews` | `submitted_at` | `GET /repos/{org}/{repo}/pulls/{pr}/reviews` | Substream of `pull_requests` |
| `workflows` | `updated_at` | `GET /repos/{org}/{repo}/actions/workflows` | Client-side filtering |
| `workflow_runs` | `created_at` | `GET /repos/{org}/{repo}/actions/runs` | Server-side `created` range filter |
| `workflow_jobs` | `started_at` | `GET /repos/{org}/{repo}/actions/runs/{run}/jobs` | Substream of `workflow_runs`. Uses `filter=latest` |
| `deployment_statuses` | `updated_at` | `GET /repos/{org}/{repo}/deployments/{id}/statuses` | Substream of `deployments`. Pagination stop condition |
| `issue_comments` | `updated_at` | `GET /repos/{org}/{repo}/issues/{number}/comments` | Substream of `issues` |
| `pr_comments` | `updated_at` | `GET /repos/{org}/{repo}/pulls/{pr}/comments` | Substream of `pull_requests` |

## Local development

It is recommended to use the Connector Builder to edit this connector. Using your local Airbyte OSS instance, navigate to the **Builder** tab, select **Import a YAML**, and load the connector's `manifest.yaml` file.

### Building the Docker image

Build using `airbyte-ci`:

1. Install [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md)
2. Run:

```bash
airbyte-ci connectors --name=source-github-2 build
```

An image will be available on your host with the tag `airbyte/source-github-2:dev`.

### Creating credentials

Create a file `secrets/config.json` with the following structure:

```json
{
  "organization": "your-org-name",
  "access_token": "ghp_xxxxxxxxxxxx",
  "start_date": "2026-01-01T00:00:00Z",
  "end_date": "2026-01-15T00:00:00Z"
}
```

Omit `end_date` for open-ended syncs. Any directory named `secrets` is gitignored across the entire Airbyte repo.

### Running as a Docker container

```bash
# Print the connector spec
docker run --rm airbyte/source-github-2:dev spec

# Validate credentials
docker run --rm \
  -v $(pwd)/secrets:/secrets \
  airbyte/source-github-2:dev check \
  --config /secrets/config.json

# Discover available streams
docker run --rm \
  -v $(pwd)/secrets:/secrets \
  airbyte/source-github-2:dev discover \
  --config /secrets/config.json

# Run a sync
docker run --rm \
  -v $(pwd)/secrets:/secrets \
  -v $(pwd)/integration_tests:/integration_tests \
  airbyte/source-github-2:dev read \
  --config /secrets/config.json \
  --catalog /integration_tests/configured_catalog.json
```

### Running the CI test suite

```bash
airbyte-ci connectors --name=source-github-2 test
```

## Changelog

| Version | Date | Description |
|---|---|---|
| 1.0.0 | 2026-03-25 | Initial release. Organisation-scoped connector with 20 streams, backfill support via `end_date`, three-tier error handling, `global_substream_cursor` for partition deduplication, `lazy_read_pointer` on all substreams, and `committer_datetime` cursor for commits |
