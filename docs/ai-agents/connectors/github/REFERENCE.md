# Github full reference

This is the full reference documentation for the Github agent connector.

## Supported entities and actions

The Github connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Repositories | [Get](#repositories-get), [List](#repositories-list), [API Search](#repositories-api-search), [Context Store Search](#repositories-context-store-search) |
| Org Repositories | [List](#org-repositories-list), [Context Store Search](#org-repositories-context-store-search) |
| Branches | [List](#branches-list), [Get](#branches-get), [Context Store Search](#branches-context-store-search) |
| Commits | [List](#commits-list), [Get](#commits-get), [Context Store Search](#commits-context-store-search) |
| Releases | [List](#releases-list), [Get](#releases-get), [Context Store Search](#releases-context-store-search) |
| Issues | [List](#issues-list), [Get](#issues-get), [API Search](#issues-api-search), [Create](#issues-create), [Update](#issues-update), [Context Store Search](#issues-context-store-search) |
| Comments | [Create](#comments-create), [List](#comments-list), [Get](#comments-get), [Context Store Search](#comments-context-store-search) |
| Pull Requests | [Create](#pull-requests-create), [List](#pull-requests-list), [Get](#pull-requests-get), [API Search](#pull-requests-api-search), [Context Store Search](#pull-requests-context-store-search) |
| Reviews | [List](#reviews-list), [Context Store Search](#reviews-context-store-search) |
| Pr Comments | [List](#pr-comments-list), [Get](#pr-comments-get), [Context Store Search](#pr-comments-context-store-search) |
| Labels | [List](#labels-list), [Get](#labels-get), [Context Store Search](#labels-context-store-search) |
| Milestones | [List](#milestones-list), [Get](#milestones-get), [Context Store Search](#milestones-context-store-search) |
| Organizations | [Get](#organizations-get), [List](#organizations-list), [Context Store Search](#organizations-context-store-search) |
| Users | [Get](#users-get), [List](#users-list), [API Search](#users-api-search), [Context Store Search](#users-context-store-search) |
| Teams | [List](#teams-list), [Get](#teams-get), [Context Store Search](#teams-context-store-search) |
| Tags | [List](#tags-list), [Get](#tags-get), [Context Store Search](#tags-context-store-search) |
| Stargazers | [List](#stargazers-list), [Context Store Search](#stargazers-context-store-search) |
| Viewer | [Get](#viewer-get), [Context Store Search](#viewer-context-store-search) |
| Viewer Repositories | [List](#viewer-repositories-list), [Context Store Search](#viewer-repositories-context-store-search) |
| Projects | [List](#projects-list), [Get](#projects-get), [Context Store Search](#projects-context-store-search) |
| Project Items | [List](#project-items-list), [Context Store Search](#project-items-context-store-search) |
| Discussions | [List](#discussions-list), [Get](#discussions-get), [API Search](#discussions-api-search), [Context Store Search](#discussions-context-store-search) |
| File Content | [Get](#file-content-get), [Context Store Search](#file-content-context-store-search) |
| Directory Content | [List](#directory-content-list), [Context Store Search](#directory-content-context-store-search) |

## Repositories

### Repositories Get

Gets information about a specific GitHub repository using GraphQL

#### Python SDK

```python
await github.repositories.get(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository (username or organization) |
| `repo` | `string` | Yes | The name of the repository |
| `fields` | `array<string>` | No | Optional array of field names to select.
If not provided, uses default fields.
 |


### Repositories List

Returns a list of repositories for the specified user using GraphQL

#### Python SDK

```python
await github.repositories.list(
    username="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "list",
    "params": {
        "username": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `username` | `string` | Yes | The username of the user whose repositories to list |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select.
If not provided, uses default fields.
 |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Repositories API Search

Search for GitHub repositories using GitHub's powerful search syntax.
Examples: "language:python stars:\>1000", "topic:machine-learning", "org:facebook is:public"


#### Python SDK

```python
await github.repositories.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub repository search query using GitHub's search syntax |
| `limit` | `integer` | No | Number of results to return |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select.
If not provided, uses default fields.
 |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |
| `total_count` | `integer` |  |

</details>

### Repositories Context Store Search

Search and filter repositories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.repositories.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "repositories",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the repository |
| `name` | `string` | Short repository name (without owner) |
| `nameWithOwner` | `string` | Fully-qualified `owner/name` identifier for the repository |
| `description` | `string` | Short description of the repository |
| `url` | `string` | Canonical GitHub URL for the repository |
| `createdAt` | `string` | ISO 8601 timestamp when the repository was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the repository was last updated |
| `pushedAt` | `string` | ISO 8601 timestamp of the most recent push to the repository |
| `forkCount` | `integer` | Number of forks of the repository |
| `stargazerCount` | `integer` | Number of users who have starred the repository |
| `isPrivate` | `boolean` | Whether the repository is private |
| `isFork` | `boolean` | Whether the repository is a fork of another repository |
| `isArchived` | `boolean` | Whether the repository has been archived |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the repository |
| `data[].name` | `string` | Short repository name (without owner) |
| `data[].nameWithOwner` | `string` | Fully-qualified `owner/name` identifier for the repository |
| `data[].description` | `string` | Short description of the repository |
| `data[].url` | `string` | Canonical GitHub URL for the repository |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the repository was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the repository was last updated |
| `data[].pushedAt` | `string` | ISO 8601 timestamp of the most recent push to the repository |
| `data[].forkCount` | `integer` | Number of forks of the repository |
| `data[].stargazerCount` | `integer` | Number of users who have starred the repository |
| `data[].isPrivate` | `boolean` | Whether the repository is private |
| `data[].isFork` | `boolean` | Whether the repository is a fork of another repository |
| `data[].isArchived` | `boolean` | Whether the repository has been archived |

</details>

## Org Repositories

### Org Repositories List

Returns a list of repositories for the specified organization using GraphQL

#### Python SDK

```python
await github.org_repositories.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "org_repositories",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Org Repositories Context Store Search

Search and filter org repositories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.org_repositories.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "org_repositories",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Branches

### Branches List

Returns a list of branches for the specified repository using GraphQL

#### Python SDK

```python
await github.branches.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Branches Get

Gets information about a specific branch using GraphQL

#### Python SDK

```python
await github.branches.get(
    owner="<str>",
    repo="<str>",
    branch="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "branch": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `branch` | `string` | Yes | The branch name |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Branches Context Store Search

Search and filter branches records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.branches.context_store_search(
    query={"filter": {"eq": {"name": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"name": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` | Branch name (e.g. `main`, `feature/foo`) |
| `prefix` | `string` | Git ref prefix for the branch (typically `refs/heads/`) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].name` | `string` | Branch name (e.g. `main`, `feature/foo`) |
| `data[].prefix` | `string` | Git ref prefix for the branch (typically `refs/heads/`) |

</details>

## Commits

### Commits List

Returns a list of commits for the default branch using GraphQL

#### Python SDK

```python
await github.commits.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `path` | `string` | No | Only include commits that modified this file path (e.g. "airbyte-integrations/connectors/source-stripe/") |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Commits Get

Gets information about a specific commit by SHA using GraphQL

#### Python SDK

```python
await github.commits.get(
    owner="<str>",
    repo="<str>",
    sha="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "sha": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `sha` | `string` | Yes | The commit SHA |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Commits Context Store Search

Search and filter commits records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.commits.context_store_search(
    query={"filter": {"eq": {"oid": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"oid": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `oid` | `string` | Full Git commit SHA |
| `abbreviatedOid` | `string` | Abbreviated Git commit SHA (typically 7 characters) |
| `messageHeadline` | `string` | First line of the commit message |
| `message` | `string` | Full commit message |
| `committedDate` | `string` | ISO 8601 timestamp when the commit was applied to its tree |
| `authoredDate` | `string` | ISO 8601 timestamp when the commit was originally authored |
| `additions` | `integer` | Number of lines added across all files in the commit |
| `deletions` | `integer` | Number of lines deleted across all files in the commit |
| `changedFiles` | `integer` | Number of files changed in the commit |
| `url` | `string` | Permalink to the commit on GitHub |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].oid` | `string` | Full Git commit SHA |
| `data[].abbreviatedOid` | `string` | Abbreviated Git commit SHA (typically 7 characters) |
| `data[].messageHeadline` | `string` | First line of the commit message |
| `data[].message` | `string` | Full commit message |
| `data[].committedDate` | `string` | ISO 8601 timestamp when the commit was applied to its tree |
| `data[].authoredDate` | `string` | ISO 8601 timestamp when the commit was originally authored |
| `data[].additions` | `integer` | Number of lines added across all files in the commit |
| `data[].deletions` | `integer` | Number of lines deleted across all files in the commit |
| `data[].changedFiles` | `integer` | Number of files changed in the commit |
| `data[].url` | `string` | Permalink to the commit on GitHub |

</details>

## Releases

### Releases List

Returns a list of releases for the specified repository using GraphQL

#### Python SDK

```python
await github.releases.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Releases Get

Gets information about a specific release by tag name using GraphQL

#### Python SDK

```python
await github.releases.get(
    owner="<str>",
    repo="<str>",
    tag="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "tag": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `tag` | `string` | Yes | The release tag name |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Releases Context Store Search

Search and filter releases records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.releases.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the release |
| `databaseId` | `integer` | REST API numeric identifier for the release |
| `name` | `string` | Display name of the release |
| `tagName` | `string` | Git tag the release points at (e.g. `v1.2.3`) |
| `description` | `string` | Markdown body / release notes |
| `publishedAt` | `string` | ISO 8601 timestamp when the release was published |
| `createdAt` | `string` | ISO 8601 timestamp when the release was created |
| `isPrerelease` | `boolean` | Whether the release is marked as a pre-release |
| `isDraft` | `boolean` | Whether the release is still a draft and not published |
| `url` | `string` | Permalink to the release on GitHub |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the release |
| `data[].databaseId` | `integer` | REST API numeric identifier for the release |
| `data[].name` | `string` | Display name of the release |
| `data[].tagName` | `string` | Git tag the release points at (e.g. `v1.2.3`) |
| `data[].description` | `string` | Markdown body / release notes |
| `data[].publishedAt` | `string` | ISO 8601 timestamp when the release was published |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the release was created |
| `data[].isPrerelease` | `boolean` | Whether the release is marked as a pre-release |
| `data[].isDraft` | `boolean` | Whether the release is still a draft and not published |
| `data[].url` | `string` | Permalink to the release on GitHub |

</details>

## Issues

### Issues List

Returns a list of issues for the specified repository using GraphQL

#### Python SDK

```python
await github.issues.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED">` | No | Filter by issue state |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Issues Get

Gets information about a specific issue using GraphQL

#### Python SDK

```python
await github.issues.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The issue number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Issues API Search

Search for issues using GitHub's search syntax

#### Python SDK

```python
await github.issues.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub issue search query using GitHub's search syntax |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |
| `total_count` | `integer` |  |

</details>

### Issues Create

Creates a new issue in the specified repository.
Any user with pull access to a repository can create an issue.
Labels and assignees are silently dropped if the authenticated user does not have push access.


#### Python SDK

```python
await github.issues.create(
    title="<str>",
    body="<str>",
    labels=[],
    assignees=[],
    milestone=0,
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "create",
    "params": {
        "title": "<str>",
        "body": "<str>",
        "labels": [],
        "assignees": [],
        "milestone": 0,
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | Yes | The title of the issue |
| `body` | `string` | No | The contents of the issue (supports Markdown) |
| `labels` | `array<string>` | No | Labels to associate with this issue (requires push access) |
| `assignees` | `array<string>` | No | Logins for users to assign to this issue (requires push access) |
| `milestone` | `integer \| null` | No | The number of the milestone to associate this issue with (requires push access) |
| `owner` | `string` | Yes | The account owner of the repository (username or organization) |
| `repo` | `string` | Yes | The name of the repository |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `node_id` | `string` |  |
| `url` | `string` |  |
| `repository_url` | `string` |  |
| `labels_url` | `string` |  |
| `comments_url` | `string` |  |
| `events_url` | `string` |  |
| `html_url` | `string` |  |
| `number` | `integer` |  |
| `state` | `string` |  |
| `state_reason` | `string \| null` |  |
| `title` | `string` |  |
| `body` | `string \| null` |  |
| `user` | `object \| null` |  |
| `labels` | `array<object>` |  |
| `assignees` | `array<object>` |  |
| `milestone` | `object \| null` |  |
| `locked` | `boolean` |  |
| `comments` | `integer` |  |
| `closed_at` | `string \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `author_association` | `string` |  |
| `active_lock_reason` | `string \| null` |  |
| `closed_by` | `object \| null` |  |
| `timeline_url` | `string` |  |
| `performed_via_github_app` | `object \| null` |  |
| `assignee` | `object \| null` |  |
| `reactions` | `object` |  |
| `sub_issues_summary` | `object` |  |
| `type` | `object \| null` |  |
| `pinned_comment` | `object \| null` |  |
| `issue_field_values` | `array<object>` |  |
| `issue_dependencies_summary` | `object` |  |


</details>

### Issues Update

Updates an existing issue in the specified repository.
Use this to close/reopen issues, change title/body, add/remove labels, assign users, or set milestones.
Any user with push access can update an issue.


#### Python SDK

```python
await github.issues.update(
    title="<str>",
    body="<str>",
    state="<str>",
    state_reason="<str>",
    labels=[],
    assignees=[],
    milestone=0,
    owner="<str>",
    repo="<str>",
    issue_number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "update",
    "params": {
        "title": "<str>",
        "body": "<str>",
        "state": "<str>",
        "state_reason": "<str>",
        "labels": [],
        "assignees": [],
        "milestone": 0,
        "owner": "<str>",
        "repo": "<str>",
        "issue_number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | No | The title of the issue |
| `body` | `string` | No | The contents of the issue (supports Markdown) |
| `state` | `"open" \| "closed"` | No | State of the issue: open or closed |
| `state_reason` | `string \| null` | No | Reason for the state change: completed, not_planned, reopened, or null |
| `labels` | `array<string>` | No | Labels to set on this issue (replaces all existing labels; requires push access) |
| `assignees` | `array<string>` | No | Logins for users to assign to this issue (replaces all existing assignees; requires push access) |
| `milestone` | `integer \| null` | No | The number of the milestone to associate this issue with, or null to remove the milestone (requires push access) |
| `owner` | `string` | Yes | The account owner of the repository (username or organization) |
| `repo` | `string` | Yes | The name of the repository |
| `issue_number` | `integer` | Yes | The number that identifies the issue |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `node_id` | `string` |  |
| `url` | `string` |  |
| `repository_url` | `string` |  |
| `labels_url` | `string` |  |
| `comments_url` | `string` |  |
| `events_url` | `string` |  |
| `html_url` | `string` |  |
| `number` | `integer` |  |
| `state` | `string` |  |
| `state_reason` | `string \| null` |  |
| `title` | `string` |  |
| `body` | `string \| null` |  |
| `user` | `object \| null` |  |
| `labels` | `array<object>` |  |
| `assignees` | `array<object>` |  |
| `milestone` | `object \| null` |  |
| `locked` | `boolean` |  |
| `comments` | `integer` |  |
| `closed_at` | `string \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `author_association` | `string` |  |
| `active_lock_reason` | `string \| null` |  |
| `closed_by` | `object \| null` |  |
| `timeline_url` | `string` |  |
| `performed_via_github_app` | `object \| null` |  |
| `assignee` | `object \| null` |  |
| `reactions` | `object` |  |
| `sub_issues_summary` | `object` |  |
| `type` | `object \| null` |  |
| `pinned_comment` | `object \| null` |  |
| `issue_field_values` | `array<object>` |  |
| `issue_dependencies_summary` | `object` |  |


</details>

### Issues Context Store Search

Search and filter issues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.issues.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the issue |
| `databaseId` | `integer` | REST API numeric identifier for the issue |
| `number` | `integer` | Repository-scoped issue number |
| `title` | `string` | Issue title |
| `state` | `string` | Issue state: `OPEN` or `CLOSED` |
| `stateReason` | `string` | Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`) |
| `createdAt` | `string` | ISO 8601 timestamp when the issue was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the issue was last updated |
| `closedAt` | `string` | ISO 8601 timestamp when the issue was closed, if applicable |
| `locked` | `boolean` | Whether the conversation on the issue is locked |
| `url` | `string` | Permalink to the issue on GitHub |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the issue |
| `data[].databaseId` | `integer` | REST API numeric identifier for the issue |
| `data[].number` | `integer` | Repository-scoped issue number |
| `data[].title` | `string` | Issue title |
| `data[].state` | `string` | Issue state: `OPEN` or `CLOSED` |
| `data[].stateReason` | `string` | Reason the issue is in its current state (e.g. `COMPLETED`, `NOT_PLANNED`) |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the issue was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the issue was last updated |
| `data[].closedAt` | `string` | ISO 8601 timestamp when the issue was closed, if applicable |
| `data[].locked` | `boolean` | Whether the conversation on the issue is locked |
| `data[].url` | `string` | Permalink to the issue on GitHub |

</details>

## Comments

### Comments Create

Creates a comment on the specified issue.
This endpoint works for both issues and pull requests, since pull requests are issues.
Any user with read access can create a comment.


#### Python SDK

```python
await github.comments.create(
    body="<str>",
    owner="<str>",
    repo="<str>",
    issue_number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "create",
    "params": {
        "body": "<str>",
        "owner": "<str>",
        "repo": "<str>",
        "issue_number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `body` | `string` | Yes | The contents of the comment (supports Markdown) |
| `owner` | `string` | Yes | The account owner of the repository (username or organization) |
| `repo` | `string` | Yes | The name of the repository |
| `issue_number` | `integer` | Yes | The number that identifies the issue or pull request |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `node_id` | `string` |  |
| `url` | `string` |  |
| `html_url` | `string` |  |
| `body` | `string` |  |
| `user` | `object \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `issue_url` | `string` |  |
| `author_association` | `string` |  |
| `performed_via_github_app` | `object \| null` |  |
| `reactions` | `object` |  |


</details>

### Comments List

Returns a list of comments for the specified issue using GraphQL

#### Python SDK

```python
await github.comments.list(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The issue number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Comments Get

Gets information about a specific issue comment by its GraphQL node ID.

Note: This endpoint requires a GraphQL node ID (e.g., 'IC_kwDOBZtLds6YWTMj'),
not a numeric database ID. You can obtain node IDs from the Comments_List response,
where each comment includes both 'id' (node ID) and 'databaseId' (numeric ID).


#### Python SDK

```python
await github.comments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The GraphQL node ID of the comment |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Comments Context Store Search

Search and filter comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.comments.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "comments",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the comment |
| `databaseId` | `integer` | REST API numeric identifier for the comment |
| `body` | `string` | Markdown body of the comment |
| `createdAt` | `string` | ISO 8601 timestamp when the comment was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the comment was last updated |
| `url` | `string` | Permalink to the comment on GitHub |
| `isMinimized` | `boolean` | Whether the comment has been hidden/collapsed |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the comment |
| `data[].databaseId` | `integer` | REST API numeric identifier for the comment |
| `data[].body` | `string` | Markdown body of the comment |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the comment was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the comment was last updated |
| `data[].url` | `string` | Permalink to the comment on GitHub |
| `data[].isMinimized` | `boolean` | Whether the comment has been hidden/collapsed |

</details>

## Pull Requests

### Pull Requests Create

Creates a new pull request in the specified repository.
To open or update a pull request in a public repository, you must have write access to the head or the source branch.


#### Python SDK

```python
await github.pull_requests.create(
    title="<str>",
    head="<str>",
    base="<str>",
    body="<str>",
    draft=True,
    maintainer_can_modify=True,
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "create",
    "params": {
        "title": "<str>",
        "head": "<str>",
        "base": "<str>",
        "body": "<str>",
        "draft": True,
        "maintainer_can_modify": True,
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `title` | `string` | Yes | The title of the new pull request |
| `head` | `string` | Yes | The name of the branch where your changes are implemented. For cross-repository pull requests in the same network, namespace head with a user like this: username:branch |
| `base` | `string` | Yes | The name of the branch you want the changes pulled into (e.g. main) |
| `body` | `string` | No | The contents of the pull request (supports Markdown) |
| `draft` | `boolean` | No | Indicates whether the pull request is a draft |
| `maintainer_can_modify` | `boolean` | No | Indicates whether maintainers can modify the pull request |
| `owner` | `string` | Yes | The account owner of the repository (username or organization) |
| `repo` | `string` | Yes | The name of the repository |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `node_id` | `string` |  |
| `url` | `string` |  |
| `html_url` | `string` |  |
| `diff_url` | `string` |  |
| `patch_url` | `string` |  |
| `number` | `integer` |  |
| `state` | `string` |  |
| `locked` | `boolean` |  |
| `title` | `string` |  |
| `body` | `string \| null` |  |
| `user` | `object \| null` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `closed_at` | `string \| null` |  |
| `merged_at` | `string \| null` |  |
| `merge_commit_sha` | `string \| null` |  |
| `draft` | `boolean` |  |
| `head` | `object` |  |
| `base` | `object` |  |
| `author_association` | `string` |  |
| `labels` | `array<object>` |  |
| `milestone` | `object \| null` |  |
| `assignees` | `array<object>` |  |
| `requested_reviewers` | `array<object>` |  |
| `comments` | `integer` |  |
| `review_comments` | `integer` |  |
| `commits` | `integer` |  |
| `additions` | `integer` |  |
| `deletions` | `integer` |  |
| `changed_files` | `integer` |  |


</details>

### Pull Requests List

Returns a list of pull requests for the specified repository using GraphQL

#### Python SDK

```python
await github.pull_requests.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED" \| "MERGED">` | No | Filter by pull request state |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Pull Requests Get

Gets information about a specific pull request using GraphQL

#### Python SDK

```python
await github.pull_requests.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The pull request number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Pull Requests API Search

Search for pull requests using GitHub's search syntax

#### Python SDK

```python
await github.pull_requests.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub pull request search query using GitHub's search syntax |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |
| `total_count` | `integer` |  |

</details>

### Pull Requests Context Store Search

Search and filter pull requests records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.pull_requests.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pull_requests",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the pull request |
| `databaseId` | `integer` | REST API numeric identifier for the pull request |
| `number` | `integer` | Repository-scoped pull request number |
| `title` | `string` | Pull request title |
| `state` | `string` | Pull request state: `OPEN`, `CLOSED`, or `MERGED` |
| `isDraft` | `boolean` | Whether the pull request is still a draft |
| `merged` | `boolean` | Whether the pull request has been merged |
| `createdAt` | `string` | ISO 8601 timestamp when the pull request was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the pull request was last updated |
| `closedAt` | `string` | ISO 8601 timestamp when the pull request was closed, if applicable |
| `mergedAt` | `string` | ISO 8601 timestamp when the pull request was merged, if applicable |
| `baseRefName` | `string` | Name of the branch being merged into |
| `headRefName` | `string` | Name of the branch with the proposed changes |
| `url` | `string` | Permalink to the pull request on GitHub |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the pull request |
| `data[].databaseId` | `integer` | REST API numeric identifier for the pull request |
| `data[].number` | `integer` | Repository-scoped pull request number |
| `data[].title` | `string` | Pull request title |
| `data[].state` | `string` | Pull request state: `OPEN`, `CLOSED`, or `MERGED` |
| `data[].isDraft` | `boolean` | Whether the pull request is still a draft |
| `data[].merged` | `boolean` | Whether the pull request has been merged |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the pull request was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the pull request was last updated |
| `data[].closedAt` | `string` | ISO 8601 timestamp when the pull request was closed, if applicable |
| `data[].mergedAt` | `string` | ISO 8601 timestamp when the pull request was merged, if applicable |
| `data[].baseRefName` | `string` | Name of the branch being merged into |
| `data[].headRefName` | `string` | Name of the branch with the proposed changes |
| `data[].url` | `string` | Permalink to the pull request on GitHub |

</details>

## Reviews

### Reviews List

Returns a list of reviews for the specified pull request using GraphQL

#### Python SDK

```python
await github.reviews.list(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reviews",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The pull request number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Reviews Context Store Search

Search and filter reviews records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.reviews.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "reviews",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the review |
| `databaseId` | `integer` | REST API numeric identifier for the review |
| `state` | `string` | Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED` |
| `body` | `string` | Review body text |
| `submittedAt` | `string` | ISO 8601 timestamp when the review was submitted |
| `createdAt` | `string` | ISO 8601 timestamp when the review was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the review was last updated |
| `url` | `string` | Permalink to the review on GitHub |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the review |
| `data[].databaseId` | `integer` | REST API numeric identifier for the review |
| `data[].state` | `string` | Review state: `PENDING`, `COMMENTED`, `APPROVED`, `CHANGES_REQUESTED`, or `DISMISSED` |
| `data[].body` | `string` | Review body text |
| `data[].submittedAt` | `string` | ISO 8601 timestamp when the review was submitted |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the review was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the review was last updated |
| `data[].url` | `string` | Permalink to the review on GitHub |

</details>

## Pr Comments

### Pr Comments List

Returns a list of comments for the specified pull request using GraphQL

#### Python SDK

```python
await github.pr_comments.list(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pr_comments",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The pull request number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Pr Comments Get

Gets information about a specific pull request comment by its GraphQL node ID.

Note: This endpoint requires a GraphQL node ID (e.g., 'IC_kwDOBZtLds6YWTMj'),
not a numeric database ID. You can obtain node IDs from the PRComments_List response,
where each comment includes both 'id' (node ID) and 'databaseId' (numeric ID).


#### Python SDK

```python
await github.pr_comments.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pr_comments",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The GraphQL node ID of the comment |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Pr Comments Context Store Search

Search and filter pr comments records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.pr_comments.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pr_comments",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Labels

### Labels List

Returns a list of labels for the specified repository using GraphQL

#### Python SDK

```python
await github.labels.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Labels Get

Gets information about a specific label by name using GraphQL

#### Python SDK

```python
await github.labels.get(
    owner="<str>",
    repo="<str>",
    name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `name` | `string` | Yes | The label name |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Labels Context Store Search

Search and filter labels records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.labels.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "labels",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the label |
| `name` | `string` | Label name |
| `color` | `string` | Label color as a 6-character hex string without a leading `#` |
| `description` | `string` | Short description of what the label is used for |
| `createdAt` | `string` | ISO 8601 timestamp when the label was created |
| `url` | `string` | Permalink to the label on GitHub |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the label |
| `data[].name` | `string` | Label name |
| `data[].color` | `string` | Label color as a 6-character hex string without a leading `#` |
| `data[].description` | `string` | Short description of what the label is used for |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the label was created |
| `data[].url` | `string` | Permalink to the label on GitHub |

</details>

## Milestones

### Milestones List

Returns a list of milestones for the specified repository using GraphQL

#### Python SDK

```python
await github.milestones.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED">` | No | Filter by milestone state |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Milestones Get

Gets information about a specific milestone by number using GraphQL

#### Python SDK

```python
await github.milestones.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The milestone number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Milestones Context Store Search

Search and filter milestones records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.milestones.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "milestones",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the milestone |
| `number` | `integer` | Repository-scoped milestone number |
| `title` | `string` | Milestone title |
| `description` | `string` | Milestone description |
| `state` | `string` | Milestone state: `OPEN` or `CLOSED` |
| `dueOn` | `string` | ISO 8601 timestamp for the milestone's due date, if set |
| `closedAt` | `string` | ISO 8601 timestamp when the milestone was closed, if applicable |
| `createdAt` | `string` | ISO 8601 timestamp when the milestone was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the milestone was last updated |
| `progressPercentage` | `number` | Percentage of associated issues/PRs that are closed |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the milestone |
| `data[].number` | `integer` | Repository-scoped milestone number |
| `data[].title` | `string` | Milestone title |
| `data[].description` | `string` | Milestone description |
| `data[].state` | `string` | Milestone state: `OPEN` or `CLOSED` |
| `data[].dueOn` | `string` | ISO 8601 timestamp for the milestone's due date, if set |
| `data[].closedAt` | `string` | ISO 8601 timestamp when the milestone was closed, if applicable |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the milestone was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the milestone was last updated |
| `data[].progressPercentage` | `number` | Percentage of associated issues/PRs that are closed |

</details>

## Organizations

### Organizations Get

Gets information about a specific organization using GraphQL

#### Python SDK

```python
await github.organizations.get(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "get",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Organizations List

Returns a list of organizations the user belongs to using GraphQL

#### Python SDK

```python
await github.organizations.list(
    username="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "list",
    "params": {
        "username": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `username` | `string` | Yes | The username of the user |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Organizations Context Store Search

Search and filter organizations records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.organizations.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "organizations",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the organization |
| `databaseId` | `integer` | REST API numeric identifier for the organization |
| `login` | `string` | Organization login/handle (unique URL slug) |
| `name` | `string` | Display name of the organization |
| `description` | `string` | Short public description of the organization |
| `email` | `string` | Public contact email for the organization, if set |
| `location` | `string` | Public location of the organization, if set |
| `isVerified` | `boolean` | Whether the organization has a verified domain |
| `createdAt` | `string` | ISO 8601 timestamp when the organization was created |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the organization |
| `data[].databaseId` | `integer` | REST API numeric identifier for the organization |
| `data[].login` | `string` | Organization login/handle (unique URL slug) |
| `data[].name` | `string` | Display name of the organization |
| `data[].description` | `string` | Short public description of the organization |
| `data[].email` | `string` | Public contact email for the organization, if set |
| `data[].location` | `string` | Public location of the organization, if set |
| `data[].isVerified` | `boolean` | Whether the organization has a verified domain |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the organization was created |

</details>

## Users

### Users Get

Gets information about a specific user using GraphQL

#### Python SDK

```python
await github.users.get(
    username="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "username": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `username` | `string` | Yes | The username of the user |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Users List

Returns a list of members for the specified organization using GraphQL

#### Python SDK

```python
await github.users.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Users API Search

Search for GitHub users using search syntax

#### Python SDK

```python
await github.users.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub user search query using GitHub's search syntax |
| `limit` | `integer` | No | Number of results to return |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |
| `total_count` | `integer` |  |

</details>

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.users.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the user |
| `databaseId` | `integer` | REST API numeric identifier for the user |
| `login` | `string` | User login/handle |
| `name` | `string` | Public display name of the user, if set |
| `email` | `string` | Public email address of the user, if set |
| `company` | `string` | Public company affiliation of the user, if set |
| `location` | `string` | Public location of the user, if set |
| `twitterUsername` | `string` | Public Twitter/X username of the user, if set |
| `url` | `string` | Permalink to the user's profile on GitHub |
| `createdAt` | `string` | ISO 8601 timestamp when the user account was created |
| `isHireable` | `boolean` | Whether the user has marked themselves as available for hire |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the user |
| `data[].databaseId` | `integer` | REST API numeric identifier for the user |
| `data[].login` | `string` | User login/handle |
| `data[].name` | `string` | Public display name of the user, if set |
| `data[].email` | `string` | Public email address of the user, if set |
| `data[].company` | `string` | Public company affiliation of the user, if set |
| `data[].location` | `string` | Public location of the user, if set |
| `data[].twitterUsername` | `string` | Public Twitter/X username of the user, if set |
| `data[].url` | `string` | Permalink to the user's profile on GitHub |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the user account was created |
| `data[].isHireable` | `boolean` | Whether the user has marked themselves as available for hire |

</details>

## Teams

### Teams List

Returns a list of teams for the specified organization using GraphQL

#### Python SDK

```python
await github.teams.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Teams Get

Gets information about a specific team using GraphQL

#### Python SDK

```python
await github.teams.get(
    org="<str>",
    team_slug="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "get",
    "params": {
        "org": "<str>",
        "team_slug": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `team_slug` | `string` | Yes | The team slug |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Teams Context Store Search

Search and filter teams records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.teams.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "teams",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the team |
| `databaseId` | `integer` | REST API numeric identifier for the team |
| `slug` | `string` | URL-friendly slug for the team within its organization |
| `name` | `string` | Display name of the team |
| `description` | `string` | Short description of the team |
| `privacy` | `string` | Team visibility: `SECRET` or `VISIBLE` |
| `url` | `string` | Permalink to the team on GitHub |
| `createdAt` | `string` | ISO 8601 timestamp when the team was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the team was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the team |
| `data[].databaseId` | `integer` | REST API numeric identifier for the team |
| `data[].slug` | `string` | URL-friendly slug for the team within its organization |
| `data[].name` | `string` | Display name of the team |
| `data[].description` | `string` | Short description of the team |
| `data[].privacy` | `string` | Team visibility: `SECRET` or `VISIBLE` |
| `data[].url` | `string` | Permalink to the team on GitHub |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the team was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the team was last updated |

</details>

## Tags

### Tags List

Returns a list of tags for the specified repository using GraphQL

#### Python SDK

```python
await github.tags.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Tags Get

Gets information about a specific tag by name using GraphQL

#### Python SDK

```python
await github.tags.get(
    owner="<str>",
    repo="<str>",
    tag="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "tag": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `tag` | `string` | Yes | The tag name |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Tags Context Store Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.tags.context_store_search(
    query={"filter": {"eq": {"name": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"name": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` | Tag name (e.g. `v1.2.3`) |
| `prefix` | `string` | Git ref prefix for the tag (typically `refs/tags/`) |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].name` | `string` | Tag name (e.g. `v1.2.3`) |
| `data[].prefix` | `string` | Git ref prefix for the tag (typically `refs/tags/`) |

</details>

## Stargazers

### Stargazers List

Returns a list of users who have starred the repository using GraphQL

#### Python SDK

```python
await github.stargazers.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stargazers",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string` |  |

</details>

### Stargazers Context Store Search

Search and filter stargazers records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.stargazers.context_store_search(
    query={"filter": {"eq": {"starredAt": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stargazers",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"starredAt": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `starredAt` | `string` | ISO 8601 timestamp when the user starred the repository |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].starredAt` | `string` | ISO 8601 timestamp when the user starred the repository |

</details>

## Viewer

### Viewer Get

Gets information about the currently authenticated user.
This is useful when you don't know the username but need to access
the current user's profile, permissions, or associated resources.


#### Python SDK

```python
await github.viewer.get()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "viewer",
    "action": "get"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fields` | `array<string>` | No | Optional array of field names to select |


### Viewer Context Store Search

Search and filter viewer records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.viewer.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "viewer",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Viewer Repositories

### Viewer Repositories List

Returns a list of repositories owned by the authenticated user.
Unlike Repositories_List which requires a username, this endpoint
automatically lists repositories for the current authenticated user.


#### Python SDK

```python
await github.viewer_repositories.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "viewer_repositories",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Viewer Repositories Context Store Search

Search and filter viewer repositories records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.viewer_repositories.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "viewer_repositories",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Projects

### Projects List

Returns a list of GitHub Projects V2 for the specified organization.
Projects V2 are the new project boards that replaced classic projects.


#### Python SDK

```python
await github.projects.list(
    org="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "list",
    "params": {
        "org": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Projects Get

Gets information about a specific GitHub Project V2 by number

#### Python SDK

```python
await github.projects.get(
    org="<str>",
    project_number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "org": "<str>",
        "project_number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `project_number` | `integer` | Yes | The project number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Projects Context Store Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.projects.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` | GraphQL node ID of the project |
| `number` | `integer` | Organization- or user-scoped project number |
| `title` | `string` | Project title |
| `shortDescription` | `string` | Short description displayed on the project summary |
| `url` | `string` | Permalink to the project on GitHub |
| `closed` | `boolean` | Whether the project has been closed |
| `public` | `boolean` | Whether the project is publicly visible |
| `createdAt` | `string` | ISO 8601 timestamp when the project was created |
| `updatedAt` | `string` | ISO 8601 timestamp when the project was last updated |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `string` | GraphQL node ID of the project |
| `data[].number` | `integer` | Organization- or user-scoped project number |
| `data[].title` | `string` | Project title |
| `data[].shortDescription` | `string` | Short description displayed on the project summary |
| `data[].url` | `string` | Permalink to the project on GitHub |
| `data[].closed` | `boolean` | Whether the project has been closed |
| `data[].public` | `boolean` | Whether the project is publicly visible |
| `data[].createdAt` | `string` | ISO 8601 timestamp when the project was created |
| `data[].updatedAt` | `string` | ISO 8601 timestamp when the project was last updated |

</details>

## Project Items

### Project Items List

Returns a list of items (issues, pull requests, draft issues) in a GitHub Project V2.
Each item includes its field values like Status, Priority, etc.


#### Python SDK

```python
await github.project_items.list(
    org="<str>",
    project_number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_items",
    "action": "list",
    "params": {
        "org": "<str>",
        "project_number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `org` | `string` | Yes | The organization login/username |
| `project_number` | `integer` | Yes | The project number |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination (from previous response's endCursor) |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Project Items Context Store Search

Search and filter project items records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.project_items.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_items",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Discussions

### Discussions List

Returns a list of discussions for the specified repository using GraphQL

#### Python SDK

```python
await github.discussions.list(
    owner="<str>",
    repo="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discussions",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `states` | `array<"OPEN" \| "CLOSED">` | No | Filter by discussion state |
| `answered` | `boolean` | No | Filter by answered/unanswered status |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |

</details>

### Discussions Get

Gets information about a specific discussion by number using GraphQL

#### Python SDK

```python
await github.discussions.get(
    owner="<str>",
    repo="<str>",
    number=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discussions",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "number": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `number` | `integer` | Yes | The discussion number |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Discussions API Search

Search for discussions using GitHub's search syntax

#### Python SDK

```python
await github.discussions.api_search(
    query="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discussions",
    "action": "api_search",
    "params": {
        "query": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `string` | Yes | GitHub discussion search query using GitHub's search syntax |
| `per_page` | `integer` | No | The number of results per page |
| `after` | `string` | No | Cursor for pagination |
| `fields` | `array<string>` | No | Optional array of field names to select |


<details>
<summary><b>Response Schema</b></summary>



#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `has_next_page` | `boolean` |  |
| `end_cursor` | `string \| null` |  |
| `total_count` | `integer` |  |

</details>

### Discussions Context Store Search

Search and filter discussions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.discussions.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "discussions",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## File Content

### File Content Get

Returns the text content of a file at a specific path and git ref (branch, tag, or commit SHA).
Only works for text files. Binary files will have text as null and isBinary as true.


#### Python SDK

```python
await github.file_content.get(
    owner="<str>",
    repo="<str>",
    path="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "file_content",
    "action": "get",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "path": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `path` | `string` | Yes | The file path within the repository (e.g. 'README.md' or 'src/main.py') |
| `ref` | `string` | No | The git ref to read from — branch name, tag, or commit SHA. Defaults to 'HEAD' (default branch) |
| `fields` | `array<string>` | No | Optional array of field names to select |


### File Content Context Store Search

Search and filter file content records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.file_content.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "file_content",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Directory Content

### Directory Content List

Returns a list of files and subdirectories at a specific path in the repository.
Each entry includes the name, type (blob for files, tree for directories), and object ID.
Use this to explore repository structure before reading specific files.


#### Python SDK

```python
await github.directory_content.list(
    owner="<str>",
    repo="<str>",
    path="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "directory_content",
    "action": "list",
    "params": {
        "owner": "<str>",
        "repo": "<str>",
        "path": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `owner` | `string` | Yes | The account owner of the repository |
| `repo` | `string` | Yes | The name of the repository |
| `path` | `string` | Yes | The directory path within the repository (e.g. 'src' or 'airbyte-integrations/connectors/source-stripe') |
| `ref` | `string` | No | The git ref — branch name, tag, or commit SHA. Defaults to 'HEAD' (default branch) |
| `fields` | `array<string>` | No | Optional array of field names to select |


### Directory Content Context Store Search

Search and filter directory content records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await github.directory_content.context_store_search(
    query={"filter": {"eq": {"id": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "directory_content",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"id": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

