---
plan: all
sidebar_position: 1
---

# Agent operations

An Agent Operation (AO) is the unit of work in Airbyte Agents. AOs measure the processing intensity of a task, not just the number of requests.

Airbyte derives AOs from one or both of these factors, depending on where the work starts:

- **Tool calls.** Each action an agent takes against a connector counts as a tool call. Listing records, fetching a single record, searching the Context Store, and writing data back to a source are all tool calls.
- **Reasoning.** When you use an Airbyte-managed agent, the input and output tokens the agent consumes while reasoning about your prompt also contribute to the AO count.

Chat is an Airbyte-managed agent, so it can consume AOs for both tool calls and reasoning. If you bring your own agent through the MCP, the API, the SDK, or the CLI, Airbyte doesn't charge for your agent's reasoning. Those surfaces consume AOs for tool calls only. Connector calls made locally through the open source SDK don't consume AOs.

Simple tasks typically make fewer tool calls and require less reasoning, so they consume fewer AOs on managed-agent surfaces. Complex tasks that span multiple connectors, require iterative searches, or produce long responses consume more.

Airbyte doesn't publish the exact formula that converts tool calls and reasoning into AOs. One AO doesn't necessarily equal one tool call, and Airbyte doesn't publish fixed AO ratios for reads, writes, searches, or token usage. Use the [Usage chart](../admin/billing.md#monitor-usage) on the Billing page to monitor your consumption.

## What produces agent operations

Any interaction that uses Airbyte-hosted execution can consume AOs. The source determines whether Airbyte includes reasoning in the AO calculation and how Airbyte tracks the work.

| Source   | Description                                                          | What contributes to AOs  | Tracked as a session? | Tool calls visible? |
| -------- | -------------------------------------------------------------------- | ------------------------ | --------------------- | ------------------- |
| **Chat** | A conversation with an agent in the web app.                         | Tool calls and reasoning | Yes                   | Yes                 |
| **MCP**  | Tool calls from agents connected through the Model Context Protocol. | Tool calls only          | No                    | Yes                 |
| **API**  | Direct calls to the Agent API.                                       | Tool calls only          | No                    | Yes                 |
| **SDK**  | Calls from an agent built with the Agent SDK.                        | Tool calls only          | No                    | Yes                 |
| **CLI**  | Connector actions run through the `airbyte-agent` command line.      | Tool calls only          | No                    | Yes                 |

Sources tracked as sessions appear on the [Sessions](../admin/sessions.md) page, where you can review the full conversation, reasoning token usage, and tool calls. Sources that aren't tracked as sessions can still consume AOs for tool calls and appear in the [Usage panel](../admin/billing.md#monitor-usage) on the Billing page. To inspect individual tool calls from the MCP, API, SDK, or CLI usage, use the [Tool calls](../admin/tool-calls.md) page.

## How AOs relate to billing

Your plan determines how many AOs you receive each month, whether you can exceed that allowance, and how much overage costs. For plan details, usage monitoring, and payment management, see [Billing and pricing](../admin/billing.md).

## Related topics

- [Billing and pricing](../admin/billing.md) -- Plan allowances, overage, invoices, and usage monitoring.
- [Review sessions](../admin/sessions.md) -- Audit what your agents did and how many AOs each session consumed.
- [Review tool calls](../admin/tool-calls.md) -- Inspect individual tool calls across all sources.
