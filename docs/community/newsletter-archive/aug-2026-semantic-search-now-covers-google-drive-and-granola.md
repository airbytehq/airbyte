---
sidebar_label: "Aug 2026: Semantic search now covers Google Drive and Granola"
---
# Semantic search now covers Google Drive and Granola

_Published August 18, 2026._

![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/aug-2026-semantic-search-now-covers-google-drive-and-granola/01m09dw5zx59ebf0x51y52cmye-4433b267d1.png)

Welcome to the Airbyte August 2026 newsletter. Two things led the month: the release of Airbyte 2.2, and semantic search availability in Google Drive and Granola.

We're also exploring new ways to make Airbyte data replication easier to use from AI agents with a CLI and MCP server. Your feedback can help shape what we build. [Take our quick survey →](https://forms.gle/LD7VsZcsJPBo3F2AA)

Here are the latest updates for the platform:

- Semantic Search for Google Drive and Granola
- Entity policies for agent connectors
- New Agent Connectors: HubSpot and LinkedIn Ads
- Sovereignty Starts Below the Model
- Airbyte 2.2 is Here
- Move from Airbyte OSS to Cloud Without Missing a Sync
- Two New Tutorials for Your Perusal

[![Airbyte's agentic platform](https://airbyte.com/images/community/newsletter/bodies/external/aug-2026-semantic-search-now-covers-google-drive-and-granola/01kv6gxvvfsd8kabpge800ktz4-33b3d55743.png)](https://cloud.airbyte.com/signup)

## Semantic search now covers Google Drive and Granola

Point your agents at the unstructured data in Google Drive and Granola meeting notes, then ask questions based on ideas instead of keywords. Semantic search unlocks hidden relationships between files to offer more robust answers to queries accessible from the Context Store. The Context Store extracts the text, splits it into passages, embeds them, and returns the passages that match your query for more targeted answers. Drive and Granola join Gong and Linear, so an agent can tie a decision from a meeting note back to the impacted record.

[Read the blog →](https://airbyte.com/blog/semantic-search-google-drive-and-granola)

## Entity policies: one connector, precise access

Set read and write access per user, per entity, and per action on a single connector. A revenue lead can edit sales data while an SDR only reads it, with no cloned connectors and no shared, over-scoped credentials. It takes about a minute to set up in the Airbyte UI.

[See how it works →](https://airbyte.com/blog/entity-policies-for-airbyte-agents)

## New agent connectors: HubSpot and LinkedIn Ads

Two of the connectors you asked for most are now available through Airbyte MCP and agent connectors. HubSpot agents can create and update contacts, companies, deals, tickets, and engagement objects to help you track relationships. In LinkedIn Ads, campaigns, groups, and creatives are writable, so an agent can pause or adjust budget on a weak campaign in near real time. Both work through the Agents app, Agent MCP, SDK, CLI, and API.

[See the connectors →](https://airbyte.com/blog/hubspot-linkedin-ads-agent-connectors)

## Sovereignty starts below the model

CEO Michel weighs in on how to manage your AI by owning the governed data layer underneath it. Without lineage and access control at that layer, you don't know what your agents touched or where your boundary sits, and no set of weights can fix stale, scattered context. Build the data layer first, then swap models whenever you want.

[Read the argument →](https://airbyte.com/blog/ai-sovereignty)

[![Airbyte Data Replication](https://airbyte.com/images/community/newsletter/bodies/external/aug-2026-semantic-search-now-covers-google-drive-and-granola/01kv6j60tqxzshpp0t0q7s6cjn-daa17e4350.png)](https://cloud.airbyte.com/signup)

## Airbyte 2.2 is here

Airbyte 2.2 OSS shipped on August 10. Syncs that produce zero records now finish successfully instead of erroring, and OAuth credential refreshes persist right away. The Helm chart adds namespace overrides, more storage options for PostgreSQL and MinIO, and separate resource sizing for orchestrators and jobs. Job-history queries run faster on a new index, and destination containers get a 60-second graceful shutdown.

One thing to plan for: upgrading from 2.1.x is irreversible, so back up your database first. The migration drops tables that 2.1.x depends on.

[Read the 2.2 release notes →](https://docs.airbyte.com/release_notes/self-managed/v-2.2)

## Move from Airbyte OSS to Cloud without missing a sync

Thinking about moving to Airbyte Cloud but found the process too difficult? We now offer a streamlined migration for your workspace, connections, and sync state, so your first Cloud sync resumes from the same cursor your last OSS sync used. A five-stage cutover keeps connections off until you approve, so two instances never write the same connection into the same destination. Contact your Airbyte representative to get started.

[Read the migration guide →](https://airbyte.com/blog/airbyte-oss-to-cloud)

[![Airbyte Tutorials](https://airbyte.com/images/community/newsletter/bodies/external/aug-2026-semantic-search-now-covers-google-drive-and-granola/01kxkdtn62hc042pyakqgb7h9n-cccb873fdc.png)](https://airbyte.com/tutorials)

## Connect your Claude Agent SDK agent to Airbyte

Build a bug-triage agent that reads new GitHub issues, checks Linear for duplicates, groups them by severity, and posts a summary to Slack. The walkthrough pairs the Claude Agent SDK with the Airbyte Agent SDK and wraps Airbyte connector calls as Claude tools, an in-process MCP server. Runnable code the whole way through.

[Scope the tutorial →](https://airbyte.com/tutorials/connect-claude-agent-sdk-agent-to-airbyte)

## Connect your OpenAI Agents SDK agent to Airbyte

In this build, a Deal Digest agent pulls your latest Salesforce opportunities and drops a written recap into a Slack channel. The new `build_connector_tools()` call streamlines the agent's discovery process. And of course the Context Store handles the pagination and rate limits, so the agent makes 40% fewer API calls and burns up to 80% fewer tokens than hitting the source APIs directly.

[See how it runs →](https://airbyte.com/tutorials/openai-agents-sdk-agent-access-to-salesforce-and-slack)

_That's it for August!_

Thanks for reading. Follow along on the social links below to keep up with what's new in Airbyte.

[![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/aug-2026-semantic-search-now-covers-google-drive-and-granola/01kqtaxn01pxwaf1qhx06apcjw-995766ab9e.png)](https://airbyte.com/)
