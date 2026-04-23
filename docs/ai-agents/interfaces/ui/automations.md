---
sidebar_position: 2
---

# Automations

An Automation is an agent task that runs on its own, without a human in the loop. You describe what you want done once, pick how you want to trigger it—manually, on a schedule, or from a webhook—and Airbyte runs the task every time the trigger fires. Automations are the right choice when you need the same work to happen repeatedly, reliably, and without someone sitting at a keyboard.

To open Automations, click **Automations** in the left sidebar.

## Create a new automation

You can create an Automation three ways. The first two start from the Automations page; the third converts an existing [Chat](./chats).

### From scratch

Click **New Automation** at the top of the Automations page. Airbyte opens a prompt dialog. Describe what you want the Automation to do in plain language, then press Enter or click the send button.

Airbyte creates the Automation in draft, seeds the Automation Builder with your prompt, and takes you into the Automation Builder so you can iterate on it, configure a trigger, and try a test run. See [The Automation Builder](#the-automation-builder) for details.

### From an idea

If you're not sure how to phrase your prompt, use a suggestion. The New Automation dialog lists ready-made ideas grouped into categories such as Sales, Support, Marketing, Finance, Security, Product, HR, Ops, and Engineering.

Click a category chip to filter the list, then click an idea to copy it into the prompt box. Edit the prompt if you want to adapt it to your workspace, then send it. Airbyte creates the Automation from the adapted prompt exactly as if you'd written it yourself.

The first time you open Automations in a new workspace, the same suggestions appear on the empty Automations page so you can start building without going through the dialog.

### From a chat

Any Chat can become an Automation. Open the chat and click **Automate this** at the top of the conversation. Airbyte takes the prompt and tool configuration you iterated on in the chat, converts the chat session into a new Automation seeded with those settings, and moves you into the Automation Builder to finish configuring it. The original chat is replaced by the Automation and no longer appears in Recent Chats.

See [Convert a chat to an automation](./chats#convert-a-chat-to-an-automation) for more detail.

## Open an existing automation

### From the sidebar

Recent Automations you've opened appear under **Recent Chats** in the sidebar, alongside your recent chats. Automations use a bolt icon so you can distinguish them at a glance. Click an Automation in the list to jump back into its Automation Builder.

### From the Automations page

Click **Automations** in the sidebar to open the full list. Every Automation in the workspace appears in the table, with its status, trigger, tools, and enabled state.

Use search and filters to find what you want:

- **Search**: Type in the search box at the top of the table to filter by Automation name.
- **Status**: Filter by Running, Active, Paused, Failed, or Draft.
- **Trigger**: Filter by Manual, Schedule, or Webhook.
- **Enabled**: Show only enabled Automations, only turned-off Automations, or both.

Click the **Edit** (pencil) icon on a row to open the Automation in the Automation Builder. Automations created before session linking was introduced can't be edited from this button; Airbyte disables the icon and explains why on hover.

## Delete an automation

To delete an Automation, click the trash icon on its row on the Automations page, or click **Delete** in the Automation Builder header. Airbyte asks you to confirm. Once you confirm, Airbyte permanently removes the Automation and all of its configuration. Deletion can't be undone. Existing run history rows that reference this Automation remain in the Sessions page for auditing.

## Rename an automation

Open the Automation in the Automation Builder and click **Properties** to open the Properties panel. Edit the **Name** field. Airbyte saves the change automatically when you click out of the field. The header shows a **Saving…** then **Saved** indicator to confirm. The new name appears immediately on the Automations page and in the sidebar.

## Turn an automation on or off

Scheduled Automations run automatically when their trigger fires. To pause a scheduled Automation without deleting it, turn its **Enabled** toggle off. The next scheduled time is skipped, and the Automation's status changes to Paused. Turn the toggle back on to resume.

You can toggle Enabled from the table on the Automations page or from the Properties panel in the Automation Builder. The toggle is only available for Automations with a Schedule trigger; Manual and Webhook Automations are always "on" in the sense that they run whenever you invoke them, so there's nothing to pause.

## The Automation Builder {#the-automation-builder}

The Automation Builder is where you design, iterate on, and run an Automation. Open it by creating a new Automation, clicking **Edit** on a row in the Automations page, or opening an Automation from the sidebar.

The Automation Builder has two tabs:

- **Agent**: A chat with the Automation Builder Agent. Describe what you want the Automation to do, correct its approach, and ask it to try again. Each message runs as a test in the same way a Chat does, so you can validate behavior before committing to a schedule.
- **Run History**: A list of every live and test run, with status, timestamps, and job-level details. See [Run history](#run-history).

The right side of the Automation Builder shows the Properties panel. Click the **Properties** button in the header to show or hide it.

Click **Back to Automations** in the header to return to the Automations page. Airbyte saves your changes automatically as you work; the header shows a **Saving…** then **Saved** indicator to confirm.

### Tips for chatting with the Automation Builder Agent

- **Treat the Automation Builder chat like a spec-writing conversation**: Describe the outcome, then iterate. Ask the agent to adjust scope, change which connector it queries, or add a step.
- **Try a test run early**: Click **Run** in the header after the agent proposes an approach. A test run uses the current draft and shows up in Run History tagged **Test run**, so you can check behavior before enabling a schedule.
- **Use the Context list to confirm connectors**: The Properties panel shows which connectors the Automation uses. If something is missing, tell the agent which connector to use and it updates the context.
- **Keep prompts specific and self-contained**: Automations don't have a user to answer follow-up questions at run time. Spell out exactly what to check, which fields to return, and where to send the result.

### Properties

Click **Properties** in the header to open the Properties panel. The panel contains:

- **Name**: The Automation's display name. Shown in the table, sidebar, and run history. Editable inline.
- **Prompt**: The original prompt the Automation was created from, shown read-only for reference. To change what the Automation does, chat with the Automation Builder Agent.
- **Context**: The connectors this Automation uses. Managed through the Automation Builder chat; edit connector membership by asking the agent to add or remove a source. Airbyte blocks direct editing here to keep the prompt and context consistent.
- **Trigger**: How the Automation is invoked. Choose Manual, Schedule, or Webhook. See [Run automations](#run-automations).
- **Schedule**: Visible when the trigger is Schedule. A builder that lets you pick a frequency (hourly, daily, weekly, monthly, or a raw cron expression) and a timezone.
- **Result webhook (optional)**: A destination URL where Airbyte posts results after a run finishes. See [Result webhooks](#result-webhooks).

## Run automations

An Automation runs when its trigger fires. Choose one trigger per Automation.

### Manually

Manual Automations only run when you explicitly invoke them. Click the **Run** (play) icon on the Automation's row in the Automations page, or click **Run** in the Automation Builder header, to start a run immediately. Airbyte queues the run, shows a confirmation, and records it in Run History. Use manual runs for Automations you want available on demand but not on a clock—for example, an end-of-quarter summary you invoke when you're ready to review it.

### On a schedule

Scheduled Automations run at times you define. Open the Properties panel, set **Trigger** to Schedule, and use the schedule builder to pick the cadence:

- **Hourly**, **Daily**, **Weekly**, or **Monthly** for common cases. Airbyte shows the equivalent cron expression so you can verify the schedule.
- **Custom cron** for anything the builder doesn't cover. Provide the raw cron expression and Airbyte translates it into a human-readable summary.

Pick the **Timezone** the schedule should use. Airbyte defaults to your local timezone. See [Time zones](../../concepts/time-zones) for how Airbyte stores and displays times across interfaces. Turn the Automation's **Enabled** toggle on to activate the schedule. Each scheduled run appears in Run History tagged **Live run**.

#### How scheduled runs are dispatched

Airbyte dispatches scheduled Automations at the exact moment the cron expression matches, in the timezone you selected. The scheduler doesn't apply jitter or a random offset, so every Automation whose schedule matches the same instant is dispatched together. For example, two Automations scheduled for `0 * * * *` in the same timezone both fire at the top of the hour.

Keep this in mind when you design schedules:

- **Avoid stacking many heavy Automations on the same round cadence.** If you have several Automations that each do substantial work, stagger them across different minutes (for example, `5 * * * *`, `15 * * * *`, `25 * * * *`) rather than running them all at `0 * * * *`. This spreads load on your connectors, reduces the chance of hitting upstream rate limits at the same moment, and makes failures easier to diagnose one Automation at a time.
- **Expect near-simultaneous webhook or connector calls** when multiple Automations share a trigger time and hit the same third-party API. If that API enforces per-minute rate limits, consider splitting the schedules.
- **Dispatch time isn't execution time.** Airbyte dispatches the run on the dot, but the agent work itself takes as long as it takes. A 9:00 schedule doesn't guarantee results by 9:00—only that the run starts then.

If you need a schedule that's more fine-grained than the Automation Builder's presets allow, use **Custom cron** and pick a specific minute offset that isn't shared with your other Automations.

### From a webhook

Webhook Automations run when an external system posts to a URL Airbyte provides. Open the Properties panel, set **Trigger** to Webhook, and copy the generated webhook URL. Configure the external system to post to that URL when the event you care about happens. Each POST starts one run.

Webhook Automations are useful for event-driven workflows like "when a Salesforce deal closes, create an onboarding ticket and notify the team in Slack."

### See the status of a running automation

While an Automation is running, its row on the Automations page shows a **Running** status badge, and the Run History tab in the Automation Builder shows a run in state **Running**. The spinner clears when the run finishes; the row's status then reflects the outcome of the most recent run (Active, Paused, or Failed).

For a step-by-step view of what happened during a run, open the run in Run History or open the session from the [Sessions page](../../admin/sessions).

## Result webhooks

A result webhook is an optional URL where Airbyte posts the result of each run. Set it in the Properties panel under **Result webhook**.

When a run finishes, Airbyte POSTs a JSON payload containing the Automation's output to the URL you provided. Use result webhooks to:

- Forward Automation output to another system, like a message channel, a queue, or a dashboard.
- Chain Automations together—one Automation's result webhook triggers another system that kicks off the next step.
- Store results somewhere you control, in addition to Airbyte's own history.

Result webhooks are currently persisted for scheduled Automations. If you leave the field blank, Airbyte still records the result in Run History—it just doesn't forward it anywhere.

## Run history

The Run History tab in the Automation Builder lists every run of the current Automation, most recent first. Each entry shows:

- A **Test run** or **Live run** badge. Test runs come from the **Run** button in the Automation Builder; live runs come from a schedule or webhook trigger.
- The run's overall state: **Running**, **Succeeded**, or **Failed**.
- When the run was created and how many jobs it produced.
- A per-job breakdown with state (Pending, Created, Ready, Running, Retrying, Cancelled, Failed, or Completed) and the job's result.

Click a run to expand it and see the full job-level detail. Runs page 10 at a time; use the pagination buttons at the bottom to see older runs.

Run History is scoped to one Automation. To audit runs across every Automation in the workspace, along with Chat sessions, open the [Sessions page](../../admin/sessions).

## Automation versions

Airbyte treats the current state of the Automation Builder as the draft version of the Automation. As you chat with the Automation Builder Agent or edit properties, Airbyte saves your changes automatically, and the header's **Saving…** / **Saved** indicator confirms each save.

- **Test runs** always execute against the current draft. Use them to verify a change before letting a schedule pick it up.
- **Live runs** (scheduled or webhook) also run against the current saved state. After you edit an Automation, the next live run uses the new version.
- **Run History** records which version of the Automation produced each run, so you can correlate behavior changes with edits.

Because each edit is saved in place, there isn't a separate "publish" step. If you want to experiment without affecting a live schedule, turn **Enabled** off, iterate with test runs until you're satisfied, and turn Enabled back on.
