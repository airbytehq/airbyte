---
sidebar_label: "Jun 2026: Team workspaces for agentic data"
---
# Team workspaces for agentic data

_Published June 17, 2026. [View on airbyte.com](https://airbyte.com/community/newsletter/jun-2026-airbyte-agents-now-supports-teams)._

![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/jun-2026-airbyte-agents-now-supports-teams/01kv6gnm669a5bdwcy9b4r01r6-aed9de910b.png)

Welcome to the Airbyte June 2026 Newsletter! We're going over our latest product updates for agentic data and Data Replication. The highlights include:

- Teams in workspaces for agentic data
- The Airbyte Agent CLI
- Write Capabilities for Salesforce Agent Connector
- 4x Faster Redshift Syncs
- Forrester Identifies 239% ROI from Airbyte
- New MotherDuck Destination

## Team workspaces for agentic data

[![Airbyte's agentic platform](https://airbyte.com/images/community/newsletter/bodies/external/jun-2026-airbyte-agents-now-supports-teams/01kv6gxvvfsd8kabpge800ktz4-33b3d55743.png)](https://cloud.airbyte.com/signup)

Upgrade to the Team plan to invite your teammates into your organization. Each member gets their own private workspace, visible only to them and admins, plus access to shared workspaces for collaborative work. The Team plan also unlocks parallel workflow execution and 10,000 Agent Operations per month.

[Upgrade to the Teams plan →](https://cloud.airbyte.com/signup)

## The Agent CLI is here

A single binary that brings Airbyte's agentic platform to your terminal. Run it from a shell, script, or CI job. List connectors, inspect schemas, and execute reads, searches, creates, and updates across your systems. Commands take JSON in and return JSON out, so it drops straight into existing automation. And with schema discovery, your agent can learn a command's structure before calling it.

Install it with one command:

```text
curl -fsSL https://airbyte.ai/install.sh | bash
```

[Read the launch blog →](https://airbyte.com/blog/airbyte-agent-cli) · [Deep dive with Cam Kennedy →](https://airbyte.com/blog/airbyte-cli-deep-dive)

## Write to Salesforce

The Salesforce Agent Connector now supports write operations. Your agents can update records, not just read them. Read-only agents can only describe work. Agents that can write can actually do work.

[Try it now →](https://cloud.airbyte.com/signup)

## One MCP gateway to rule them all

Most MCP gateways are just shells over a collection of inconsistent servers. We wrote about what a gateway actually needs to work in production, and how the Airbyte Agent MCP powered by the Context Store is the solution.

[Read the blog →](https://airbyte.com/blog/mcp-gateway)

[![Airbyte Data Replication](https://airbyte.com/images/community/newsletter/bodies/external/jun-2026-airbyte-agents-now-supports-teams/01kv6j60tqxzshpp0t0q7s6cjn-daa17e4350.png)](https://cloud.airbyte.com/signup)

## Redshift syncs, up to 4x faster

Destination Redshift 4.0 ships three upgrades in one release: Speed Mode, Direct Loading, and a full migration to the Bulk CDK. Together they deliver up to a 4.6x throughput increase. Direct Loading also eliminates raw tables and the transformation SQL that ran in your warehouse on every sync, with projected compute savings of 50 to 70% depending on workload. No configuration changes required to upgrade.

[Deep dive with Sunil Kuruba →](https://airbyte.com/blog/redshift-4)

## Forrester measured the ROI of Airbyte: 239%

We commissioned Forrester to study what Airbyte Data Replication actually delivers. The Total Economic Impact study found a **239% ROI, $1.1M in net present value**, and payback in under six months. Behind those numbers: pipelines built 60% faster, 40% less time spent on maintenance, and one customer cutting a month of coding effort down to two days.

[Read the blog →](https://airbyte.com/blog/forrester-tei-report) · [Or the full study →](https://tei.forrester.com/go/Airbyte/DataMovementPlatform/?lang=en-us)

## MotherDuck is now a certified destination

The MotherDuck destination connector is officially certified: maintained by Airbyte engineers, tested, and production ready. Sync any of 700+ sources into the serverless data warehouse built on DuckDB, with typed, deduplicated tables out of the box.

[Read the post →](https://airbyte.com/blog/motherduck-certified-destination)

_That's it for June!_

Thanks for reading, and follow us with the handy social media links below to stay up to date with the latest features in Airbyte.

[![Airbyte](https://airbyte.com/images/community/newsletter/bodies/external/jun-2026-airbyte-agents-now-supports-teams/01kqtaxn01pxwaf1qhx06apcjw-995766ab9e.png)](https://airbyte.com/)
