# Review tool calls

Airbyte Agents logs every tool call your agents make. Review this log to understand what your agents are doing, troubleshoot failures, and investigate unexpected activity or cost spikes.

To review tool calls, click your profile icon and click **Tool Calls**.

## What are tool calls?

A tool call is a single action an agent takes against a connector. Each time an agent lists records, fetches a single record, searches the Context Store, or writes data back to a source, Airbyte records one tool call.

Airbyte classifies tool calls as one of the following types:

- **Direct**: A real-time request to a third-party API. Airbyte routes the call through the connector and returns the live response to the agent. Direct tool calls are useful for operational queries, real-time lookups, and actions that change state, like creating a ticket or sending a message.
- **Search**: A query against data Airbyte has already replicated into the Context Store. Airbyte answers the call from the cache without contacting the upstream API, which makes search tool calls fast and cost-efficient.

Tool calls are the billable unit that most directly reflects the work your agents do. Airbyte combines tool calls with token usage to calculate [agent operations (AOs)](../concepts/agent-operations.md). For billing details, see [Billing and pricing](./billing.md).

Tool calls can originate from any interface: Chat, Automations, the Automation Builder chat, MCP, the API, and the SDK. The Tool Calls page shows activity from all sources.

## How to interpret the table

The Tool Calls page has two sections: summary cards at the top and a Recent Tool Activity table below.

### Summary cards

The cards at the top of the page show rolled-up metrics for your organization:

- **Total Workspaces**: The number of active workspaces in your organization.
- **Total Credentials**: The number of connected data source credentials across all workspaces.
- **Context Store Activity**: The number of successful Context Store retrievals in the last 30 days.

### Recent Tool Activity table

The Recent Tool Activity table shows individual tool calls in reverse chronological order, with the most recent call at the top. Each row represents one tool call.

#### Live View

The **Live View** toggle controls whether the table refreshes automatically. When Live View is on, Airbyte polls for new activity every 10 seconds and refreshes the summary cards every 30 seconds. Turn Live View off to pause updates while you investigate a specific entry.

#### Filters

Use the filters above the table to narrow the activity to a specific subset:

- **Workspace**: Show tool calls from a single workspace, or show all workspaces.
- **Tool Type**: Show only Direct tool calls, only Search tool calls, or both.
- **Status**: Show only successful calls, only failed calls, or both.

#### Columns

Each row in the table includes the following information:

- **Tool Type**: A badge that identifies the call as **Direct** or **Search**. Search calls that Airbyte served from the Context Store also show a **Context Store** badge.
- **Entity**: The resource the agent acted on, such as `contacts` or `orders`. This matches the stream name exposed by the connector.
- **Action**: The operation the agent performed, such as `list`, `get`, `search`, or `create`.
- **Workspace**: The workspace the tool call belongs to. Click the workspace name to view that workspace's credentials.
- **Connector**: The connector the agent used, such as HubSpot or Stripe.
- **Timestamp**: The date and time Airbyte recorded the call.
- **Status**: A green check mark for successful calls, or a red X for failed calls. Use the Status filter to focus on failures when you're troubleshooting.

If the table is empty, your agents haven't made any tool calls yet, or your filters exclude every call in the window. Clear your filters to confirm.
