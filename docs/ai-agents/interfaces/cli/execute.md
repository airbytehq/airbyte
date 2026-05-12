---
plan: all
sidebar_position: 5
---

# Execute operations

`connectors execute` runs an action against an entity on a connector. It's the workhorse command — every actual read, search, or write happens through it.

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "hubspot",
  "entity": "contacts",
  "action": "read",
  "select_fields": ["id", "email", "name"]
}'
```

Required fields:

- `name` (with `workspace`) or `id`: which connector to run against.
- `entity`: the resource, such as `contacts`, `issues`, `repositories`.
- `action`: an action the connector supports on that entity, such as `list`, `get`, `context_store_search`, or `read`.

Always run [`connectors describe`](./describe-connector) before the first execute on a connector. Entity and action names vary per connector and aren't guessable.

## Pick the right action

Most connectors expose a baseline set of actions. The authoritative list for a given connector comes from `connectors describe`, but as a starting point:

| Action | Purpose | Filtering |
| --- | --- | --- |
| `context_store_search` | Default for reads. Filter, sort, paginate over the indexed entity store. | Yes (rich). |
| `list` | Live read directly from the source. Use when the search index may lag or when you need today's data. | Limited. |
| `get` | Fetch a single entity by ID. | N/A. |
| `api_search` | Provider-native search (for example, Slack search syntax). | Provider-specific. |
| `create` | Write a new entity. | N/A. |
| `update` | Modify an existing entity. | N/A. |

For reads, prefer `context_store_search` unless you specifically need real-time data — the indexed store is faster and supports richer filtering. Fall back to `list` when search returns empty and you suspect indexing lag.

## Pass action-specific parameters

Action-specific arguments go under `params`. The shape is entity- and action-dependent — `describe` is authoritative:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "hubspot",
  "entity": "contacts",
  "action": "context_store_search",
  "select_fields": ["id", "email", "firstName"],
  "params": {
    "limit": 20,
    "query": {"filter": {"fuzzy": {"firstName": "Teo"}}}
  }
}'
```

## Filter the response

Unfiltered responses can be large. The CLI gives you two layers of filtering — use both whenever you know which fields you need.

### `select_fields` and `exclude_fields` (API-side)

Both belong inside the JSON payload and are forwarded to the source connector. `select_fields` is an allowlist; `exclude_fields` is a blocklist. They support dot notation for nested fields. If both are passed, `select_fields` wins.

```bash
# Keep only id, email, name
airbyte-agent connectors execute --json '{
  "workspace": "default", "name": "hubspot",
  "entity": "contacts", "action": "read",
  "select_fields": ["id", "email", "name"]
}'

# Drop heavy fields
airbyte-agent connectors execute --json '{
  "workspace": "default", "name": "hubspot",
  "entity": "messages", "action": "read",
  "exclude_fields": ["body_html", "attachments"]
}'
```

API-side filtering reduces upstream work — the source connector doesn't emit columns you don't need.

### `--fields` (client-side)

`--fields` filters the response after the API returns it. Use it to shape the printed payload without changing what the source connector emits.

```bash
airbyte-agent connectors execute --json '{...}' --fields 'data.id,data.email'
```

Paths use dot notation. When a path crosses an array, the remaining segments apply to every element ("array broadcast"). For list-style responses wrapped in `{"data": [...]}`, you can omit the `data.` prefix:

```bash
airbyte-agent organizations list --fields id,organization_name
airbyte-agent organizations list --fields data.id,data.organization_name
```

Both forms work. The CLI auto-broadcasts when no path matches a top-level key.

The two layers are complementary. Pass `select_fields` to reduce upstream work and `--fields` to keep stdout clean for human consumption. Errors are never filtered — you always see the full error payload.

## Long payloads

`execute` payloads can get long (large `query` objects, nested filters). Load them from a file with `--json @path/to/file.json`:

```bash
cat > read-contacts.json <<'JSON'
{
  "workspace": "default",
  "name": "hubspot",
  "entity": "contacts",
  "action": "context_store_search",
  "select_fields": ["id", "email", "firstName"],
  "params": {
    "limit": 50,
    "query": {
      "filter": {"and": [{"equals": {"email_status": "verified"}}]}
    }
  }
}
JSON

airbyte-agent connectors execute --json @read-contacts.json
```

`@filename` is resolved relative to the current working directory.

## Pagination

Pagination is action- and connector-specific. `list` typically accepts `cursor`, `per_page`, or both. `context_store_search` returns a `next` token alongside `data`. Run `describe` to see the exact params and the cursor shape an action returns.

## Errors

Validation errors (missing `entity`, missing `action`, malformed `params`) exit with code `4` and a JSON error on stderr. API errors include the full server response in `detail`:

```json
{
  "type": "validation_error",
  "message": "Invalid configuration",
  "status_code": 400,
  "retryable": false,
  "detail": {"errors": [{"field": "limit", "message": "must be <= 100"}]}
}
```

For the full error matrix and retry behavior, see [Troubleshooting](./troubleshooting).
