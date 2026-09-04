# Airbyte Agents release notes

## September 4, 2026

Connectors

- Your agents can now search your Klaviyo email templates by meaning, including the template name and email body, so they can find templates on a similar topic without matching the exact wording.

Other

- Search by meaning is now more reliable. Previously, during periods of heavy indexing, some records could be indexed without searchable content and were silently missing from your agents' results. All records are now indexed completely.
- Indexing connectors that sync files, such as Google Drive, is now more reliable when processing large volumes of extracted text, so file indexing no longer stalls or fails partway through on big document sets.

## September 2, 2026

Web app

- Chat now searches across all of your indexed data by default, so your agent can pull in relevant records from every connector in your workspace without you turning on a setting first. Workspace-wide searches also no longer time out in workspaces with several connectors.
- Everyone in your organization can now view the API client ID and secret on the Profile page. Previously only administrators could see them, and other members saw an empty page.

## September 1, 2026

Web app

- Your connectors and Context Store now stay marked Ready when synced data hasn't been searched for a while. Previously they looked like they were still building, even though your agents could still search that data.

## August 31, 2026

Web app

- The skills page now warns you when a published skill can't be served to agents because your organization is missing one or more connectors the skill depends on, so you can set up those connectors before your agents need them.

Connectors

- The Greenhouse connector now signs in with OAuth and uses Greenhouse's latest Harvest API, adding access to interviews and file attachments alongside candidates, applications, jobs, and offers.
- Credential checks for connectors that sign in with OAuth are now more reliable. When a quick validation can't safely use your credentials, the check automatically falls back to a full validation instead of failing.

## August 28, 2026

Web app

- The Connectors page no longer shows an error on a connector whose data is ready and searchable again, so the status you see reflects how the connector is working now rather than a problem that has already been resolved.

## August 27, 2026

Web app

- Chat now keeps up with your skills while a conversation is open. If you add, edit, disable, or remove a skill mid-chat, your agent picks up the change on your next message instead of continuing to follow the old instructions. If the skill list can't be loaded for a message, the agent tells you it's temporarily unavailable and asks you to try again rather than answering from skill content it saw earlier.

SDK

- Search filters now separate text matching from list matching. Use `contains` to match part of a text field, ignoring capitalization, and the new `array_contains` to check whether a list field includes an exact value. If you previously used `contains` against a list field, switch that filter to `array_contains`.
- When you run connectors with credentials supplied from your own environment, you can now keep those credentials in Google Cloud Secret Manager in addition to AWS Secrets Manager.

## August 26, 2026

Connectors

- Your agents can now search Notion comments by meaning, so they can find relevant discussion without matching exact keywords.
- Your agents can now search Sentry issues by meaning, including the issue title and where the error happened, so they can find related problems without knowing the exact error text.
- Your agents can now search your Facebook Marketing ad creative text by meaning, including headlines and body copy, so they can find ads with similar messaging without matching exact wording.
- Your agents can now search your Customer.io campaign email content by meaning, including subject lines and message bodies, so they can find campaigns on a similar topic without matching exact wording.

Other

- Context Store data that gets stuck partway through an update now recovers on its own, so your agents keep searching current data without anyone needing to restart it.

## August 25, 2026

Connectors

- You can now search by meaning, not just exact keywords, across Slack, HubSpot, Intercom, Monday.com, Asana, Greenhouse, and TikTok Marketing. Your agents can find relevant Slack messages and threads, HubSpot tickets, notes, calls, emails, and meetings, Intercom conversations, Monday.com boards, items, and updates, Asana tasks and projects, Greenhouse job posts, and TikTok ad text without matching the wording exactly.

Other

- Search now handles content that was written as rich text, such as job descriptions and email bodies, more accurately. Formatting is stripped into clean, readable text before it's indexed, so results better reflect what the content actually says.
- Search results no longer drop identifying details, such as a record's title, from the record data they return. It's easier to tell results apart and act on the right one.

## August 24, 2026

SDK

- Text filters when searching your synced data now use `startswith` and `endswith` for prefix and suffix matches, and `contains` for a case-insensitive substring match on text fields. These replace the previous `like` operator, so your filters no longer depend on wildcard patterns.

## August 21, 2026

Connectors

- You can now search your Freshdesk data by meaning instead of exact keywords. Your agents can find relevant tickets, contact and company notes, and satisfaction survey feedback based on what the text is about, and narrow results by details like status, priority, or account tier.

Other

- When your agents filter a search-by-meaning request by a detail that isn't available, they now get a clear message listing the details you can filter on, instead of a confusing failure. Connector descriptions also list those filterable details up front, so agents pick valid ones the first time.

## August 20, 2026

Web app

- Links in chat messages are now readable in dark mode.
- Sortable column headings in tables now match the styling of the other headings instead of appearing in mixed case.

Connectors

- You can now search Twilio, Typeform, and incident.io by meaning. Your agents can find text message bodies, form questions and response answers, and incident names, alert descriptions, and incident updates without matching exact keywords.

Other

- When your agent searches your synced data using a field name that doesn't exist, it now gets the closest matching field names back so it can correct the search, instead of a generic failure.

## August 19, 2026

Web app

- Pinning chats no longer stops at 50. Every chat you pin now shows up in the pinned group in the sidebar and reads as pinned in the chat header. Pinning and unpinning also take effect immediately, without waiting for the list to refresh.

SDK

- Google Ads list methods no longer take a page size, because Google fixes each page of results at its own size and rejects the setting. To get the next page, pass the page token from the previous response along with the same query.

Connectors

- Google Ads queries now page through large result sets correctly, so your agents return complete results instead of stopping after the first page. The connector also documents that it only reads accounts your sign-in has direct access to. Agents no longer retry accounts that are reachable only through a manager account.

Other

- When your agents match customers or companies across your connected apps, they now know which fields they can actually query and start from email addresses before trying other identifiers. Expect fewer failed lookups and quicker answers.

## August 18, 2026

Web app

- Fixed an issue where long-running chat responses could be cut off before the agent finished answering.

SDK

- Searches against your synced data now filter out weakly related results by default, so agents get more relevant matches. You can adjust or turn off this minimum similarity cutoff when you need broader results.

## August 17, 2026

Web app

- When connector setup fails because of a configuration problem, such as a missing or invalid credential, the error now appears on the credentials page right away instead of only after repeated retry attempts.
- The custom plan on the plans page no longer shows a redundant "Custom" price above the "Talk to sales" button.

## August 13, 2026

Connectors

- You can now search Zendesk Support by meaning, including the text of ticket comments, so your agents can find relevant conversations without matching exact keywords. Each result carries details of the ticket it belongs to, such as the title, status, and priority, so your agents know which conversation a comment came from.

## August 12, 2026

Web app

- The sessions list now stays on screen while you change filters or move between pages. Results dim briefly while the new ones load instead of the table disappearing.
- Status labels for connectors and Context Store now stay on a single line and shorten with an ellipsis in narrow columns, so they're easier to read.

Other

- Your agents can now combine data from more than one connector in a single query against your synced data, so you can join related records, such as issues from one tool with calls from another, without running separate queries.
- Fixed an issue where a retried Context Store update could count already-completed data as failed, which could stop healthy data from staying searchable.

## August 11, 2026

Web app

- When your request to an agent is ambiguous, the chat now asks you a short clarifying question with a few options to choose from instead of guessing. You can pick an option, type your own answer, or skip the question and let the agent proceed with its best assumption, which it states in its reply.

## August 10, 2026

Web app

- Context Store status now warns you when your cached data is getting old, so you can tell at a glance whether your agents are searching fresh data or data that hasn't been updated in a while.
- When setting up a connector's cached data fails, the credentials page now tells you whether it's something you can fix yourself, such as a configuration or sign-in problem, and lets you edit the connector right away instead of showing a generic failure.
- Pages that check which features are available to your organization no longer stay stuck loading when that check is slow or unavailable. They now fall back to standard behavior and recover on their own.

SDK

- Downloading a document through a connector now returns readable text in manageable pages instead of one oversized response. Each page tells your agent how much text came back and whether more is available, so large files no longer overwhelm your agent.

Connectors

- You can now search GitHub by meaning, including issue descriptions, pull request descriptions, and comments, so your agents can find relevant discussions without matching exact keywords.

## August 7, 2026

Connectors

- Gmail is now available to connect. Your agents can read and organize mail, including messages, threads, drafts, and labels, and setup asks you to sign in with your Google account rather than choosing between sign-in methods.

## August 6, 2026

Web app

- Your connectors list and Context Store now tell you when a connector's latest data update failed. If it failed because your sign-in details are expired or no longer valid, the connector shows "Action Required" and you can select it to reconnect. Other failures show as "Failing," and your already-synced data stays searchable in the meantime.
- Filtering agent sessions by workspace now clears the connector filter at the same time, so you no longer see an empty list when the connector you had selected isn't used in the workspace you switched to.

## August 5, 2026

Other

- Your Context Store now stays on as long as your agents are using a connector for anything, not only searching it. Previously, a connector's Context Store could be turned off after a stretch without searches, even when your agents were still reading and writing data through that connector.

## August 4, 2026

Web app

- You can now pin the chats you come back to most. Pin or unpin a chat from the sessions table, the chat header, or the sidebar, filter the sessions list to show only pinned chats, and find your pinned chats grouped at the top of the sidebar. Pins are personal to you and stay with you across workspaces in your organization.
- New chat, MCP server, SDK, and CLI are now unavailable in the sidebar until you add a connector, and a tooltip points you to the connectors page. They become available as soon as you finish connecting an app.

Other

- Search results your agents get back from synced data now keep the field names you configured, so details that previously came back empty for some connected apps are included again.

## August 3, 2026

Web app

- Chat and session headers now show who started a chat when it was created by someone else on your team, so it's easier to tell at a glance whose work you're looking at.

## July 31, 2026

Other

- Fixed an issue where very large scanned PDF files could disrupt file indexing for search. Oversized documents are now skipped so your other files continue to be indexed normally.

## July 29, 2026

Web app

- Chat now stops as soon as an access policy blocks a connector action and tells you access was denied, instead of retrying the request or quietly moving on to other tools.
- When you review who can access a connector's data, the list of people now includes only those who can actually reach that workspace, so you no longer see teammates who could never use the connector.
- Chat and workflow building now run on Claude Opus 5.

Connectors

- LinkedIn Ads is now generally available instead of experimental. Your agents can work with ad accounts, campaigns, campaign groups, creatives, conversions, and lead forms, including creating, updating, and deleting campaigns and campaign groups, and can pull ad analytics broken down by device, company, company size, country, industry, job function, job title, region, and seniority. You can connect with either OAuth or a LinkedIn access token.
- Connector setup checks now send the default values some services require, so connections validate correctly for apps such as LinkedIn Ads and Salesforce.

## July 28, 2026

Web app

- Chat answers now display tables as real tables instead of raw text, and wide tables scroll sideways so you can read every column.
- The sessions list now shows who started each session in a new "Created by" column.
- Fixed an issue on the Team plan where the Members page failed to load for organizations that had a pending invitation.
- When a request fails for a reason that won't resolve on its own, such as something you don't have access to, the app now tells you right away instead of quietly retrying first.

Connectors

- You can now connect Google Analytics with a service account key, so you can set it up without signing in through Google and keep it running unattended.
- Connecting Slack no longer asks for access to group direct messages, so you grant fewer permissions when you authorize it.

## July 27, 2026

Web app

- Pages across the app, including your dashboard, billing, credentials, profile, sessions, and users, have a refreshed look with clearer page headers and summary cards.
- A connector's recent activity list now shows which page you're viewing, so it's easier to keep your place while you page through agent requests.
- Entities that are still being prepared for semantic search now show an indexing indicator, so you can tell the difference between an entity that isn't ready yet and one that doesn't support semantic search.
- People are now listed alphabetically when you review who can access an entity, so it's faster to find someone.

## July 24, 2026

MCP

- If you belong to more than one organization, the Airbyte Agent MCP can now list your organizations before you pick one to work in. Previously, multi-organization accounts hit an error when no organization was selected yet.

Other

- Semantic search now keeps up with edits to records you have already synced. Previously only newly added records were indexed for search, so later changes to an existing record were not reflected. Updated records are now re-indexed, so your agents search the current version of your data.
- Fixed an issue where asking an agent about data from a connector that was still finishing its initial setup could fail the entire request. Those queries now return no results until your data is ready, so the rest of the agent's work continues uninterrupted.

## July 21, 2026

Web app

- You can now watch a short tutorial video directly from the connectors page. Select "How this works" to see how connectors let your agents read and write data in the apps your team already uses.

SDK

- Connector reference documentation now describes semantic search, showing you which fields you can search by meaning and how to run a semantic query from the SDK, CLI, or API for connectors that support it.

Connectors

- You can now search Granola by meaning with semantic search, so your agents can surface the most relevant meeting notes from transcripts and summaries instead of matching exact keywords.

## July 20, 2026

Web app

- You can now open a connector to a dedicated detail page that brings together its entities, Context Store status, and recent agent request activity in one place. The connectors view also shows which entities your agents are allowed to access and how many times each entity has been read or written.

SDK

- A new `agent_tool` decorator lets you wire connector tools into agent frameworks the SDK doesn't natively support. You write your own execute, inspect, and docs functions, and the decorator steers the agent to inspect the connector and read its docs before running an action. Tool failures now raise a catchable `AirbyteToolError` you can handle in your own tool-dispatch loop.

## July 16, 2026

Web app

- Workspace options are now sorted alphabetically when you create an API key, making it easier to select the correct workspace.

SDK

- The Google Drive SDK now supports typed Context Store searches across file content. Downloads also apply the required media parameter automatically, so you no longer need to pass it yourself to retrieve file bytes.

Connectors

- You can now use semantic search across synced Google Drive files, including text extracted from PDFs, Word documents, spreadsheets, presentations, CSV files, and plain text files. Supported file downloads return readable text so your agent can use the contents directly.

Other

- Context Store now keeps the newest source version of a record when incremental syncs contain conflicting versions, preventing stale records from replacing fresher data in search results.

## July 15, 2026

MCP

- When you use the Airbyte Agent MCP, read-only SQL queries against your synced data no longer prompt for a write approval, so your agents can run those queries without an extra confirmation step.

Connectors

- The Sentry connector now lists your projects through Sentry's organization-scoped endpoint, replacing an endpoint Sentry has deprecated so that listing your projects keeps working reliably.

Other

- Fixed an issue that could prevent your connected data from staying current for agent search when records contained certain timestamp values. Updates now recover on their own so your search results stay fresh.

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
