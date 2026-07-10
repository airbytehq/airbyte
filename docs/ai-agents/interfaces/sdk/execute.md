---
plan: all
sidebar_position: 3
---

# Execute operations

Once you've added a connector to your workspace, you can run operations against it from Python. The SDK offers direct execution and patterns for exposing a connector as a tool to an AI agent framework.

## Direct execution

The `connect()` factory takes a connector slug and returns an execution object. Call its `execute(entity, action, params)` method to run an operation. When your workspace has exactly one connector of a given type, you don't need to pass a `connector_id`. The SDK resolves the connector by its slug automatically.

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
- `action` is one of the connector's supported actions, such as `list` or `get`. Some connectors support additional actions like `context_store_search`, `api_search`, or `download`; check the connector's reference page.
- `params` contains action-specific arguments. The exact keys are connector- and entity-specific. GitHub's `issues.list` accepts `per_page`, for example, while other connectors paginate via `cursor`. Use [`list_entities()`](#introspection) to discover the parameters a connector supports at runtime.
- Always wrap the call in `try`/`finally` and `await connector.close()` once you're done to release the underlying HTTP client.

See the connector's page in the [Connectors](../../connectors) reference for the entities and actions it supports.

### Typed connectors and `HostedExecutor`

For connectors with a generated typed submodule, `connect()` returns a typed connector with IDE autocompletion, method-level docstrings, and structured call shortcuts. For example: `await hubspot.contacts.list(limit=10)`. The [agent connectors](../../connectors) page lists every connector; the **Slug** column is the string to pass to `connect()`.

For every other connector in the bundled registry, `connect()` returns a generic `HostedExecutor` with the same `execute(entity, action, params)` method but without typed shortcuts. The execution behavior is otherwise identical.

`connect()` raises `ValueError` if the slug isn't in the bundled registry (the message lists every supported slug) or if no Airbyte credentials are available. It does *not* raise when a typed submodule is missing. YAML-only connectors return a `HostedExecutor`.

### Multiple connectors of the same type

If your workspace has more than one connector of a given type (for example, two separate Stripe accounts), slug resolution is ambiguous. Pass an explicit `connector_id` to `connect()` so the SDK knows which one to target:

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

## Expose a connector as an agent tool

When you wrap a connector as a tool for an AI agent, the agent needs to know which entities and actions exist, what parameters each takes, and how pagination works. The recommended pattern is `build_connector_tools`, which binds ready-to-use tools that let the agent read just-in-time skill docs before it executes.

### Recommended: build_connector_tools

`build_connector_tools(connector)` returns a `ConnectorTools` object with three callables bound to one connector: `inspect_connector`, `read_skill_docs`, and `execute`. Pass `framework=` so runtime errors surface as that framework's retry signal, then register all three with `tools.as_list()`.

```python title="agent.py"
from pydantic_ai import Agent
from airbyte_agent_sdk import build_connector_tools, connect

github = connect("github")
tools = build_connector_tools(github, framework="pydantic_ai")

agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

Instead of packing the whole connector schema into one static tool description, the agent works through a progressive introspection flow:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

- `inspect_connector()` returns the connector's hosted metadata and Context Store readiness, and resolves the skill-doc ID the other tools use.
- `read_skill_docs()` with no section returns the outline and general guidance. `read_skill_docs(section="<id>")` returns the exact entity and action guidance the agent needs before it executes.
- `execute(entity, action, params)` runs the operation.

The SDK binds the skill-doc ID internally, so the model only passes an optional `section`. This keeps the agent's context small: it reads the outline, drills into the one section it needs, then executes, instead of loading every entity and action up front. Skill docs are served by Airbyte from the same connector definition the SDK is generated from, so they stay in sync with the connector.

`connect("github")` returns a typed connector when a generated submodule exists, but `build_connector_tools` also accepts a generic `HostedExecutor` for YAML-only connectors. Either works with the same three tools.

:::note
Skill docs are hosted by Airbyte and served by the platform. If you point the SDK at a connector running in open source mode (no hosted backend), `build_connector_tools` still returns the same three tools, but `inspect_connector` reports `"mode": "local"` and `read_skill_docs` falls back to the connector's generated (YAML-derived) description instead of hosted section docs. `execute` still runs directly against the connector.
:::

To expose only `execute` with a single generated description instead of the progressive flow, pass `use_progressive_docs=False`. `tools.as_list()` then returns just the `execute` tool.

#### Other frameworks

`tools.as_list()` returns plain async callables, so you can register them with any framework. Set `framework=` to match.

LangChain wraps each callable as a `StructuredTool`:

```python title="agent.py"
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import build_connector_tools, connect

github = connect("github")
tools = build_connector_tools(github, framework="langchain")

lc_tools = [
    StructuredTool.from_function(coroutine=tool, name=tool.__name__, description=tool.__doc__)
    for tool in tools.as_list()
]
```

:::note
LangChain 1.x re-raises tool errors by default, so a wrong `read_skill_docs` section guess aborts the run before the agent can self-correct from the returned outline. To let the agent recover, add the `wrap_tool_call` middleware shown in [Surface tool errors back to the model](../../get-started/developer-quickstart/tutorial-langchain#surface-tool-errors-back-to-the-model) in the LangChain quickstart.
:::

FastMCP registers each callable as a tool:

```python title="server.py"
from fastmcp import FastMCP
from airbyte_agent_sdk import build_connector_tools, connect

mcp = FastMCP("github-tools")
github = connect("github")

for tool in build_connector_tools(github, framework="mcp").as_list():
    mcp.tool(tool)
```

### Alternatives

The decorator patterns below predate `build_connector_tools`. They bind a single `execute` tool with the connector's full catalog baked into the description up front, rather than letting the agent read skill docs on demand. Prefer `build_connector_tools` for new agents. Reach for these when you want to expose a narrow set of operations, need full control over the tool description, or run a local connector without hosted skill docs.

#### Manual docstrings

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

#### Auto-generated tool descriptions

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

##### Decorator order matters

The framework decorator (for example, `@agent.tool_plain` or FastMCP's `@mcp.tool`) captures `__doc__` at decoration time. `@Connector.tool_utils` must be the inner decorator so it can rewrite `__doc__` before the framework reads it.

```python title="agent.py"
@agent.tool_plain            # Outer: framework captures __doc__
@GithubConnector.tool_utils  # Inner: rewrites __doc__ first
async def github_execute(entity, action, params=None):
    ...
```

If you reverse the order, the framework captures the original empty docstring and the LLM loses the generated documentation.

##### Custom docstrings

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
    `action` must be `list`, `get`, or `context_store_search`.
    Pass owner and repo info in the `params` dict, for example:
    `params={"owner": "airbytehq", "repo": "airbyte"}`.
    """
    return await github.execute(entity, action, params or {})
```

## Download files

Some connectors support a `download` action for binary entities like attachments, audio recordings, and documents. Download responses return a byte stream instead of JSON.

Normally, you first list a parent resource to find the file's ID, then download the file. The examples below assume `zendesk_support = connect("zendesk-support")`. Zendesk Support has a generated typed submodule, so `connect()` returns a typed connector here. YAML-only connectors would return a `HostedExecutor` and use the generic `execute(entity, action, params)` API instead.

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
