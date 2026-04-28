---
sidebar_position: 1
---

# Agent operations

An agent operation (AO) is the unit of work in Airbyte Agents. Every time an agent processes a prompt, reasons about data, or calls a tool, it consumes AOs. AOs measure the processing intensity of a task, not just the number of requests.

Airbyte derives AOs from a combination of two factors:

- **Tool calls.** Each action an agent takes against a connector counts as a tool call. Listing records, fetching a single record, searching the Context Store, and writing data back to a source are all tool calls.
- **Token usage.** The input and output tokens an agent consumes while reasoning about your prompt contribute to the AO count.

Simple tasks typically make fewer tool calls and use fewer tokens, so they consume fewer AOs. Complex reasoning tasks that span multiple connectors, require iterative lookups, or produce long responses consume more.

## What produces agent operations

Any interaction with an agent consumes AOs. The source of the interaction determines how Airbyte tracks it.

| Source | Description | Tracked as a session? |
| --- | --- | --- |
| **Chat** | A conversation with an agent in the web app. | Yes |
| **Automation** | A single run of a scheduled, webhook-triggered, or manually triggered automation. | Yes |
| **Automation Builder Chat** | A conversation inside the Automation Builder while designing an automation. | Yes |
| **MCP** | Tool calls from agents connected through the Model Context Protocol. | No |
| **API** | Direct calls to the Airbyte Agents API. | No |
| **SDK** | Calls from an agent built with the Airbyte Agents SDK. | No |

Sources tracked as sessions appear on the [Sessions](../admin/sessions.md) page, where you can review the full conversation and tool calls. Sources that aren't tracked as sessions still consume AOs and appear in the [Usage panel](../admin/billing.md#monitor-usage) on the Billing page.

## How AOs relate to billing

Your plan determines how many AOs you receive each month, whether you can exceed that allowance, and how much overage costs. For plan details, usage monitoring, and payment management, see [Billing and pricing](../admin/billing.md).

## Related topics

- [Billing and pricing](../admin/billing.md) -- Plan allowances, overage, invoices, and usage monitoring.
- [Review sessions](../admin/sessions.md) -- Audit what your agents did and how many AOs each session consumed.
- [Review tool calls](../admin/tool-calls.md) -- Inspect individual tool calls across all sources.
