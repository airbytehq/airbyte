---
plan: all
sidebar_position: 3
---

# Skills

Skills are reusable instructions that tell your agents how to handle a particular kind of task. Airbyte serves them to every agent in your organization, regardless of the interface the agent uses: the web app, the MCP server, the API, the SDK, or the CLI. Airbyte provides a set of default skills, and organization administrators can add custom skills from the **Skills** page in the web app.

## What skills are

Each skill is a Markdown document that describes when an agent should use it and what the agent should do. For example, a skill might explain how your team defines a "stalled" sales opportunity, which CRM fields to check, and how to summarize the result. When a user asks an agent about stalled deals, the agent reads the skill and follows it instead of guessing at your conventions.

Skills help you:

- **Encode institutional knowledge.** Capture business definitions, naming conventions, and preferred workflows once, and every agent applies them.
- **Get consistent results.** Agents across chats, interfaces, and teammates follow the same steps and return the same shape of answer.
- **Stay in control of cost.** Agents read only the sections of a skill they need, so detailed guidance doesn't bloat the context window.

Skills are different from the connector documentation an agent reads with `inspect_connector` and `read_skill_docs`. Airbyte generates that documentation from each connector's entities and actions, and you don't edit it. Skills are guidance you write about your own business, and they sit on top of connectors. To learn how agents discover connector documentation, see [Connect, Ask, Act](./connect-ask-act.md).

## Airbyte skills and custom skills

Airbyte provides default skills that improve agents' handling of common tasks. These skills are read-only. You can't edit them, and they don't appear in the list on the Skills page.

Custom skills are skills your organization writes. You create them, publish them, revise them, and delete them from the Skills page, and Airbyte serves them to your agents alongside the default skills.

## Who can manage skills

Everyone in an organization can view the Skills page. Only organization administrators can add, edit, publish, turn on or off, or delete skills, and manage the variables skills use. To learn about roles, see [Governance](./governance.md).

## The skills page

To open the Skills page, click **Skills** in the sidebar of the web app.

The page lists the custom skills in your organization. Use the search box and the status, workspace, tag, and connector filters to find a skill. Each row shows:

- **Name**: The skill's human-readable name.
- **Status**: **Draft**, **Published**, or **Disabled**. Published skills also show a **Draft changes** indicator when an administrator has unpublished edits in progress. Agents keep using the published version until those changes are published.
- **Workspace**: The workspace the skill is limited to, or an indication that it's available across the whole organization.
- **Tags**: The tags you assigned to categorize the skill.
- **Connectors**: The connectors the skill declares.
- **Version**: The version your agents currently run.
- **Reads**: How many times agents read the skill in the last 30 days.

A published skill can show a **Connector missing** warning. This means the skill is published and enabled, but agents aren't receiving it because one or more of its required connectors isn't configured. See [Required and optional connectors](#required-and-optional-connectors).

## Skill fields

When you add or edit a skill, you fill in the following fields.

| Field | Purpose |
| --- | --- |
| **Name** | The human-readable name of the skill. |
| **Skill ID** | The machine-readable name of the skill. Use lowercase letters, numbers, and single hyphens, like `pipeline-hygiene-review`. Agents resolve the skill by this ID, so you can't change it after you publish. |
| **Summary** | A short description of when to use the skill. Agents read the summary to decide whether a skill applies to the task at hand, so describe the situations it covers, like "Use when the user asks about stalled or incomplete opportunities in the CRM pipeline." |
| **Workspace** | Limits the skill to a single workspace. Leave it empty to make the skill available across the whole organization. You can't change the workspace after you publish. |
| **Tags** | Labels that categorize your skills. Tags appear in the skills list and power the tag filter. |
| **Instructions** | The skill's content, written in Markdown. Each `## Heading` is a section an agent can read separately. Organize your instructions into focused sections so agents can load only what they need. |
| **Serve as single document** | When this option is on, agents read the full skill at once. When it's off, agents read the outline and choose which sections to read by heading. Turn it off for long skills to keep the agent's context window small. |
| **Required connectors** | Connectors that always use this skill. Airbyte serves the skill only when every required connector is configured. You can't change required connectors after you publish. |
| **Optional connectors** | Connectors that may use this skill when needed. Optional connectors don't affect whether Airbyte serves the skill. |
| **Variables** | Placeholders in your instructions that Airbyte fills in when it serves the skill. See [Variables](#variables). |

Skills have limits on the length of the name, summary, tags, and instructions. The editor shows a character or byte count next to each limited field.

### Required and optional connectors

Connectors tell Airbyte which of your connected systems a skill is about.

- **Required connectors** gate whether Airbyte serves the skill. Airbyte serves the skill only when all of its required connectors are configured. If the skill is limited to a workspace, the connectors must be configured in that workspace. If the skill is organization-wide, the connectors must be configured somewhere in the organization. When a required connector is missing, the skill stays published and enabled but the Skills page shows a **Connector missing** warning and agents don't receive it. Configuring the connector clears the warning.
- **Optional connectors** don't gate serving. Declare a connector as optional when the skill benefits from it but works without it, or when a variable in the skill reads from it.

A connector can't be both required and optional. Changing a skill's connectors re-resolves the variable values the skill reads.

:::warning
You can't change a skill's required connectors after you publish it. If you need different required connectors, create a new skill.
:::

## Create a skill

1. On the Skills page, click **Add skill**.
2. Fill in the [skill fields](#skill-fields).
3. Do one of the following.
    - Click **Save as draft** to keep working on the skill later. Drafts are never used by your agents.
    - Click **Publish** to make the skill available. Enter a short note explaining what the skill does, and confirm. Airbyte creates version 1 and agents start using it immediately.

If a skill has never been published, you can remove it by clicking **Discard draft**. This deletes the skill.

## Modify a skill

Published versions of a skill are immutable. To change a skill, you edit a draft and publish it as a new version.

1. On the Skills page, open the skill and click **Edit**. Airbyte starts a draft based on the version your agents currently run. If another administrator already has a draft open, Airbyte shows that draft instead.
2. Make your changes. Save your work at any time with **Save as draft**. Agents continue to use the published version while draft changes exist.
3. When you're ready, click **Publish**, enter a note describing what changed, and confirm. Airbyte creates the next version number and agents switch to it immediately.

To abandon your changes, click **Discard draft changes**. The skill returns to the version your agents run now.

### Validation

Before you can publish, the draft must pass validation. The editor lists any problems at the top of the form, for example:

- A field exceeds its length limit.
- The instructions reference a variable that doesn't exist.
- The instructions reference a variable that reads from a connector the skill doesn't declare as required or optional.
- Nothing has changed since the live version.

You can save a draft that has validation problems, but you can't publish it until you fix them.

### Concurrent edits

If two administrators work on the same skill at once, Airbyte protects the published version.

- If someone else saves the draft while you're editing it, your save is refused. Reload the draft and reapply your edits.
- If someone else publishes or discards the draft while you're editing it, Airbyte shows you the current version.
- If someone changes the active version after you start a draft, you can't publish that draft. Discard it, or make its starting version active again first.

## Versioning

Every time you publish, Airbyte records a new, immutable version of the skill along with your note, your name, and the date. The version your agents run is the **active** version.

To see the history, open the skill and click **Version history**, or click the version chip in the editor. The history shows every published version and marks the one that's live.

### Roll back to an earlier version

You don't need to republish to return to an earlier version.

1. Open the version history and find the version you want.
2. Click **Make this version live**, optionally enter a note explaining why, and confirm.

Airbyte moves the pointer your agents follow to that version. No new version is created, and the previous active version stays in the history. If the skill has an open draft based on a different version, that draft can't be published until you discard it or re-activate its starting version.

To read the content of an earlier version without activating it, click **View** next to it. Airbyte shows it read-only.

## Disable and enable a skill

Disabling a skill stops agents from using it without deleting it or changing its versions. Use this to pause a skill while you investigate a problem.

1. On the Skills page, open the skill's actions menu and click **Disable**.
2. Confirm.

The change applies to new agent sessions. To turn the skill back on, choose **Enable** from the same menu. If you activate a different version while the skill is off, agents don't receive it until you enable the skill.

## Delete a skill

Deleting a skill removes it from every agent in your organization. You can't undo this.

1. On the Skills page, open the skill's actions menu and click **Delete**.
2. Confirm by clicking **Delete skill**.

You can only delete custom skills. To stop using a skill temporarily, [disable it](#disable-and-enable-a-skill) instead.

## Variables

Variables let a skill reference values that Airbyte fills in when it serves the skill, so you don't hard-code them in the instructions. Reference a variable in the instructions as `{{key}}`, or click **Insert variable** in the editor to pick one and insert it at the cursor.

Skills can use two kinds of variables.

- **Platform variables**: Airbyte resolves these from a connected source, for example an ID discovered from your CRM. They have no value to set. A platform variable resolves only when the connector it reads from is declared on the skill and configured in the skill's scope.
- **Organization variables**: Values your organization defines, like a quarterly revenue target. Each variable has a key, a label, a description agents see, and a value.

Organization administrators create and edit organization variables from the variable picker in the skill editor. A key uses lowercase letters, numbers, and underscores, and can't start with a number or reuse a key Airbyte reserves.

Variables are shared across all skills in the organization. Renaming or deleting a variable immediately breaks any skill or draft that references the old key, and republishing the skill isn't enough to fix it. Update each affected skill to use the new key. The variable dialog tells you how many skills and drafts reference a variable before you rename or delete it.

## Limitations

- Airbyte-provided skills are read-only and don't appear in the skills list.
- After you publish a skill, its skill ID, workspace, and required connectors are locked.
- Disabling or enabling a skill affects new agent sessions, not sessions already in progress.
- Deleting a skill is permanent.
