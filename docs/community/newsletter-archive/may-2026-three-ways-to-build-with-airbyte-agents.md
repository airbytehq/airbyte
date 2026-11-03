---
sidebar_label: "May 2026: Airbyte's agentic platform: A New Era for Airbyte"
---
# Airbyte's agentic platform: A New Era for Airbyte

_Published May 5, 2026. [View on airbyte.com](https://airbyte.com/community/newsletter/may-2026-three-ways-to-build-with-airbyte-agents)._

[![Airbyte's agentic platform](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqt946qh2ad8c9x6xcez46zj-a8f0d2e32d.jpg)](https://airbyte.com/blog/airbyte-agents)

Today we're launching our agentic data platform. It's the biggest step we've taken as a company since we open-sourced our first connector six years ago.

We want to explain why we built this product, and why we think it's important.

## The problem

As agents move into real workflows, they need access to more tools. That means going through a lot of API plumbing: authentication, pagination, filters, schema, and matching entities across systems.

Simply put, APIs are built for pre-determined workflows that assume you know what you want to query: think specific endpoints, object IDs, and exact fields.

Agents often start one step earlier. They need to discover what data actually matters before they can start reasoning. This is where most of the existing architectures break.

## The solution

Airbyte fixes the context layer underneath. The foundation is a piece of infra we call the [Context Store](https://docs.airbyte.com/ai-agents/concepts/context-store). A data index optimized for agentic search, that gives agents a structured way to discover the right records, while still allowing them to read and write directly to upstream systems when needed.

## The results

In early benchmarks, calling the Context Store consumed up to 80% fewer tokens and made 40% fewer tool calls compared to querying vendor MCPs and APIs directly.

What does this mean? Lower token usage, fewer rate limits, and more accurate outputs from cleaner context, all while saving money in the process.

[Read the full launch story from Airbyte CEO Michel Tricot →](https://airbyte.com/blog/airbyte-agents)

[![Watch the launch video](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqtbv56mba35jchsgzzqcegf-d405a0b686.png)](https://www.youtube.com/watch?v=xvzIUNRISUg)

[Watch the launch video](https://www.youtube.com/watch?v=xvzIUNRISUg)

## Three ways to build with agentic data

[![Three ways to build with agentic data](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqt9z4s37x7qbf629nhph9gv-4a815851d3.png)](https://airbyte.com/blog/airbyte-agents)

**🔌 The Airbyte Agent MCP** — One connection that gives your agent access to all your business systems through the Context Store and direct API calls. Install it in Claude, ChatGPT, Cursor, or any MCP-compatible client. Connect your sources with OAuth. No code required.

[Read the MCP deep dive →](https://airbyte.com/blog/agent-mcp) · [Setup docs →](https://docs.airbyte.com/ai-agents/interfaces/mcp/)

**🛠️ The Agent SDK** — A Python library for teams building production agents. Works alongside Claude Agent SDK, OpenAI Agents SDK, PydanticAI, LangChain, FastMCP, or your own Python loop. Reads from the Context Store for discovery, writes to live systems with a full audit trail.

[Read the SDK deep dive →](https://airbyte.com/blog/agent-sdk) · [SDK docs →](https://docs.airbyte.com/ai-agents/interfaces/sdk/)

**⚡ Automations** _(Research Preview)_ — A visual interface for building and running agents directly inside Airbyte. Designed for teams that want to ship agents without the infra overhead.

[Explore Automations →](https://docs.airbyte.com/ai-agents/interfaces/ui/automations)

## What early users are saying

![What early users are saying](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqta70yq4gf11zj3ecx5nqwp-2fe50df3c5.png)

"Airbyte has massively accelerated our roadmap. What we thought would take 6 plus months, we were testing in the first week of the beta program." — **Nate Chambers**, Chief Product Officer, ORCA Analytics

"Without Airbyte, we'd be stitching together bespoke connectors for every integration, which would slow us down dramatically. With Airbyte, our AI features have fresh, reliable data to work with." — **Franziska Ibscher**, Head of Product, Drivepoint

## Pricing and getting started

[![Get started](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqtah9s67my7wndwvfteh39x-bdc98186a9.png)](https://cloud.airbyte.com/signup)

Airbyte's agentic platform has a generous [Free plan](https://airbyte.com/pricing) so you can start building today. Paid plans with higher limits are available when you need to scale.

The product is early, and we think that's okay. We know the best way to build a great product is to develop it with our users.

P.S. If you already have an existing Airbyte account, your credentials should work just fine!

[Get started →](https://cloud.airbyte.com/signup)

## Airbyte Core 2.1 release notes

[![Airbyte Core 2.1 release notes](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqtasc61cxxde54q0sf842ka-4492d06519.png)](https://docs.airbyte.com/release_notes/self-managed/v-2.1)

For those running Airbyte Core, version 2.1 shipped on April 3rd. A few highlights:

- **Helm chart V1 is no longer supported.** Migrate to V2 before upgrading. [Migration guide →](https://docs.airbyte.com/platform/deploying-airbyte/chart-v2-community)
- **Authentication enabled by default** on new deployments, with configurable Ingress in values.yaml.
- **15-minute and 30-minute sync frequencies** now available for sub-hourly scheduling.
- **Async schema discovery** so the UI no longer blocks during large schema fetches.
- **Connector JVM OOM handling** so connectors now exit cleanly instead of hanging, with new failure metrics.

Note: 2.1 is labeled experimental as we've changed how versions are assembled. If stability is your primary concern, you may want to wait for the next patch.

[Full release notes →](https://docs.airbyte.com/release_notes/self-managed/v-2.1)

[![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/may-2026-three-ways-to-build-with-airbyte-agents/01kqtaxn01pxwaf1qhx06apcjw-995766ab9e.png)](https://airbyte.com/)
