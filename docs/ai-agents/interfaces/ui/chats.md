---
sidebar_position: 1
---

# Chats

A Chat is a conversation between you and an Airbyte agent in the web app. You send a prompt, the agent decides which connectors to use and which tool calls to make, and it replies with an answer grounded in your data. Chats are the fastest way to explore data, get a one-off answer, or prototype an idea before turning it into a reusable [Automation](./automations).

To open Chats, click **New chat** in the left sidebar, or click an existing chat under **Recent Chats**.

## Start a new chat

Click **New chat** in the sidebar to open the Chat landing page. Type a prompt in the text box and press Enter, or click the send button. Airbyte creates a new chat session, opens it, and sends your first message automatically.

Every chat runs against the connectors you've already authenticated in your workspace. You don't need to select connectors up front—the agent picks the right ones based on your prompt and the [context](#context) available to it.

### Templates

The Chat landing page suggests prompts you can use instead of writing your own. Suggestions are grouped into categories such as Sales, Support, Marketing, Finance, Security, Product, HR, Ops, and Engineering. Click a category chip to filter the suggestions, then click a suggestion to copy it into the prompt box. Edit the prompt if you want to adapt it, then send it.

Suggestions are starting points, not fixed templates. The agent treats the text exactly like any other prompt, so you can freely reword or combine suggestions.

## Resume an old chat

Every chat you start is saved. To return to a chat, open the sidebar and click the chat under **Recent Chats**. The sidebar shows your five most recent chats by default. Click **Show more** to expand the list, or open the Sessions page from Settings to browse every chat and automation run in your organization.

When you reopen a chat, the full history loads in place and you can continue the conversation by sending another message. Older messages stay available—scroll up or click **Load older messages** to page through the history.

Only the person who started a chat can send messages in it. If another member of your organization opens the chat (for example, via a link to its URL), they see the full conversation in read-only mode and can't post new messages.

## Context

**Context** is the data and connectors the agent can use to answer your prompt. Airbyte uses the context to decide which tool calls to make, which entities to query, and how to interpret your question.

### What context is available

Two places surface the context the agent has.

- **When starting a chat**: The Chat landing page lists every connector you've already authenticated in the workspace under **Available context**. The agent can use any of these connectors automatically, so you don't need to name them in your prompt.
- **From the chat itself**: Inside an open chat, click the **Context** dropdown over the message input to see the same list. Each entry shows the connector's name and logo. If a connector doesn't appear in either view, the agent can't use it in this chat.

### Add new context

To give the agent more to work with, connect another source. Open the **Credentials** page from the sidebar, connect the new source, and authenticate it. The new connector is immediately available in any chat you open afterward.

If you're in the middle of a chat and realize the agent needs a connector it doesn't have, connect the source in another tab, then return to the chat and ask the agent to try again. The agent picks up the new connector automatically on its next message.

## What you can use Chats for

Chats are best for interactive, one-off work where you want to iterate with the agent. Common use cases include:

- **Exploring data**: Ask natural-language questions about your customers, deals, tickets, or usage data and drill deeper based on the agent's replies.
- **Summarizing and reporting**: Generate on-demand summaries, such as "What deals closed this quarter?" or "Which accounts have the most open support tickets?"
- **Cross-system questions**: Ask questions that span multiple connectors. For example, match Salesforce accounts to HubSpot contacts or Zendesk tickets.
- **Drafting content**: Use replies as a starting point for emails, follow-ups, status updates, or internal notes.
- **Prototyping an Automation**: Iterate on a prompt in Chat until the agent reliably returns what you want, then convert the chat into an [Automation](./automations) so it can run on a schedule or webhook.

If you want the same work to happen repeatedly, on a schedule, or in response to an event, use an Automation instead.

## Tips for effective conversations

- **Be specific about the outcome**: Tell the agent what you want back. "List the 10 highest-value open Salesforce deals, sorted by amount, with owner and close date" works better than "Show all deals."
- **Name the source if you know it**: If you want data from a specific connector, say so. "Pull ticket counts from Zendesk" is clearer than "Pull ticket counts," especially when multiple connectors cover similar data.
- **Iterate in small steps**: Ask a question, review the answer, then refine. Agents do their best work when you narrow in gradually rather than asking one complex question.
- **Check tool calls when something looks off**: Expand a tool call in the conversation to see which connector the agent used, which entity it queried, and whether the call succeeded. This is the fastest way to diagnose unexpected results.
- **Give feedback on replies**: Use the thumbs-up or thumbs-down buttons on any assistant message. Feedback helps Airbyte improve agent quality and helps you remember which replies you trusted.

## Convert a chat to an automation

As your chat develops, you may want to turn it into something that can run repeatedly. These are called Automations.

To convert a chat, click **Automate this** at the top of the chat. Airbyte takes the prompt and tools you've been iterating on, converts the existing chat session into a new Automation seeded with those settings, and opens it in the [Automation Builder](./automations#the-automation-builder) so you can add a trigger, fine-tune the prompt, and run it.

Converting a chat replaces it—the original chat is turned into the Automation and no longer appears as a chat. If you want to keep exploring the same question as a chat after converting, start a new chat. The resulting Automation starts in draft, so it doesn't run until you configure a trigger and enable it. See [Automations](./automations) for the full builder workflow.
