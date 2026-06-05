# Airbyte Agents release notes

## June 3, 2026

Web app

- The Shopify shop name you enter during OAuth setup is now preserved correctly.
- The context store status indicator now waits for data to load before displaying, preventing a brief flash of incorrect state.
- The standalone Getting Started page has been removed. You're now guided through setup as you use the app.

Connectors

- The Jira connector now supports OAuth 2.0 sign-in.
- Re-enabled the Ashby connector.
- Fixed the Shopify OAuth callback listener to stay active until authentication completes.

## June 2, 2026

Web app

- Sessions and Tool Calls have moved to the bottom of the sidebar for a cleaner layout.

Connectors

- Added the Snowflake connector with read support for databases, schemas, tables, views, warehouses, and columns.
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
- Fixed Shopify OAuth integration for the embedded connector widget.

## May 18, 2026

Web app

- Fixed chat messages appearing out of order when resuming a conversation.
- Updated Granola connector setup instructions with corrected API key guidance.
- The members list in Settings now shows a loading indicator while data is being fetched.
- Improved error messages when connector setup encounters issues detecting available data.
- The agent now retries automatically when the AI provider is temporarily overloaded.

Connectors

- Linear, Asana, and Google Drive connectors now support OAuth sign-in.
- Fixed Shopify OAuth callback handling to complete authentication reliably.

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
- The Gmail connector now uses a single, more appropriate permission scope instead of multiple broad ones.

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
