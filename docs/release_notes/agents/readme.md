# Airbyte Agents release notes

## July 14, 2026

SDK

- Connector download operations can now return file content in structured, JSON-safe chunks that tell you the byte range returned and whether more content remains, so your agents can page through large downloads instead of only receiving a raw byte stream.

Connectors

- You can now manage associations between records with the HubSpot connector. Your agents can link records such as a contact to a deal or company, create labeled associations, list all associations for a record, and remove associations, making it easier to manage how your CRM records relate to one another.

## July 10, 2026

Web app

- New workspaces you create now have Context Store search enabled automatically, so your agents can search that workspace's synced data right away.
- During connector setup, your data entity selection is now locked while a connector is saving or checking its configuration, so your choices can't change unexpectedly mid-save.

## July 9, 2026

Web app

- When you create or edit a workspace, you no longer need to choose a Context Store region. That field has been removed to simplify workspace setup.
- Connector setup and configuration forms have a refreshed, more consistent appearance.
- The floating support button no longer appears while you're on a workspace chat page, reducing clutter in the chat view.

Connectors

- Fixed an issue where the Gong connector could lose access and stop syncing when its authorization token was rotated. Gong connections now stay authenticated reliably.
- The Slack connector now requests fewer permissions when you connect it, since direct message and channel-invite permissions that weren't used have been removed.

## July 8, 2026

Connectors

- You can now create, update, and delete notes, calls, emails, meetings, and tasks with the HubSpot connector, so your agents can log and manage CRM engagement activity such as adding a note to a contact or logging a call.

## July 7, 2026

Web app

- When you use chat to explore a workspace's connected data, the assistant now gathers more results before it stops, so answers to broad questions are more complete. If it reaches the limit, it lets you know the results are partial instead of stopping without explanation.

## July 6, 2026

Connectors

- When you query Google Ads campaigns, you now get each campaign's start and end dates. The Google Ads connector was also updated to a newer version of the Google Ads API, so your Google Ads data keeps flowing reliably.

## July 3, 2026

Web app

- You can now see an "Admin" badge next to admin members when managing workspace members, making it easier to identify who has administrative permissions.

SDK

- Semantic search can now return multiple matching passages from the same source record. Set the new `dedup` option to `none` to retrieve all relevant chunks, or keep the default `max` to get only the single best match per record.

Connectors

- The Linear connector now supports semantic search over issue descriptions and comments, so your agents can find relevant Linear content using natural language.
- Connectors using OAuth no longer lose refreshed tokens during health checks, which previously could cause intermittent authentication failures.

## July 2, 2026

Web app

- Workspace filter options on the Sessions page are now sorted alphabetically.
- You can now click links in connector setup field descriptions to open external documentation.

Connectors

- You can now create, update, and delete contacts, companies, and conversations with the Intercom connector.
- You can now access hourly and lifetime ad performance reports through the TikTok Marketing connector.

## July 1, 2026

Web app

- You can now filter sessions by workspace on the Sessions page, making it easier to find sessions for a specific workspace.
- Fixed an issue where workspace members on shared workspaces could not launch the connector setup experience.

MCP

- If you belong to multiple organizations, you can now list and switch between them within an MCP session using the new `list_organizations` and `use_organization` tools.

Connectors

- The GitHub connector now automatically derives the repository owner and name from your configured repository paths, improving reliability when reading data across multiple repositories.

## June 29, 2026

SDK

- Fixed an issue where responses from connectors using record transforms returned only the transformed fields instead of the complete record. All original fields are now preserved alongside transformed values.

Connectors

- You can now create, update, and delete Shopify data through your agent, including customers, products, draft orders, discount codes, blog posts, pages, inventory levels, collections, and metafields.
- Search results from Freshdesk, Gong, Linear, Slack, and Zendesk Support now automatically include related names and context. For example, Freshdesk ticket results show the requester's name and email, and Slack messages include the author's display name.

## June 26, 2026

Web app

- Fixed an issue where adding or removing workspace members could fail or behave incorrectly when editing multiple members at once.

Connectors

- Your agents can now create and update contacts, deals, companies, and tickets in HubSpot.
- The Google Ads connector has been upgraded from API version 20 to version 23 for continued compatibility with Google's platform.
- Fixed an issue where connector health checks could fail when your configuration included multiple values for fields like property IDs or account IDs.

## June 25, 2026

Web app

- Your recent chats in the sidebar now show only conversations from your current workspace.
- When you create or edit a workspace, the member picker now scrolls properly with long lists and options are sorted alphabetically. The workspace picker is also centered correctly on mobile devices.
- New workspaces you create now default to private visibility. Minting API tokens for a workspace now requires workspace admin access.

Connectors

- The Facebook Marketing connector now uses Facebook Graph API v25.0 for improved compatibility.

## June 24, 2026

Web app

- When new members accept an organization invitation, they now automatically receive access to all shared workspaces in the organization.

MCP

- Fixed an issue where some connectors were not accessible through the Airbyte Agent MCP when using organization-scoped or operator tokens.

SDK

- SDK models are now forward-compatible with new connector registry extensions, preventing unexpected validation errors when connector specifications evolve.
- The SDK now only includes connectors that are publicly available, removing experimental connectors from packages and documentation.

Connectors

- The Exa connector is now available for all users. Exa provides AI-powered web search and content retrieval.
- Updated the Monday connector (v2.0.0) for forward-compatibility with monday.com's upcoming July 2026 API changes. Some deprecated User fields have been removed from the cached data schema.

## June 23, 2026

Web app

- You can now add team members directly when creating a new workspace, so everyone has access from the start.
- The workspace picker shows an "Admin" badge on workspaces where you have admin privileges.
- Switching workspaces while in a chat shows a toast confirming which workspace you switched to.
- Member lists in workspace settings are now sorted alphabetically.

Connectors

- Gong call transcripts now support semantic search, allowing your agent to find relevant conversations based on meaning rather than exact keyword matches.
- Your agent can now search GitHub data using more natural field names, and sorting results by fields like creation date works correctly.

## June 19, 2026

Web app

- Chat connections to your agent are now more reliable. If the initial connection fails due to a temporary network issue, the app automatically retries instead of showing an error.

SDK

- Fixed an issue where connectors with an empty authentication header prefix would send a leading space in API requests, potentially causing authentication failures.

Connectors

- The Shopify connector is now generally available. You can connect your Shopify store to read orders, products, customers, inventory, and more.
- Amazon Ads entities such as campaigns, ad groups, and keywords are now correctly linked to advertising profiles, so your agent can resolve data across multiple accounts more accurately.
- Fixed an issue where certain connectors were not displayed correctly in your connector list and could not be used by your agent.

Other

- Upgraded the AI model powering Chats and Automations for improved response quality.

## June 18, 2026

Web app

- Your credentials page now shows a "Direct only" badge on connectors that support direct queries but not Context Store search.
- The option to convert a chat to an automation is no longer available in the chat interface.
- The "New workspace" button now appears at the top of the workspace picker for faster access.
- Fixed an issue where shared workspaces could be hidden from organization members who didn't have a direct workspace grant.

Connectors

- Setting up and using direct-only connectors is now more reliable.

## June 17, 2026

Other

- The Context Store now pauses automatically for connectors that haven't been searched recently. When you next search a paused connector, it resumes immediately and you'll see a notice while its data refreshes.

## June 16, 2026

API

- You now see only the workspaces you belong to, and deleting a workspace requires workspace admin permission.

Connectors

- The incident.io connector now lets you list and retrieve teams from your incident.io account.

## June 15, 2026

Web app

- You can now switch between workspaces and create new ones directly from the sidebar without leaving your current page.
- The Connectors page now shows "Paused" and "Re-enabling" status indicators for the Context Store, so you can see at a glance when data indexing is temporarily inactive.
- Connectors that only support direct requests now clearly indicate that the Context Store is not available, instead of showing irrelevant status information.
- Fixed an issue where some connectors could temporarily disappear from the available connectors list during intermittent backend errors.

API

- Connector template and credential API responses now include `runtime_mode` and `supports_context_store` fields, so you can programmatically determine whether a connector supports the Context Store, direct requests, or both.

## June 12, 2026

Web app

- Chat sessions and automations are now organized by workspace. If you use multiple workspaces, your conversations and workflows stay scoped to the workspace you're working in.
- When you create a workspace, you're automatically granted admin permissions on it.
- Agents now read connector documentation before executing each operation, improving accuracy when working with your connected data.
- When your automations send Slack messages, they now include a link back to the automation for easy traceability.
- Fixed an issue where organization and workspace data could appear stale after refreshing connector credentials.
- Fixed progress indicators during connector editing to correctly show completed steps.

SDK

- New `build_connector_tools()` function builds hosted connector tools with progressive documentation lookup. Your agent inspects and reads connector docs before executing, improving accuracy. Pass `use_progressive_docs=False` to keep the single-tool behavior.

API

- Workspace-scoped tokens now properly restrict connector access to your workspace, preventing cross-workspace data access.

Connectors

- The Granola Notes entity is now pre-selected when you set up the connector.

## June 11, 2026

Web app

- Organizations on the Team or Custom plan now see connectors and credentials scoped to your active workspace, so you only see what belongs to the workspace you're working in.

API

- New endpoints let you inspect connector metadata and readiness, and discover available connector skill documentation programmatically.

CLI

- New `connectors inspect` command shows connector metadata, readiness status, and available documentation. New `skills` commands let you list, search, and read connector documentation directly from the CLI.

Connectors

- Semantic search now correctly returns only the fields your agent requests, improving the precision of data retrieval from your connected sources.

## June 9, 2026

Web app

- To prevent runaway billing, agent operations are now blocked when your organization's usage exceeds three times (3x) the Agent Operations included in your plan. A banner in the app notifies you when this threshold is reached.

Connectors

- Agents can now search Gong call transcripts at the speaker-turn level, making it easier to find what a specific person said during a call.

## June 8, 2026

Connectors

- The TikTok Marketing connector now supports Spark Ads and product catalogs, letting your agent list authorized Spark Ad posts and browse product catalog details for an advertiser.

## June 5, 2026

MCP

- New workspace management tools let you switch the active workspace for your session and check which workspace is currently selected. Workspace-scoped tools now operate on the selected workspace automatically without needing to pass the workspace name each time.
- Read-only operations through the execute endpoint (such as searching connected data) no longer require human approval, reducing friction for read queries.

Connectors

- The Slack connector now supports joining public channels, allowing your agent to add itself to channels before sending messages or performing other actions.

## June 3, 2026

Web app

- The context store status indicator now waits for data to load before displaying, preventing a brief flash of incorrect state.
- The standalone Getting Started page has been removed. You're now guided through setup as you use the app.

Connectors

- The Jira connector now supports OAuth 2.0 sign-in.
- Re-enabled the Ashby connector.

## June 2, 2026

Web app

- Sessions and Tool Calls have moved to the bottom of the sidebar for a cleaner layout.

Connectors

- Improved data synchronization for WooCommerce, LinkedIn Ads, Snapchat Marketing, Google Analytics Data API, and Slack connectors.
- Fixed an issue where non-OAuth authentication fields were not displayed during connector setup.

## June 1, 2026

CLI

- The Airbyte Agent CLI is now available with a one-line installer and browser-based sign-in.

## May 29, 2026

Web app

- Fixed permission errors that could prevent some users from viewing and creating connectors.

## May 28, 2026

Web app

- Organizations can now enable Single Sign-On (SSO) for streamlined team authentication.
- Fixed dashboard statistics to display with proper number formatting.

## May 25, 2026

Connectors

- The Salesforce connector now supports Notes and Users, including read and write operations.

## May 22, 2026

Web app

- Free-tier users now see a clear upgrade prompt when approaching plan limits.

Connectors

- The Salesforce connector now supports write operations with the necessary OAuth scopes.
- GitHub and Slack connectors now synchronize data to the context store faster.

## May 20, 2026

Connectors

- The Notion connector now supports write operations for pages, blocks, comments, and data sources.

## May 19, 2026

Web app

- Automation error details now render with markdown formatting for easier reading.
- Organization members are now sorted alphabetically in Settings.
- Chat messages stream faster with improved markdown rendering performance.

Connectors

- Fixed Asana connector to use the correct default OAuth scopes.
- Improved Salesforce agent guidance with better account ranking for financial data.

## May 18, 2026

Web app

- Fixed chat messages appearing out of order when resuming a conversation.
- Updated Granola connector setup instructions with corrected API key guidance.
- The members list in Settings now shows a loading indicator while data is being fetched.
- Improved error messages when connector setup encounters issues detecting available data.
- The agent now retries automatically when the AI provider is temporarily overloaded.

Connectors

- Linear, Asana, and Google Drive connectors now support OAuth sign-in.

## May 15, 2026

Web app

- Organizations on the Team plan now support multiple users. Invite team members from the Settings page.
- Redesigned the sign-in page with updated typography and branding.
- The mobile-only blocking view has been replaced with a non-intrusive banner.

## May 14, 2026

Web app

- A success dialog now appears after you connect your first connector.
- The Connectors page now features a Popular section and a Get Started banner to help you find connectors quickly.

Connectors

- Added transactional message operations to the Customer.io connector.
- Fixed the default start date for the Google Search Console connector.

Other

- The agent now considers which operations each connector supports, leading to more relevant suggestions.

## May 12, 2026

Web app

- Connector authentication now begins earlier in chat, so setup prompts appear sooner when you mention a new source.
- Redesigned the empty state on the Credentials page with clickable connector tiles for faster setup.
- Improved the prompt helper text in the automation builder.

Connectors

- Added the Customer.io connector with support for customer profiles, segments, campaigns, and transactional messages.
- Jira and Linear connectors now sign in correctly.
- The Slack connector now supports advanced formatting options when sending messages.

SDK

- Fixed context store search to correctly handle field names that contain dots.

## May 8, 2026

Web app

- Session history and tool call details are now visible directly in the sidebar.
- The embedded connector setup widget now closes when you click outside it, except during an active OAuth flow, credential check, or save.

Connectors

- Re-enabled the Confluence connector.
- The GitHub connector now requests only the OAuth scopes needed for each operation.

Other

- The agent now handles temporary AI provider outages more gracefully with automatic fallback retries.

## May 7, 2026

Web app

- Connector icons now appear inline in the chat header when you have fewer than ten connected sources.
- Fixed stale session data when switching between organizations.
- Improved the wording of Support Agent quick-action prompts.

Connectors

- Re-enabled the Harvest connector with OAuth authentication.
- Improved HubSpot context store search by flattening nested properties fields.

MCP

- MCP connections now refresh authentication tokens proactively to prevent mid-session failures.

## May 6, 2026

Web app

- The Connectors page now shows popular connectors when you have none configured, making it faster to get started.
- Added quick-install links for Claude Desktop, ChatGPT, and Codex in the MCP setup menu.
- The app now adapts to smaller screens with an auto-collapsing sidebar.
- Fixed rendering of bulleted and numbered lists in chat messages.
- The chat input field is now disabled while the assistant is responding.

Other

- Automation runs now properly fail after all retries are exhausted, instead of remaining in a running state.

## May 5, 2026

Web app

- Updated the Connectors page with clearer options for adding new connectors.
- Fixed an issue where changes to OAuth connector settings could not be saved.

Connectors

- Improved context store search to support date range filtering and array-valued fields such as call participants.
- Added missing Zendesk Support entities to the context store for better search coverage.
- Temporarily disabled the Zoho CRM connector.

SDK

- Fixed a bug where list responses containing a single element were incorrectly unwrapped into a scalar value.

## May 4, 2026

Initial release of Airbyte Agents.
