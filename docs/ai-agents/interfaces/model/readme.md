---
plan: all
sidebar_position: 5
sidebar_label: Airbyte model
---

# Airbyte model

The Airbyte model is a natural language interface to your data. Point any client that speaks the OpenAI Responses API or the Anthropic Messages API at Airbyte, select `airbyte:v1` as the model, and ask questions in plain language. Airbyte picks the connectors, runs the read-only queries, and answers with your data.

To your coding agent or client, Airbyte looks like a normal model. There's nothing to install and no protocol to implement: you change a base URL, a model name, and an API key.

:::note Public alpha

The Airbyte model is in public alpha. Its behavior, limits, and setup steps can change.

:::

## When to use the Airbyte model

Use the Airbyte model when:

- You want an existing coding agent, like Codex or Claude Code, to answer questions about your business data without installing or configuring anything else.
- Your client can point at a custom model endpoint, but doesn't speak Model Context Protocol.
- You want Airbyte to do the reasoning. The model decides which connectors to query and how, and returns a written answer instead of raw records.
- You're prototyping and don't want to write agent code.

Use a different interface when:

- **You need your own agent's reasoning, tools, or prompts.** The Airbyte model is a sealed agent. It never calls your client's tools and doesn't accept your system prompt. Use the [MCP server](../mcp/readme.md) if your client speaks MCP, or the [SDK](../sdk/readme.md) or [API](../api/readme.md) if you're writing the agent yourself.
- **You need raw, structured records.** The Airbyte model answers in prose. The [CLI](../cli/readme.md), [SDK](../sdk/readme.md), and [API](../api/readme.md) return data you can pipe, parse, or store.
- **You're scripting or running in CI.** The [CLI](../cli/readme.md) composes with shell tools and exits with a status code.
- **You want the cheapest reasoning.** With every other bring-your-own-agent interface, you pay your own model provider for reasoning and Airbyte only bills tool calls. With the Airbyte model, Airbyte does the reasoning and bills for it. See [Pricing](#pricing).

For a side-by-side comparison of all interfaces, see [Choose how to use Airbyte Agents](../../get-started/choose-how-to-use.md).

## Requirements

Before you begin, make sure you have the following:

- **An Airbyte Agents account.** Sign up at [app.airbyte.ai](https://app.airbyte.ai) if you don't have one.

- **An API key.** See [API keys](../../admin/api-keys.md).

- **Connectors in the key's workspace.** The model can only query sources that are authenticated in the workspace the key belongs to. See [Add a connector](../ui/add-connector.md).

- **A supported client.** Codex, Claude Code, pydantic-AI, or anything else that can call the OpenAI Responses API or the Anthropic Messages API against a custom base URL.

## Endpoints

| Client type | Base URL | Model |
| --- | --- | --- |
| OpenAI Responses, like Codex, pydantic-AI, and the OpenAI SDK | `https://api.airbyte.ai/v1` | `airbyte:v1` |
| Anthropic Messages, like Claude Code | `https://api.airbyte.ai` | `airbyte:v1` |

Anthropic clients append `/v1/messages` themselves, so their base URL omits `/v1`. Authenticate with your API key as a bearer token, or as `x-api-key` on Anthropic clients.

## Set up your client

Create an API key in the web app first. After you create it, Airbyte shows these same snippets with your key already filled in. You can reopen them at any time from **Setup instructions** on the **API Keys** page.

<details>
<summary>Codex on macOS or Linux</summary>

1. Save the following profile as `~/.codex-airbyte/airbyte.config.toml`. Use a dedicated Codex home so Airbyte's model catalog doesn't affect your normal Codex sessions.

   ```toml title="~/.codex-airbyte/airbyte.config.toml"
   model = "airbyte:v1"
   model_provider = "airbyte"

   [model_providers.airbyte]
   name = "Airbyte Model"
   base_url = "https://api.airbyte.ai/v1"
   wire_api = "responses"
   # Optional: uncomment and export AIRBYTE_SOURCE_ID to pin one connector per session.
   # env_http_headers = { "X-Airbyte-Source-Id" = "AIRBYTE_SOURCE_ID" }

   [model_providers.airbyte.auth]
   command = "/usr/bin/printenv"
   args = ["AIRBYTE_MODEL_API_KEY"]
   refresh_interval_ms = 0
   ```

   Keep these keys at the top level of the file. Don't nest them under a `[profiles.airbyte]` table, and remove any `[profiles.airbyte]` entry from `config.toml`. Codex refuses `--profile airbyte` if both exist.

2. Export your key and start Codex.

   ```bash
   export CODEX_HOME="$HOME/.codex-airbyte"
   mkdir -p "$CODEX_HOME"
   export AIRBYTE_MODEL_API_KEY="abm_..."
   codex --profile airbyte -m "airbyte:v1" "List my Linear teams with their keys."
   ```

Codex needs the `[model_providers.airbyte.auth]` command block to discover Airbyte's model catalog. If you replace it with `env_key`, Codex can't list the model.

</details>

<details>
<summary>Codex on Windows</summary>

1. Save the following profile as `%USERPROFILE%\.codex-airbyte\airbyte.config.toml`.

   ```toml title="%USERPROFILE%\.codex-airbyte\airbyte.config.toml"
   model = "airbyte:v1"
   model_provider = "airbyte"

   [model_providers.airbyte]
   name = "Airbyte Model"
   base_url = "https://api.airbyte.ai/v1"
   wire_api = "responses"
   # Optional: uncomment and export AIRBYTE_SOURCE_ID to pin one connector per session.
   # env_http_headers = { "X-Airbyte-Source-Id" = "AIRBYTE_SOURCE_ID" }

   [model_providers.airbyte.auth]
   command = "powershell.exe"
   args = ["-NoProfile", "-NonInteractive", "-Command", "$env:AIRBYTE_MODEL_API_KEY"]
   refresh_interval_ms = 0
   ```

2. Export your key and start Codex in PowerShell.

   ```powershell
   $env:CODEX_HOME = "$env:USERPROFILE\.codex-airbyte"
   New-Item -ItemType Directory -Force -Path $env:CODEX_HOME | Out-Null
   $env:AIRBYTE_MODEL_API_KEY = "abm_..."
   codex --profile airbyte -m "airbyte:v1" "List my Linear teams with their keys."
   ```

</details>

<details>
<summary>Claude Code on macOS or Linux</summary>

Set the base URL, your key, and all four model variables, then start Claude Code.

```bash
export ANTHROPIC_BASE_URL="https://api.airbyte.ai"
export ANTHROPIC_API_KEY="abm_..."
export ANTHROPIC_MODEL="airbyte:v1"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="airbyte:v1"
export ANTHROPIC_SMALL_FAST_MODEL="airbyte:v1"
export CLAUDE_CODE_SUBAGENT_MODEL="airbyte:v1"
claude
```

Set all four model variables. Claude Code picks a model per request type, and requests that ask for any other model fail with `400`.

</details>

<details>
<summary>Claude Code on Windows</summary>

Set the base URL, your key, and all four model variables in PowerShell, then start Claude Code.

```powershell
$env:ANTHROPIC_BASE_URL = "https://api.airbyte.ai"
$env:ANTHROPIC_API_KEY = "abm_..."
$env:ANTHROPIC_MODEL = "airbyte:v1"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "airbyte:v1"
$env:ANTHROPIC_SMALL_FAST_MODEL = "airbyte:v1"
$env:CLAUDE_CODE_SUBAGENT_MODEL = "airbyte:v1"
claude
```

Set all four model variables. Claude Code picks a model per request type, and requests that ask for any other model fail with `400`.

</details>

<details>
<summary>pydantic-AI</summary>

Read the key from the environment so it never lands in a file you might commit.

```python
import os

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIResponsesModel(
    "airbyte:v1",
    provider=OpenAIProvider(base_url="https://api.airbyte.ai/v1", api_key=os.environ["AIRBYTE_MODEL_API_KEY"]),
)
agent = Agent(model)

result = agent.run_sync("List my Linear teams with their keys.")
print(result.output)
```

</details>

<details>
<summary>Any other client</summary>

Call the endpoints directly. Both support streaming with `"stream": true`.

```bash title="OpenAI Responses"
curl -X POST "https://api.airbyte.ai/v1/responses" \
  -H "authorization: Bearer $AIRBYTE_MODEL_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"airbyte:v1","input":"List my Linear teams."}'
```

```bash title="Anthropic Messages"
curl -X POST "https://api.airbyte.ai/v1/messages" \
  -H "x-api-key: $AIRBYTE_MODEL_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"airbyte:v1","max_tokens":4096,"messages":[{"role":"user","content":"List my Linear teams."}]}'
```

</details>

## Choose which connector answers

Each request runs against one source in the key's workspace. There are two ways to choose it.

- **Name the connector in your question.** For example, "Query my Salesforce source for opportunities that closed last month." Airbyte lists the sources in the workspace and picks the one you named. If the workspace has more than five sources and your question doesn't identify one, Airbyte asks you to pin a source instead.

- **Pin a source for the whole session.** Send the `X-Airbyte-Source-Id` header with a source name or ID. Every request then runs against that source. In Codex, uncomment `env_http_headers` in the profile and export `AIRBYTE_SOURCE_ID`.

## What the Airbyte model doesn't do

The Airbyte model is a sealed agent, not a general-purpose one. Compared to a normal model endpoint:

- **It answers only from your connected data.** Queries are read-only. It can't write to your sources, run your client's tools, or edit files.
- **It ignores your system prompt and generation settings.** Fields like `instructions`, `system`, `tools`, `temperature`, and `max_tokens` are accepted and ignored so clients don't break, but they don't change the answer.
- **It doesn't remember conversations.** Every turn is independent. Clients that resend the conversation get an answer based on that replayed history, but `previous_response_id` and `store` don't retrieve anything server-side.
- **It accepts text only.** Images, documents, and tool results in the newest message are rejected.
- **It stops long runs.** Each run has a fixed processing budget. When a run reaches it, Airbyte returns a notice asking you to narrow the request by project, status, date, or result count.

## Pricing

The Airbyte model consumes [agent operations (AOs)](../../concepts/agent-operations.md) for both tool calls and reasoning, because Airbyte, not you, runs the model. This is different from the MCP server, the API, the SDK, and the CLI, where you bring your own model and Airbyte bills tool calls only. Usage appears in the Usage panel on the [Billing](../../admin/billing.md) page.

Because clients resend conversation history on every turn, long conversations cost more than short, specific ones.

## Activity isn't shown in the web app

Airbyte model activity doesn't appear on the [Sessions](../../admin/sessions.md) or [Tool Calls](../../admin/tool-calls.md) pages. Your client shows what the model is doing while it works, and usage is reflected in billing, but there's no record to review in the web app afterward.

## Troubleshoot

| What you see | What it means |
| --- | --- |
| `401` | Your key is wrong, revoked, or expired. Create a new one. |
| A request to pin a source | The workspace has more than five sources and the question didn't name one. Name the connector or send `X-Airbyte-Source-Id`. |
| `503`, or an answer saying data isn't ready | The source hasn't finished its initial sync. Counts and aggregates need the [Context Store](../../concepts/context-store.md) to be populated. Wait and try again. |
| `400` on some Claude Code requests | One of the four model variables isn't set, so Claude Code asked for a different model. |
| `429` | You hit a rate limit. Retry with backoff. |

<!-- The adapter also accepts a workspace-scoped Airbyte token minted with org Application
credentials (POST /api/v1/account/applications/scoped-token). It's undocumented on purpose:
the ~20-minute TTL expires mid-session and forces a re-mint and client restart. Revisit if
embedded customers need per-end-user credentials. -->
