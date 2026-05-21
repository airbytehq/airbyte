# Airbyte Agents release notes

## May 5, 2026

Web app

- You can now save changes to OAuth connectors without signing in again when your existing credentials are still valid. This fixes cases where changing only connector selections left the Save button disabled.
- Sign-in pages now show updated Airbyte Agents screenshots in both light and dark mode.
- The Connectors page now points you to every way you can add a connector: Connectors, chat, automations, the MCP server, and the API.
- Account and billing pages should load faster when billing details are slow or not cached.
- Billing admins can still use migration and plan controls when subscription IDs need repair, and the app now shows a repairable warning instead of blocking those controls.

SDK

- SDK-generated connectors now keep list results in the expected shape even when only one record matches. This fixes validation errors in connectors such as Snapchat Marketing, Chargebee, and Zendesk Chat.

Connectors

- Connector setup is more reliable when different workspaces require different sign-in fields.
- Agents can now find connected data more reliably when you filter by dates or search fields with multiple values, such as participants on a Gong call.
- Zendesk Support now includes more data in connected-data search, including articles, article attachments, automations, group memberships, macros, organization memberships, SLA policies, and triggers.
- Zoho CRM is temporarily hidden from the connector list while it is unavailable.

## May 4, 2026

Initial release of Airbyte Agents.
