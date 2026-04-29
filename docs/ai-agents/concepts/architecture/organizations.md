---
sidebar_position: 1
---

# Organizations

An organization is the top-level container in Airbyte Agents. It represents a single account, maps to one billing subscription, and owns every workspace, connector, and credential beneath it.

## What an organization contains

Each organization has:

- **Platform API credentials** — A `client_id`, `client_secret`, and `organization_id` that authenticate programmatic access through the [API](../../interfaces/api), [SDK](../../interfaces/sdk), and [MCP server](../../interfaces/mcp). Find these on the [Profile page](https://app.airbyte.ai/profile).
- **Workspaces** — Every organization starts with a `default` [workspace](./workspaces), which is all most people need. If you need to isolate credentials across tenants or teams, you can create additional workspaces.
- **Context Store configuration** — The [Context Store](../context-store) is enabled by default and operates at the organization level. You can turn it on or off from the Credentials page.
- **Billing** — Plans, payment methods, usage limits, and invoices live at the organization level. See [Billing and pricing](../../admin/billing).
- **Users** — People who can sign in and interact with the organization through the [web app](../../interfaces/ui).

## One organization per account

When you sign up at [app.airbyte.ai](https://app.airbyte.ai), Airbyte creates an organization for you automatically. Your account belongs to that organization. If you need to work across multiple organizations, your Airbyte account can be associated with more than one — pass the `organization_id` to the SDK or API to target a specific organization. See [Multiple organizations](../../interfaces/sdk/authenticate#multiple-organizations).

## Related topics

- [Profile](../../admin/profile) — View and copy API credentials, rename the organization.
- [Billing and pricing](../../admin/billing) — Plans, usage, invoices.
- [Workspaces](./workspaces) — The isolation layer within an organization.
