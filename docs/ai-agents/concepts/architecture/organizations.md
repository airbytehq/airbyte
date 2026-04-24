---
sidebar_position: 1
---

# Organizations

An organization is the top-level container in Airbyte Agents. It represents a single account, maps to one billing subscription, and owns every workspace, connector, and credential beneath it.

## What an organization contains

Each organization has:

- **Platform API credentials** — A `client_id`, `client_secret`, and `organization_id` that authenticate programmatic access through the [API](../../interfaces/api), [SDK](../../interfaces/sdk), and [MCP server](../../interfaces/mcp). Find these on the [Profile page](https://app.airbyte.ai/profile).
- **Workspaces** — One or more [workspaces](./workspaces), each holding its own set of connectors and credentials. Every organization starts with a `default` workspace.
- **Context Store configuration** — The [Context Store](../context-store) is an organization-level setting. Administrators can turn it on or off for the entire organization from the Credentials page.
- **Billing** — Plans, payment methods, usage limits, and invoices live at the organization level. See [Billing and pricing](../../admin/billing).
- **Users** — People who can sign in and interact with the organization through the [web app](../../interfaces/ui).

## One organization per account

When you sign up at [app.airbyte.ai](https://app.airbyte.ai), Airbyte creates an organization for you automatically. Your account belongs to that organization. If you need to work across multiple organizations, your Airbyte account can be associated with more than one — pass the `organization_id` to the SDK or API to target a specific organization. See [Multiple organizations](../../interfaces/sdk/authenticate#multiple-organizations).

## Who can administer an organization

Organization administrators can:

- Rename the organization from the [Profile page](../../admin/profile).
- Manage [billing](../../admin/billing), including payment methods, spending caps, and plan changes.
- Turn the [Context Store](../context-store) on or off.
- View [sessions](../../admin/sessions) and [tool calls](../../admin/tool-calls) for the entire organization.

## Related topics

- [Profile](../../admin/profile) — View and copy API credentials, rename the organization.
- [Billing and pricing](../../admin/billing) — Plans, usage, invoices.
- [Workspaces](./workspaces) — The isolation layer within an organization.
