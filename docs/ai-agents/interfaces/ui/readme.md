---
sidebar_position: 1
---

# Web app

The Airbyte Agents web app at [app.airbyte.ai](https://app.airbyte.ai) is the fastest way to use Airbyte Agents without writing code. Describe what you want in natural language, and Airbyte picks the right connectors, makes the necessary tool calls, and replies with an answer grounded in your data.

Use the web app when you want Airbyte itself to be your agent. For Python agents you build yourself, use the [SDK](../sdk). For agents in any other language, use the [API](../api). For agents that already speak Model Context Protocol, use the [MCP server](../mcp).

## Chats and Automations

The web app has two primary surfaces for working with an Airbyte agent.

- [**Chats**](./chats): Interactive conversations with an Airbyte agent. Ask a question, iterate on the answer, and explore your data in natural language. Chats are the fastest way to get a one-off answer or prototype an idea.
- [**Automations**](./automations): Agent tasks that run without a person in the loop. Trigger an Automation manually, on a schedule, or from a webhook. Use Automations when you need the same work to happen repeatedly and reliably.

Every Chat and Automation runs against the connectors you've authenticated in your workspace. Manage connectors from the **Credentials** page in the sidebar. For the catalog of available connectors, see [Agent connectors](../../connectors).

## Set up connectors and context

Administrators can add connectors and configure the Context Store from the web app.

- [**Add a connector**](./add-connector): Authenticate data sources so agents in Chats, Automations, and every other interface can use them.
- [**Context Store**](../../concepts/context-store): Configure the searchable replica of select entities from your connected data sources that powers grounded answers and large-scale analytics.

## Related administration

Other parts of the web app are covered in [Account and administration](../../admin):

- [Profile](../../admin/profile) for account settings.
- [Sessions](../../admin/sessions) for the run history of every Chat and Automation in your organization.
- [Review tool calls](../../admin/tool-calls) for inspecting and approving deferred tool calls.
- [Billing](../../admin/billing) for plans, usage, and invoices.

import DocCardList from '@theme/DocCardList';

<DocCardList />
