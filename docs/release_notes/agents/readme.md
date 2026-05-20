# Airbyte Agents release notes

## May 5, 2026

Web app

- Save edits to OAuth connectors without re-authenticating when the saved credentials are still valid. This fixes cases where changing only connector entities left the Save button disabled.
- The sign-in pages now use the updated Airbyte Agents screenshot artwork in both light and dark mode, with rounded corners and a drop shadow.
- The Connectors page now points you to every place you can add a connector: Connectors, chat, automations, the MCP server, and the API.

API

- The organization info endpoint now loads independent billing and plan details in parallel and applies timeouts to optional provider calls. This should make account pages faster on cache misses and prevent slow billing providers from delaying the whole response.
- Experimental connectors now use the workspace-scoped Airbyte connector spec when checking or creating sources. This preserves OAuth fields that were missing from the standard spec path.
- Billing admins now see repairable warnings when Stigg and Orb subscription IDs do not match, and migration or plan controls stay available when that mismatch is the only issue.
- Workspace-scoped source template specs are now available through the API. Experimental connector flows can use this endpoint to render the correct OAuth configuration for the selected workspace.

Connectors

- Context Store search now supports date ranges with both lower and upper bounds, and keyword search works on array-valued fields such as Gong call context and participants.
- Zendesk Support now exposes eight more entities in Context Store search: articles, article attachments, automations, group memberships, macros, organization memberships, SLA policies, and triggers.
- Zoho CRM is temporarily hidden from the Airbyte Agents connector list while it is unavailable.

SDK

- SDK extractors that select one item from a list now keep returning a list when the generated type expects one. This fixes validation errors for connectors such as Snapchat Marketing, Chargebee, and Zendesk Chat when an API response contains exactly one matching record.

## May 4, 2026

Initial release of Airbyte Agents.
