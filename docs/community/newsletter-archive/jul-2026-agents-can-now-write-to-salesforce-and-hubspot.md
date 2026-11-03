---
sidebar_label: "Jul 2026: Agents can now write to Salesforce and HubSpot"
---
# Agents can now write to Salesforce and HubSpot

_Published July 16, 2026. [View on airbyte.com](https://airbyte.com/community/newsletter/jul-2026-agents-can-now-write-to-salesforce-and-hubspot)._

![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/jul-2026-agents-can-now-write-to-salesforce-and-hubspot/01kxkea50g45v08r924e781ga3-4f9acdf09d.png)

This month, agents got more ways to act on your data, not just read it. Write operations landed in the Salesforce and HubSpot connectors, semantic search arrived for Gong and Linear, workspaces came to Airbyte's agentic platform, and Direct Loading rolled out across every certified destination.

Here's what we have to share today:

- Salesforce and HubSpot Write Capabilities
- Semantic Search for Gong and Linear
- Workspaces for agentic data
- Direct Loading for All Certified Destinations
- New Tutorials using LangChain and Claude

## Agents can now write to Salesforce and HubSpot

[![Airbyte's agentic platform](https://airbyte.com/images/community/newsletter/bodies/external/jul-2026-agents-can-now-write-to-salesforce-and-hubspot/01kv6gxvvfsd8kabpge800ktz4-33b3d55743.png)](https://cloud.airbyte.com/signup)

The Salesforce and HubSpot Agent Connectors now ship with write operations. Your agents can create and update contacts, companies, deals, and tickets in HubSpot, and move opportunities through pipeline stages in Salesforce, all through the same interfaces: MCP, Python SDK, API, and Agent CLI.

[Learn how it works →](https://airbyte.com/blog/salesforce-hubspot-write-capabilities)

## Semantic search for Gong and Linear

Semantic search in the Context Store now covers Gong call transcripts and Linear issue descriptions and comments: ask by meaning, and the agent finds the relevant passages, ranks them, and returns the surrounding context so you know who said what and when. Everything runs through the Context Store, where open-source benchmarks show agents querying Gong use up to 80% fewer tokens than the native API (up to 75% for Linear).

[Read the blog →](https://airbyte.com/blog/semantic-search-for-gong-and-linear)

## Workspaces now available for agentic data

Organize your agent context by team, project, or person. Each workspace gets its own connections and its own slice of the Context Store, so your sales team's agent and your personal agent don't share context unless you want them to. Grant access to any workspace at any time. Agents working across multiple workspaces query each one independently and combine the results. Workspaces are available on the Team plan, along with SSO and multiple users.

[Learn more →](https://airbyte.com/blog/airbyte-agents-workspaces)

[![Airbyte Data Replication](https://airbyte.com/images/community/newsletter/bodies/external/jul-2026-agents-can-now-write-to-salesforce-and-hubspot/01kv6j60tqxzshpp0t0q7s6cjn-daa17e4350.png)](https://cloud.airbyte.com/signup)

## Direct Loading now available for all certified destinations

Direct Loading writes data straight to your destination without intermediate staging, cutting sync times and compute costs. It started with a handful of destinations; as of this month it covers every certified destination in the catalog.

[The full breakdown →](https://airbyte.com/blog/direct-loading-on-certified-destinations)

[![Airbyte Tutorials](https://airbyte.com/images/community/newsletter/bodies/external/jul-2026-agents-can-now-write-to-salesforce-and-hubspot/01kxkdtn62hc042pyakqgb7h9n-cccb873fdc.png)](https://airbyte.com/tutorials)

## Reduce token use and response time in your LangChain agent

Most agents burn tokens on discovery: listing resources, paging through results, retrying after rate limits. This tutorial wires a Slack connector to a LangChain agent through the Context Store, with working code. Benchmarks show 40% fewer tool calls and up to 80% fewer tokens.

[Scope the tutorial →](https://airbyte.com/tutorials/reduce-token-usage-on-langchain-agents)

## Fight Stripe disputes with an installable Claude skill

Our Controller was spending 45 minutes per dispute pulling evidence from Stripe, Zendesk, Orb, Slack, and Google Drive. She built an Airbyte agent automation that took contested disputes from under 10% to over 90%, and we packaged it as a Claude skill you can install and run on your own stack. The agent provides the documents for you to review and submit; it will never submit on your behalf.

[Start winning now →](https://airbyte.com/tutorials/fighting-stripe-disputes-with-airbyte-agents)

_That's it for July!_

Thanks for reading, and follow us with the handy social media links below to stay up to date with the latest features in Airbyte.

[![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/jul-2026-agents-can-now-write-to-salesforce-and-hubspot/01kqtaxn01pxwaf1qhx06apcjw-995766ab9e.png)](https://airbyte.com/)
