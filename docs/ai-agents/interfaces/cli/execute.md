---
plan: all
sidebar_position: 4
---

# Execute operations

`connectors execute` runs an action against an entity on a configured connector. Use it for reads, searches, creates, and updates.

Always run [`connectors describe`](./describe-connector) before executing. The describe response is the source of truth for entity names, action names, action parameters, and fields.

## Basic command

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title", "state"],
  "params": {
    "limit": 10
  }
}'
```

Required input:

- `id`, or `name` with `workspace`, to choose the connector.
- `entity`, such as `issues`, `contacts`, or `messages`.
- `action`, such as `context_store_search`, `list`, `get`, `api_search`, `create`, or `update`.

Optional input:

- `params`: action-specific parameters.
- `select_fields`: fields to include in the connector response.
- `exclude_fields`: fields to remove from the connector response.
- `skip_truncation`: disables automatic truncation of long text fields in list and search responses. This maps to `--skip-truncation` when using per-parameter flags.

## Choose an action

The actions available on a connector come from `connectors describe`. Many connectors support some of these actions:

- **`context_store_search`**: Search or filter the indexed Context Store. Prefer this for reads when indexed data is acceptable.
- **`list`**: Read live data from the source. Use this when you need data that may not be indexed yet.
- **`get`**: Fetch one record by ID.
- **`api_search`**: Use a provider-native search surface, when the connector exposes one.
- **`create`**: Create a record in the source service.
- **`update`**: Update a record in the source service.

Don't guess an action name. If it isn't in the describe output for that connector and entity, don't call it.

## Pass action parameters

Action-specific parameters go under `params`:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title", "state"],
  "params": {
    "limit": 20,
    "query": {
      "filter": {
        "equals": {
          "state": "open"
        }
      }
    }
  }
}'
```

The exact `params` shape is connector-, entity-, and action-specific. Read it from `connectors describe`.

## Filter response fields

Use two layers of filtering when you know which fields you need.

### API-side filtering: `select_fields` and `exclude_fields`

`select_fields` and `exclude_fields` are part of the JSON payload and are forwarded to the connector execution API.

Use `select_fields` to keep only specific fields:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title", "state"],
  "params": {
    "limit": 10
  }
}'
```

Use `exclude_fields` to drop heavy or unnecessary fields:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "default",
  "name": "Slack",
  "entity": "messages",
  "action": "list",
  "exclude_fields": ["blocks", "attachments"],
  "params": {
    "limit": 10
  }
}'
```

If you pass both, the API gives `select_fields` priority.

### Client-side filtering: `--fields`

`--fields` filters the JSON after the API returns it. `connectors execute` returns `{"status":"success","result": ...}` on success, so field paths start under `result`.

For object results, name the object fields you want:

```bash
airbyte-agent connectors execute --json @request.json --fields result.id,result.name
```

For array results, name the row fields you want. The CLI applies the field path to each row:

```bash
airbyte-agent connectors execute --json @request.json --fields result.number,result.title,result.state
```

Paths use dot notation. When a path crosses an array, the remaining path applies to every element. For list-style responses wrapped in `{"data": [...]}`, the CLI can also broadcast row-level paths:

```bash
airbyte-agent connectors list --json '{"workspace": "default"}' --fields id,name
```

## Load JSON from a file

For long payloads, write the request to a file:

```json
{
  "workspace": "default",
  "name": "GitHub",
  "entity": "issues",
  "action": "context_store_search",
  "select_fields": ["id", "title", "state"],
  "params": {
    "limit": 10
  }
}
```

Then run:

```bash
airbyte-agent connectors execute --json @request.json
```

`@filename` is resolved relative to the current working directory.

## Pagination

Pagination is connector- and action-specific. Use `connectors describe` to check whether the action returns a cursor, page token, offset, or provider-specific pagination fields. Pass the next-page value back under `params` using the parameter name documented by that action.
