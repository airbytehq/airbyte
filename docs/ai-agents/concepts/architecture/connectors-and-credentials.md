---
sidebar_position: 3
---

# Connectors and credentials

A connector in Airbyte Agents is a stored credential and configuration for a third-party service. Connectors are what agents use to read, search, and write data in external systems. Each connector lives inside a [workspace](./workspaces) and is available to every [interface](../../interfaces) that can access that workspace.

## What a connector includes

When you add a connector, Airbyte stores:

- **Connector type** — Which third-party service the connector targets, identified by a `definition_id`. Browse the full catalog in [Agent connectors](../../connectors).
- **Credentials** — The API key, OAuth tokens, or other secrets needed to authenticate with the service.
- **Configuration** — Any non-credential settings the connector needs, like a list of repositories for GitHub or an account ID for an ad platform.

Airbyte validates credentials at execution time and handles OAuth token refresh automatically.

## Two ways to run connectors

Airbyte agent connectors support two operating modes.

### Hosted mode

Airbyte stores your credentials securely in the cloud and manages token refresh. Authenticate with your platform credentials, add connectors through any interface, and execute operations without managing secrets yourself. This is the default mode and the recommended starting point.

### Open source mode

Each agent connector is also an open source Python package you can install and run independently. In open source mode, you provide API credentials directly to the connector in your code. No Airbyte account is required. Use this mode when you want to manage credentials yourself or run connectors in an air-gapped environment.

For installation and usage in open source mode, see each connector's page in [Agent connectors](../../connectors).

## Connector lifecycle

A typical connector lifecycle looks like this:

1. **Add credentials** — Provide the third-party service's credentials through the [web app](../../interfaces/ui/add-connector), [API](../../interfaces/api/add-connector), or [SDK](../../interfaces/sdk/add-connector). Airbyte stores the credentials and returns a connector ID.
2. **Execute operations** — Make tool calls against the connector. Each call targets an entity and an action. See [Execute operations (API)](../../interfaces/api/execute) or [Execute operations (SDK)](../../interfaces/sdk/execute).
3. **Use the Context Store** — The [Context Store](../context-store) is enabled by default and replicates and indexes a subset of your connector data. This powers fast search operations without hitting the upstream API.

## Entities and actions {#entities-and-actions}

Each connector exposes a set of entities and actions that define what agents can do with that service.

- **Entities** are the resources the connector can access, like `contacts`, `issues`, `orders`, or `messages`.
- **Actions** describe what the agent can do with each entity. Common actions include `list`, `get`, `search`, `create`, and `download`.

The exact entities and actions vary by connector. See the connector's page in [Agent connectors](../../connectors) for the full list.

## Credential management

Airbyte Agents uses a two-layer credential model.

### Platform credentials

Platform credentials identify your organization with Airbyte. When you sign in to the web app, Airbyte authenticates you behind the scenes. For programmatic access through the API, SDK, or MCP server, your organization's `client_id`, `client_secret`, and `organization_id` — available on the [Profile page](../../admin/profile) — serve the same purpose. The platform uses these to issue short-lived tokens.

| Token type | Scope | Lifetime | Use case |
| --- | --- | --- | --- |
| Application token | Organization-wide | 15 minutes | Managing connectors, generating scoped tokens, executing operations |
| Scoped token | Single workspace | 20 minutes | Workspace-isolated access for multi-tenant apps |

For details, see [Authentication](../../interfaces/api/authentication).

### Connector credentials

Connector credentials authenticate with each third-party service. The credential shape depends on the service:

- **API key or personal access token** — A single secret. GitHub uses `personal_access_token`, Linear uses `api_key`, Notion uses `token`.
- **OAuth** — A `client_id`, `client_secret`, and `refresh_token`. Airbyte rotates access tokens automatically at execution time.

Airbyte stores all connector credentials securely. You provide them once, and Airbyte injects them into every execution request.

### Add once, use everywhere

Credentials you add through one interface are available to all of them. A connector configured in the web app works through the API, SDK, or MCP server without re-entering credentials. This applies to every interface in the platform.

## Security

- Platform tokens are short-lived by design. Application tokens expire after 15 minutes; scoped tokens expire after 20 minutes.
- Airbyte stores connector credentials server-side and never returns them in API responses after creation.
- Never expose platform credentials or tokens in client-side code. Keep them in your backend.
- Rotate platform credentials periodically from the [Profile page](https://app.airbyte.ai/profile).

## Related topics

- [Agent connectors](../../connectors) — Browse the connector catalog.
- [Authentication (API)](../../interfaces/api/authentication) — Token types and the authentication flow.
- [Authentication (SDK)](../../interfaces/sdk/authenticate) — Credential configuration for Python apps.
- [Context Store](../context-store) — The searchable replica powered by your connectors.
