# Airbyte Agents release notes

## May 8, 2026

Web app

- Sessions and tool calls are now available as first-level navigation items in the sidebar, making it easier to review recent agent activity.
- Agent Builder access no longer depends on a LaunchDarkly flag, so available organizations can reach the Agent Builder flow without a feature-flag mismatch.
- Embedded connector setup dialogs now close when you click outside them, while staying open during sign-in, configuration checks, and save steps so in-progress setup is not interrupted.

API

- Organization billing details load more reliably for recent signups by avoiding stale reads and allowing billing requests more time to complete.
- Agents are more resilient to temporary Claude provider failures because chat, workflow, and query agents can fall back to another configured model.
- Agent responses now redact mentions of competing products in more user-facing flows.

Connectors

- Confluence is available again in Airbyte Agents.
- GitHub connector OAuth setup now requests scopes based on the entities you use, so authorization can be better matched to your selected GitHub capabilities.
- Confluence, Gong, Granola, and Pylon were updated to newer replication versions.

Other

- Airbyte now sends internal Slack alerts when Context Store setup fails, helping the team detect and resolve setup problems faster.

## May 7, 2026

Web app

- Switching organizations in the admin picker now performs a full navigation and clears cached data, reducing stale session and organization state after an org switch.
- Chat headers now show connected connector icons inline when there are fewer than 10 connectors, making the active data sources easier to recognize at a glance.
- Support Agent quick-action prompts now use clearer wording, and the chat input keeps focus after submitting or stopping a response.
- The help/status view now renders non-operational service states correctly.
- The connector empty-state hero no longer appears after you have fresh credentials, so credential pages show the right next step.

MCP

- The stdio MCP server now refreshes service tokens proactively, reducing the chance of authentication interruptions during long-running sessions.

Connectors

- Harvest is available again in Airbyte Agents with OAuth credential support.
- HubSpot context search now exposes flattened company and contact properties, making searches over common HubSpot fields easier and more reliable.
- Harvest and Jira were updated to newer replication versions.

## May 6, 2026

Web app

- The Connectors page now shows a richer empty state with popular connector shortcuts and a clearer path to add a different connector.
- The MCP install menu now includes Claude, ChatGPT, and Codex setup options alongside the existing Claude Code, Cursor, VS Code, URL copy, and docs options.
- The app now warns mobile users that Airbyte Agents works best on desktop, while still allowing them to continue.
- Embedded connector setup now keeps each widget launch isolated, which prevents a previous setup attempt from leaking state into a new one.
- Chat feedback buttons now send analytics events, helping the team understand whether responses are useful.
- Markdown content now shows bulleted and numbered lists correctly.
- Support chat now disables message submission while a response is streaming.

API

- Context Store search is more reliable under concurrent query load.
- Connector execution can reuse cached source configuration when falling back to Airbyte, reducing latency for connector operations.
- Workflow runs now fail after hard retry exhaustion instead of staying in an ambiguous retry state.

Connectors

- Gmail guidance and setup behavior now better explain message detail fields and raw MIME message encoding, and experimental connector setup can use workspace-specific specs.
- Several connectors were updated to newer replication versions.

## May 5, 2026

Web app

- The sign-in page now uses clearer screenshot assets with improved styling.
- The Connectors page notice now better explains the available connector creation options.
- Embedded connector setup now supports saving edits to OAuth-based connectors.

SDK

- The connector SDK now preserves list-shaped extractor results even when an API response contains only one matching item.

API

- Organization info loads faster by fetching independent account details in parallel with per-step timeouts.
- Workspace-scoped connector specs are now available through the templates API, so experimental connector setup can show the fields required for the selected workspace.

Connectors

- Context Store search now supports date ranges and array-valued fields, making searches more precise for data such as call participants or other multi-value fields.
- Zendesk Support context search now includes additional entities.
- Zoho CRM was temporarily disabled in Airbyte Agents.
- Several connectors were updated to newer replication versions.

## May 4, 2026

Initial release of Airbyte Agents.
