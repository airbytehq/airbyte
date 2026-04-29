# Review sessions

The Sessions page shows a read-only history of every agent interaction in your workspace, along with token usage and the tools each interaction used. Use it to audit what your agents did, troubleshoot unexpected results, and understand what's driving your [agent operations (AOs)](../concepts/agent-operations.md).

## What sessions are

A session is a single agent run, from the moment an agent starts working to the moment it finishes. Each session captures:

- The prompt or trigger that started the run.
- The messages exchanged between you and the agent, if any.
- The tool calls the agent made to answer the prompt, including the connector each tool call targeted.
- The input and output tokens the agent consumed.
- The resulting AOs charged to your plan.

Airbyte logs sessions for work initiated in the web app. Work initiated through [MCP](../interfaces/mcp/readme.md), the [API](../reference/api/readme.md), or the [SDK](../interfaces/sdk/readme.md) is billed by tool call but isn't logged as a session. See [Session types](#session-types) for details.

## How to understand the Sessions table

The Sessions table lists the most recent sessions first. Each row represents one session, and the columns describe what the agent did and how much work it took.

- **Source**: A descriptive name for the session. For automations, this is the automation's name. For chats, this is the chat's title.
- **Type**: Whether the session is a [Chat](#chat) or an [Automation](#automation). Automation Builder Chats appear under **Chat**.
- **Tools**: The connectors the agent used during the session. Hover over a connector icon to see its name.
- **Messages**: The number of messages exchanged in the session. Automation sessions typically have fewer messages than chat sessions, since they don't involve a back-and-forth with a user.
- **Input Tokens**: The total tokens the agent received as input, across every turn in the session.
- **Output Tokens**: The total tokens the agent produced, across every turn in the session.
- **Tool Calls**: The number of tool calls the agent made during the session. Drill into [tool calls](./tool-calls.md) to see individual calls.
- **Date**: When the session last updated. Sessions that are still running show the most recent activity time. Dates display in your browser's local [time zone](../concepts/time-zones).
- **Actions**: Per-row buttons to review or resume the session.
    - Click the **View** icon to open the session and see its messages and tool calls.
    - Click the **Open** icon to jump to the chat or automation the session belongs to.

Use the **Type** and **Tools** filters above the table to narrow the list. The Type filter scopes to chats or automations. The Tools filter scopes to sessions that used one or more specific connectors.

## Session types {#session-types}

Airbyte counts three kinds of work as sessions. Each is billed as AOs against your plan.

### Chat {#chat}

A Chat session is a conversation you have with an agent in the web app. You send prompts, the agent responds, and the agent may call tools to answer you. Chat sessions continue until you stop chatting, and you can return to them later to keep the conversation going.

Chats you hold inside the Automation Builder, while designing or editing an automation, are also Chat sessions. Airbyte tracks them separately in the Usage panel as **Automation Builder Chat** so you can see how much of your usage comes from building automations versus general chatting. They appear under the Chat filter in the Sessions table.

### Automation {#automation}

An Automation session is one run of an automation. The session starts when the automation's trigger fires—a schedule, a webhook, or a manual run—and ends when the automation finishes. Automations don't have a user in the loop, so their sessions are typically a sequence of tool calls and internal reasoning rather than a back-and-forth conversation.

Each run of an automation is its own session. If the same automation runs on a schedule, each scheduled run appears as a separate row in the Sessions table.

### Work that isn't counted as a session

Airbyte also processes tool calls from these sources, but doesn't log them as sessions:

- **[MCP](../interfaces/mcp/readme.md)**: Tool calls from agents connected through the Model Context Protocol.
- **[API](../reference/api/readme.md)**: Direct calls to the Airbyte Agents API.
- **[SDK](../interfaces/sdk/readme.md)**: Calls made from an agent built with the Airbyte Agents SDK.

These tool calls still consume AOs and appear in your [Usage panel](./billing.md#monitor-usage), but they don't have a corresponding Sessions row. To review them, open the Usage panel on the Billing page and filter by the **MCP**, **API**, or **SDK** source.

## Review previous session data

Click the **View** icon in a session's row to open the session history. The session history is read-only and shows the full conversation exactly as it happened.

- For a Chat session, you see the messages exchanged between you and the agent, along with the tool calls the agent made in each turn.
- For an Automation session, you see the automation's run in chronological order. Since automations don't have a user in the loop, you mostly see the agent's reasoning and the tool calls it made.

Click a tool call to expand it and see the function name, the connector it targeted, the type of call (Search or Direct), and the arguments the agent passed.

To keep chatting with the agent from where a Chat session left off, click **Continue this chat** at the bottom of the session history. This returns you to the live chat so you can send a new message.

## Access previous sessions

To open the Sessions page, click **Sessions** in the left navigation of your workspace. The page lists sessions across every automation and chat in your workspace. Sessions never expire, so you can review work from any point in your workspace's history.

If you want to see usage without opening individual sessions, the [Usage panel](./billing.md#monitor-usage) on the Billing page summarizes AOs and tool calls across sessions and non-session sources. Rows for Chat, Automation, and Automation Builder Chat link back to the originating session.
