---
plan: all
sidebar_position: 4
---

# Describe a connector

`connectors describe` returns the contract for a connector: every entity it exposes, every action valid on each entity, and the parameter schema each action accepts. It's the source of truth for what a specific connector supports, and the first thing you should call before running [`connectors execute`](./execute) against an unfamiliar connector.

Entity and action names vary by connector type. Don't guess them — every guess is an avoidable round trip and, for write actions, a possible mistake.

## Describe by name

```bash
airbyte-agent connectors describe --json '{
  "workspace": "default",
  "name": "hubspot"
}'
```

`name` plus `workspace` resolves to a single connector. `workspace` falls back to the default set by [`workspaces use`](./workspaces#set-a-default-workspace) when omitted.

## Describe by ID

When a workspace has multiple connectors of the same type, pass the connector ID directly:

```bash
airbyte-agent connectors describe --id <connector_id>
```

You can get the ID from [`connectors list`](./add-connector#list-existing-connectors) or from the create response.

## Reading the output

The response is a JSON document with three sections:

- `connector`: high-level metadata (`id`, `name`, `type`, status).
- `entities`: an array of entities the connector exposes. Each entity has a `name`, a list of `actions`, and per-action parameter schemas.
- `schema`: when available, the JSON Schema for entity records the connector returns. Useful for figuring out which fields to pass to `select_fields` or `--fields`.

A trimmed example:

```jsonc
{
  "connector": { "id": "f24fb2b0-...", "name": "hubspot", "type": "HubSpot" },
  "entities": [
    {
      "name": "contacts",
      "actions": [
        { "name": "list", "params": { "limit": { "type": "integer" } } },
        { "name": "context_store_search", "params": { "query": { "type": "object" } } },
        { "name": "get", "params": { "id": { "type": "string", "required": true } } }
      ]
    }
  ]
}
```

Once you know the entity and action you want to run, pass them to [`connectors execute`](./execute).

## Trim the response

Describe responses can be large. Use `--fields` to keep only what you need:

```bash
# Just the entity and action names
airbyte-agent connectors describe --json '{"workspace": "default", "name": "hubspot"}' \
  --fields 'entities.name,entities.actions.name'
```

## When entities or actions look wrong

If `describe` returns an unexpected schema — missing entities, unexpected required params — the underlying connector definition may have changed. Re-run `connectors list-available` to make sure the connector is still available, and check the connector's [reference page](../../connectors) for the canonical entity list.
