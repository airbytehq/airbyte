---
sidebar_label: "Feb 2026: Airbyte agentic data platform is now in public beta"
---
# Airbyte agentic data platform is now in public beta

_Published February 26, 2026. [View on airbyte.com](https://airbyte.com/community/newsletter/feb-2026-context-store)._

![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/feb-2026-context-store/header-thumbnail-3x-1-optimized-feb-19-2026-4-33-36-pm-01khw7erw7mctcskgsxhb0ns41-446b847619.png)

2026 is zipping along, and we're shipping faster than ever!

In December, we released agent connectors, open source Python SDKs purpose-built to give AI agents consistent, real-time access to operational data for context-rich decision making.

The [Airbyte agentic data platform](https://airbyte.com/blog/agent-engine-public-beta) builds on these connectors to give your agents a unified interface to external data sources. This is done via tool calls with configured parameters for unprecedented control. The agentic data platform includes a fully-managed authentication module supporting OAuth, hosted agent connectors, and the Context Store.

[![Airbyte agentic data platform public beta](https://airbyte.com/images/community/newsletter/bodies/external/feb-2026-context-store/public-beta-optimized-feb-19-2026-2-21-12-pm-01khvzwbkdnpe2tfm3h91swn74-93dd74844f.png)](https://airbyte.com/ai)

[Try it now →](https://airbyte.com/ai)

## Context Store

The Context Store captures a subset of relevant data from connected sources in Airbyte-managed object storage, enabling your agents to perform efficient search operations without repeatedly querying vendor APIs. This is a feature built on our tried and true replication technology, which no other solution provides.

This ensures that your agent only requests data from external systems when absolutely necessary, optimizing processes for compute and latency.

We're entering public beta with 20+ agent connectors today, including HubSpot, Salesforce, Gong, Linear, GitHub, and more, with hundreds more coming fast from Airbyte's native ecosystem of 700+ data connectors.

[Try it now.](https://airbyte.com/ai)

## Airbyte Joins the Agentic AI Foundation

[![Airbyte Joins the Agentic AI Foundation](https://airbyte.com/images/community/newsletter/bodies/external/feb-2026-context-store/696f7d97a41b362d37a97e3c-unnamed-13-4342b5d4f2.png)](https://airbyte.com/blog/airbyte-joins-agentic-ai-foundation)

The Agentic AI Foundation brings together the people building the core protocols that agentic systems will run on such as MCP (Model Context Protocol), AGENTS.md, and goose. These aren't proprietary standards locked behind corporate walls. They're open, transparent, and community-driven.

This aligns perfectly with how we've always operated at Airbyte. We started as an open source project because we believed data movement should be accessible, not locked behind expensive enterprise contracts.

We look forward to partnering with companies who share our commitment to building the future of agentic AI.

[Read our CEO Michel Tricot's full announcement.](https://airbyte.com/blog/airbyte-joins-agentic-ai-foundation)

## Airbyte Knowledge MCP Server

[![Airbyte Knowledge MCP Server](https://airbyte.com/images/community/newsletter/bodies/external/feb-2026-context-store/697796bdba033cff0da87fe6-unnamed-16-b9c29a161d.png)](https://airbyte.com/blog/knowledge-mcp-server)

We're launching a public MCP server that gives AI agents direct access to Airbyte's complete knowledge base. This includes our documentation, API specifications, GitHub issues/PRs, YouTube content, and community discussions.

This gives agents reliable, up-to-date information about how Airbyte works rather than relying on potentially outdated training data. [Read more.](https://airbyte.com/blog/knowledge-mcp-server)

## Engineering Spotlight: Building OAuth Flows with MCP Apps

[![Building OAuth Flows with MCP Apps](https://airbyte.com/images/community/newsletter/bodies/external/feb-2026-context-store/oauth-blog-01khw08h4txyfzcm3fpp7gvrfx-c177f267e7.png)](https://airbyte.com/blog/building-oauth-flows)

[MCP Apps](https://modelcontextprotocol.io/docs/extensions/apps) are a newly released extension to the Model Context Protocol that lets MCP tools return interactive HTML interfaces instead of plain text. MCP Apps enable interactive UIs directly in agentic chat, rendering directly in the conversation within Claude, ChatGPT, and other MCP clients. The value: users can interact with complex interfaces without leaving the chat context.

We wanted to test this capability at scale, so we built OAuth flows for [Airbyte's agent connectors](https://github.com/airbytehq/airbyte-agent-connectors) (Asana, HubSpot, Slack, and more). This resulted in production-ready connectors with OAuth flows that work entirely within Claude.

Check out the process [here](https://airbyte.com/blog/building-oauth-flows).
