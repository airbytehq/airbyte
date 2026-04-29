---
sidebar_position: 3
---

# Execute operations

Once you've added a connector to your workspace, you can run operations against it from Python. The SDK offers three execution paths and patterns for exposing a connector as a tool to an AI agent framework.

## Direct execution

The `connect()` factory takes a connector slug and returns an execution object. Call its `execute(entity, action, params)` method to run an operation. When your workspace has exactly one connector of a given type, you don't need to pass a `connector_id` — the SDK resolves the connector by its slug automatically.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import connect

async def main():
    github = connect("github")
    try:
        result = await github.execute("issues", "list", params={"per_page": 10})
        for row in result.data:
            print(row)
    finally:
        await github.close()

asyncio.run(main())
```

- `entity` is the resource, such as `issues`, `repositories`, or `pull_requests`.
- `action` is one of the connector's supported actions, such as `list` or `get`. Some connectors support additional actions like `search` or `download`; check the connector's reference page.
- `params` contains action-specific arguments. The exact keys are connector- and entity-specific — GitHub's `issues.list` accepts `per_page`, for example, while other connectors paginate via `cursor`. Use [`list_entities()`](#introspection) to discover the parameters a connector supports at runtime.
- Always wrap the call in `try`/`finally` and `await connector.close()` once you're done to release the underlying HTTP client.

See the connector's page in the [Connectors](../../connectors) reference for the entities and actions it supports.

### Typed connectors and `HostedExecutor`

For connectors with a generated typed submodule, `connect()` returns a typed connector with IDE autocompletion, method-level docstrings, and structured call shortcuts. For example: `await hubspot.contacts.list(limit=10)`. The [agent connectors](../../connectors) page lists every connector; the **Slug** column is the string to pass to `connect()`.

For every other connector in the bundled registry, `connect()` returns a generic `HostedExecutor` with the same `execute(entity, action, params)` method but without typed shortcuts. The execution behavior is otherwise identical.

`connect()` raises `ValueError` if the slug isn't in the bundled registry (the message lists every supported slug) or if no Airbyte credentials are available. It does *not* raise when a typed submodule is missing — YAML-only connectors return a `HostedExecutor`.

### Multiple connectors of the same type

If your workspace has more than one connector of a given type — for example, two separate Stripe accounts — slug resolution is ambiguous. Pass an explicit `connector_id` to `connect()` so the SDK knows which one to target:

```python title="agent.py"
stripe_us = connect("stripe", connector_id="<us_account_connector_id>")
stripe_eu = connect("stripe", connector_id="<eu_account_connector_id>")
```

<!--
AGENTIC-1134: Without a connector_id, connect("stripe") returns an executor
successfully and only raises ValueError("Multiple connectors found ...") on
the first .execute() call. Public docs shouldn't call out the exact timing;
instead steer readers to pass connector_id up front.
-->

For patterns that look up a connector ID without hard-coding it, see [Get a connector](./add-connector#get-a-connector).

## Natural-language queries

`ask()` and `ask_sync()` dispatch a natural-language prompt across every connector in a workspace. Airbyte routes the prompt to the right connector, runs the right operations, and returns a structured result.

```python title="agent.py"
import asyncio
from airbyte_agent_sdk import ask

async def main():
    result = await ask("list my 5 most recent Stripe customers")
    print(result.outcome, result.answer)
    for call in result.results:
        print(call.entity, call.action, call.status)

asyncio.run(main())
```

Check `result.outcome == "success"` before trusting `result.answer`. The `result.results` list contains one entry per tool call the dispatcher made. Each entry is an `AskToolCallResult` with the fields the dispatcher saw end-to-end:

```python title="Example result.results[0] for a routed list call"
AskToolCallResult(
    source_id="58caf5e9-7a6b-4d1e-9f3c-d4a2e81b9f70",
    entity="customers",
    action="list",
    params={"limit": 5},
    status="success",
    data=[{"id": "cus_…", "email": "…"}, ...],
    connector_metadata={"has_next_page": True, "end_cursor": "…"},
    execution_time_ms=2635,
)
```

When the dispatcher routes to a connector-native read (`action="list"` or `"get"`), `data` is a flat list or a single record, and pagination lives in `connector_metadata`.

<!--
AGENTIC-1138 problem 1: context_store_search routing nests records and
pagination together under data.{data,meta}, and leaves connector_metadata
null. Don't document this in the public narrative; once the backend
normalizes to the connector-native envelope this paragraph can go.
-->

Use `ask_sync()` in scripts and notebooks where you don't want to manage an event loop:

```python title="notebook.ipynb"
from airbyte_agent_sdk import ask_sync

result = ask_sync("list my 5 most recent Stripe customers")
print(result.answer)
```

Prefer `connect()` plus `execute()` when you know exactly which entity and action to call. Prefer `ask()` when you want the platform to pick the right operation based on a natural-language request.

## Expose a connector as an agent tool

When you wrap a connector as a tool for an AI agent, the agent needs to know which entities and actions exist, what parameters each takes, and how pagination works. The SDK supports two styles.

### Manual docstrings

Define one tool per operation with a hand-written docstring. Use this when you want to expose a narrow set of operations or need full control over parameters.

```python title="agent.py"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect

agent = Agent("openai:gpt-4o")
github = connect("github")

@agent.tool_plain
async def list_issues(owner: str, repo: str, limit: int = 10) -> str:
    """List open issues in a GitHub repository."""
    result = await github.issues.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
    return str(result.data)
```

The docstring becomes the tool description the LLM sees. Function parameters become the tool's input schema.

### Auto-generated tool descriptions

For broad coverage, use the `tool_utils` decorator on a typed connector. The decorator replaces the wrapped function's docstring with a generated description that includes every entity, action, required and optional parameter, and response shape. The LLM then sees every operation the connector supports with no extra wiring.

```python title="agent.py"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.github import GithubConnector

agent = Agent("openai:gpt-4o")
github = connect("github")

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await github.execute(entity, action, params or {})
```

#### Decorator order matters

The framework decorator (for example, `@agent.tool_plain` or FastMCP's `@mcp.tool`) captures `__doc__` at decoration time. `@Connector.tool_utils` must be the inner decorator so it can rewrite `__doc__` before the framework reads it.

```python title="agent.py"
@agent.tool_plain            # Outer: framework captures __doc__
@GithubConnector.tool_utils  # Inner: rewrites __doc__ first
async def github_execute(entity, action, params=None):
    ...
```

If you reverse the order, the framework captures the original empty docstring and the LLM loses the generated documentation.

#### Custom docstrings

Generated docstrings are almost always the right choice. Override them only when your agent specifically misuses the tool and a custom description fixes it.

:::warning
Custom docstrings can contradict the connector's actual behavior, and they don't update when the connector adds new actions. Prefer generated docstrings unless you have a specific reason not to.
:::

```python title="agent.py"
@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute GitHub operations.

    `entity` must be a simple name such as `issues`, `repositories`, or `pull_requests`.
    `action` must be `list`, `get`, or `search`.
    Pass owner and repo info in the `params` dict, for example:
    `params={"owner": "airbytehq", "repo": "airbyte"}`.
    """
    return await github.execute(entity, action, params or {})
```

## Download files

Some connectors support a `download` action for binary entities like attachments, audio recordings, and documents. Download responses return a byte stream instead of JSON.

Normally, you first list a parent resource to find the file's ID, then download the file. The examples below assume `zendesk_support = connect("zendesk-support")`. Zendesk Support has a generated typed submodule, so `connect()` returns a typed connector here — YAML-only connectors would return a `HostedExecutor` and use the generic `execute(entity, action, params)` API instead.

```python title="agent.py"
zendesk_support = connect("zendesk-support")
comments = await zendesk_support.ticket_comments.list(ticket_id="456")
for comment in comments.data:
    for attachment in comment.attachments or []:
        print(f"Attachment: {attachment['id']} - {attachment['file_name']}")
```

Once you have the attachment ID, stream the file to disk:

```python title="agent.py"
stream = await zendesk_support.attachments.download(attachment_id="12345")
with open("./downloads/ticket_attachment.pdf", "wb") as f:
    async for chunk in stream:
        f.write(chunk)
```

Or use `download_local()` to save a file in one call:

```python title="agent.py"
file_path = await zendesk_support.attachments.download_local(
    attachment_id="12345",
    path="./downloads/ticket_attachment.pdf",
)
```

To see which entities support `download`, check the [connector's reference page](../../connectors).

## Introspection

On typed connectors, you can ask at runtime what the connector supports. These methods are not available on `HostedExecutor`; call `connect()` with a connector that has a generated typed submodule.

`list_entities()` returns every entity, its available actions, and the parameters each action accepts.

```python title="agent.py"
entities = github.list_entities()
for entity in entities:
    print(f"{entity['entity_name']}: {entity['available_actions']}")
    # issues: ['list', 'get']
```

`entity_schema(entity)` returns the JSON schema for records of that entity, or `None` if the connector doesn't ship one for that entity. Always guard the result:

```python title="agent.py"
schema = github.entity_schema("issues")
if schema is None:
    print("No schema available for issues")
else:
    print(list(schema.get("properties", {}).keys()))
```

## Handle errors

Most SDK-owned errors inherit from `AirbyteError`, including `HTTPStatusError` (non-2xx responses from the API) and `AuthenticationError` (invalid or expired credentials). The hosted execution path also propagates raw `httpx` errors unwrapped. Catch both in one place.

```python title="agent.py"
import httpx
from airbyte_agent_sdk import AirbyteError, connect

stripe = connect("stripe")
try:
    result = await stripe.execute("customers", "list", params={"limit": 10})
except (AirbyteError, httpx.HTTPError) as err:
    print(f"Execution failed: {err!r}")
```

For the full exception hierarchy, including `HTTPStatusError` and other SDK-defined subclasses in `airbyte_agent_sdk.http.exceptions`, see the [SDK reference](../../reference/sdk).
