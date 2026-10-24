---
sidebar_position: 1
sidebar_label: Internal use cases
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Implementation guide: Internal use cases

This guide walks you through building a production-ready agent that connects to your organization's data. You control the credentials, and your agent operates on behalf of your team or company.

## Overview

This guide is for teams building agents for internal use: support bots, operations agents, research assistants, or any agent that works with your organization's own data. By the end of this guide, you'll have:

- Multiple connectors registered as tools in your agent
- Credentials stored securely in Agent Engine (not your infrastructure)
- The context store enabled for low-latency search
- A production-ready architecture you can extend

This guide assumes you've completed a [quick start](../quickstarts/) and have basic knowledge of connectors, entities, and actions. You're working from an existing project, not starting from scratch.

## Prerequisites

- An [Agent Engine account](https://app.airbyte.ai/) with your client ID and client secret (find these under **Authentication Module** > **Installation**)
- API credentials for the services you want to connect (for example, a GitHub personal access token and a Slack bot token)
- Python 3.13+ and [uv](https://github.com/astral-sh/uv)
- An LLM provider API key (for example, [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com/))

## Architecture

For internal use cases, the architecture is straightforward: your agent uses Airbyte connectors to interact with third-party APIs, and Agent Engine manages the credentials and execution.

```text
┌─────────────┐      ┌─────────────────┐      ┌──────────────┐
│  Your agent  │─────▶│  Agent Engine    │─────▶│ Third-party  │
│  (Python)    │      │  (credentials,  │      │ APIs (GitHub,│
│              │◀─────│   execution)    │◀─────│ Slack, etc.) │
└─────────────┘      └─────────────────┘      └──────────────┘
```

**Use hosted mode for production.** Even for internal use, hosted mode is the right choice. Agent Engine manages credential lifecycle (including token refresh), provides the context store for low-latency search, and means you don't store third-party secrets in your own infrastructure. Open source mode is appropriate for local development and testing.

## Step 1: Install connector packages

Install the connector packages for the services you want to connect. This guide uses GitHub and Slack as examples, but you can substitute any connectors from the [catalog](/ai-agents/connectors/).

```bash
uv add airbyte-agent-github airbyte-agent-slack
```

You also need your agent framework and LLM provider. If you don't already have these in your project:

```bash
uv add pydantic-ai  # or langchain langchain-openai langgraph
```

## Step 2: Enable connectors in Agent Engine

Before you can use connectors in hosted mode, enable them in your Agent Engine organization. This tells Agent Engine which data sources your agents can access.

### With the UI

1. Log in to [Agent Engine](https://app.airbyte.ai/).
2. Click **Connectors** > **Manage Connectors** (or **Enable Connector**).
3. Search for and enable each connector you need (for example, GitHub and Slack).
4. For each connector, check **Direct** to enable real-time agent queries.

### With the API

You can automate this with the API. First, get an application token:

```bash
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

Then list available connector definitions to find the `sourceDefinitionId` for each connector:

```bash
curl 'https://api.airbyte.ai/api/v1/integrations/definitions/sources?name=github' \
  -H 'Authorization: Bearer <application_token>'
```

Create a source template for each connector:

```bash
curl -X POST https://api.airbyte.ai/api/v1/integrations/templates/sources \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "organization_id": "<your_organization_id>",
    "actor_definition_id": "<source_definition_id>",
    "partial_default_config": {}
  }'
```

## Step 3: Create a customer and store credentials

Even with a single user, you need a customer in Agent Engine. A customer is an isolated environment that holds connectors and credentials. For internal use, create one customer that represents your organization or use case.

**Best practice:** Use a meaningful name like `internal-ops`, `support-bot`, or your company name. This makes it easy to identify in the Agent Engine UI.

### Get a scoped token

Generate a scoped token for your customer. If the customer doesn't exist, Agent Engine creates it automatically.

```bash
# First, get an application token (if you don't already have one)
curl -X POST https://api.airbyte.ai/api/v1/account/applications/token \
  -H 'Content-Type: application/json' \
  -d '{
    "client_id": "<your_client_id>",
    "client_secret": "<your_client_secret>"
  }'
```

```bash
# Then, generate a scoped token for your customer
curl -X POST https://api.airbyte.ai/api/v1/account/applications/scoped-token \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "customer_name": "internal-ops"
  }'
```

### Create connectors with your credentials

Create a connector for each service you want to access. This stores your API credentials securely in Agent Engine.

```bash title="Create a GitHub connector"
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "connector_type": "github",
    "customer_name": "internal-ops",
    "replication_config": {
      "repositories": ["your-org/your-repo"],
      "credentials": {
        "option_title": "PAT Credentials",
        "personal_access_token": "<your_github_token>"
      }
    }
  }'
```

```bash title="Create a Slack connector"
curl -X POST https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <scoped_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "connector_type": "slack",
    "customer_name": "internal-ops",
    "replication_config": {
      "credentials": {
        "option_title": "API Token",
        "api_token": "<your_slack_bot_token>"
      }
    }
  }'
```

You only need to do this once per connector. After creation, your connectors persist in Agent Engine and your agent authenticates using your Airbyte credentials, not the third-party tokens.

## Step 4: Connect your agent to connectors

Now connect your agent to the connectors you created. In hosted mode, you provide your Airbyte credentials instead of third-party API keys. The SDK handles token exchange and refresh automatically.

### Configure environment variables

Add your Airbyte credentials and LLM key to your `.env` file:

```text title=".env"
AIRBYTE_CLIENT_ID=your-airbyte-client-id
AIRBYTE_CLIENT_SECRET=your-airbyte-client-secret
AIRBYTE_CUSTOMER_NAME=internal-ops
OPENAI_API_KEY=your-openai-api-key
```

:::warning
Never commit your `.env` file to version control. Add it to `.gitignore`.
:::

### Initialize connectors and register tools

<Tabs>
<TabItem value="python" label="Python" default>

```python title="agent.py"
import os
from dotenv import load_dotenv
from pydantic_ai import Agent

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_slack import SlackConnector

load_dotenv()

# Shared Airbyte credentials for hosted mode
airbyte_config = AirbyteAuthConfig(
    customer_name=os.environ["AIRBYTE_CUSTOMER_NAME"],
    airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
    airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
)

# Initialize connectors — both use the same Airbyte credentials
github = GithubConnector(auth_config=airbyte_config)
slack = SlackConnector(auth_config=airbyte_config)

agent = Agent(
    "openai:gpt-4o",
    system_prompt=(
        "You are an internal operations assistant. Use the GitHub and Slack "
        "tools to answer questions about repositories, issues, pull requests, "
        "channels, and messages."
    ),
)

@agent.tool_plain
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None):
    return await github.execute(entity, action, params or {})

@agent.tool_plain
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None):
    return await slack.execute(entity, action, params or {})
```

</TabItem>
<TabItem value="langchain" label="LangChain">

```python title="agent.py"
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_slack import SlackConnector

load_dotenv()

airbyte_config = AirbyteAuthConfig(
    customer_name=os.environ["AIRBYTE_CUSTOMER_NAME"],
    airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
    airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
)

github = GithubConnector(auth_config=airbyte_config)
slack = SlackConnector(auth_config=airbyte_config)

@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute GitHub connector operations."""
    result = await github.execute(entity, action, params or {})
    return json.dumps(result, default=str)

@tool
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Slack connector operations."""
    result = await slack.execute(entity, action, params or {})
    return json.dumps(result, default=str)

llm = ChatOpenAI(model="gpt-4o")
agent = create_react_agent(llm, [github_execute, slack_execute])
```

</TabItem>
<TabItem value="fastmcp" label="FastMCP">

```python title="server.py"
import os
import json
from dotenv import load_dotenv
from fastmcp import FastMCP

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_slack import SlackConnector

load_dotenv()

airbyte_config = AirbyteAuthConfig(
    customer_name=os.environ["AIRBYTE_CUSTOMER_NAME"],
    airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
    airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
)

github = GithubConnector(auth_config=airbyte_config)
slack = SlackConnector(auth_config=airbyte_config)

mcp = FastMCP("Internal Ops Agent")

@mcp.tool()
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute GitHub connector operations."""
    result = await github.execute(entity, action, params or {})
    return json.dumps(result, default=str)

@mcp.tool()
@SlackConnector.tool_utils
async def slack_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute Slack connector operations."""
    result = await slack.execute(entity, action, params or {})
    return json.dumps(result, default=str)

if __name__ == "__main__":
    mcp.run()
```

</TabItem>
<TabItem value="api" label="API">

If you're not using Python, execute operations directly via the API. First, list your connectors to get connector IDs:

```bash
curl https://api.airbyte.ai/api/v1/integrations/connectors \
  -H 'Authorization: Bearer <application_token>'
```

Then execute operations against a specific connector:

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "entity": "issues",
    "action": "list",
    "params": {
      "owner": "your-org",
      "repo": "your-repo"
    }
  }'
```

</TabItem>
</Tabs>

**Why `@Connector.tool_utils`?** This decorator auto-generates a comprehensive tool description from the connector's metadata, including all available entities, actions, parameters, and response structures. The LLM uses this description to decide which tool to call and how to call it. Use auto-generated descriptions unless the LLM demonstrably misuses a tool because of them.

**Decorator order matters.** The `@Connector.tool_utils` decorator must be the inner decorator (closest to the function). The framework decorator (`@agent.tool_plain`, `@tool`, `@mcp.tool()`) must be the outer decorator. This is because frameworks capture docstrings at decoration time, and `tool_utils` needs to set the docstring before the framework sees it.

## Step 5: Scale to more connectors with dependency injection

As you add more connectors, managing them as module-level variables gets unwieldy. Use dependency injection to keep your code clean and testable.

This pattern is especially useful when:

- You have three or more connectors
- You want to test tools with mock connectors
- Different parts of your application need different connector configurations

<Tabs>
<TabItem value="python" label="Python" default>

```python title="agent.py"
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_hubspot import HubspotConnector
from airbyte_agent_slack import SlackConnector

load_dotenv()

@dataclass
class AgentDeps:
    github: GithubConnector
    hubspot: HubspotConnector
    slack: SlackConnector

def create_deps() -> AgentDeps:
    """Create connectors with shared Airbyte credentials."""
    config = AirbyteAuthConfig(
        customer_name=os.environ["AIRBYTE_CUSTOMER_NAME"],
        airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
        airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
    )
    return AgentDeps(
        github=GithubConnector(auth_config=config),
        hubspot=HubspotConnector(auth_config=config),
        slack=SlackConnector(auth_config=config),
    )

agent = Agent(
    "openai:gpt-4o",
    deps_type=AgentDeps,
    system_prompt=(
        "You are an internal operations assistant with access to GitHub, "
        "HubSpot, and Slack. Use the appropriate tool for each question."
    ),
)

@agent.tool
@GithubConnector.tool_utils
async def github_execute(
    ctx: RunContext[AgentDeps], entity: str, action: str, params: dict | None = None
):
    return await ctx.deps.github.execute(entity, action, params or {})

@agent.tool
@HubspotConnector.tool_utils
async def hubspot_execute(
    ctx: RunContext[AgentDeps], entity: str, action: str, params: dict | None = None
):
    return await ctx.deps.hubspot.execute(entity, action, params or {})

@agent.tool
@SlackConnector.tool_utils
async def slack_execute(
    ctx: RunContext[AgentDeps], entity: str, action: str, params: dict | None = None
):
    return await ctx.deps.slack.execute(entity, action, params or {})
```

```python title="main.py"
import asyncio
from agent import agent, create_deps

async def main():
    deps = create_deps()
    result = await agent.run(
        "What are the 5 most recent open issues in our repo?",
        deps=deps,
    )
    print(result.output)

if __name__ == "__main__":
    asyncio.run(main())
```

</TabItem>
<TabItem value="langchain" label="LangChain">

With LangChain, use a factory function to create tools with shared configuration:

```python title="tools.py"
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool

from airbyte_agent_github import GithubConnector, AirbyteAuthConfig
from airbyte_agent_hubspot import HubspotConnector
from airbyte_agent_slack import SlackConnector

load_dotenv()

def create_tools():
    """Create all connector tools with shared Airbyte credentials."""
    config = AirbyteAuthConfig(
        customer_name=os.environ["AIRBYTE_CUSTOMER_NAME"],
        airbyte_client_id=os.environ["AIRBYTE_CLIENT_ID"],
        airbyte_client_secret=os.environ["AIRBYTE_CLIENT_SECRET"],
    )

    github = GithubConnector(auth_config=config)
    hubspot = HubspotConnector(auth_config=config)
    slack = SlackConnector(auth_config=config)

    @tool
    @GithubConnector.tool_utils
    async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
        """Execute GitHub connector operations."""
        result = await github.execute(entity, action, params or {})
        return json.dumps(result, default=str)

    @tool
    @HubspotConnector.tool_utils
    async def hubspot_execute(entity: str, action: str, params: dict | None = None) -> str:
        """Execute HubSpot connector operations."""
        result = await hubspot.execute(entity, action, params or {})
        return json.dumps(result, default=str)

    @tool
    @SlackConnector.tool_utils
    async def slack_execute(entity: str, action: str, params: dict | None = None) -> str:
        """Execute Slack connector operations."""
        result = await slack.execute(entity, action, params or {})
        return json.dumps(result, default=str)

    return [github_execute, hubspot_execute, slack_execute]
```

```python title="agent.py"
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from tools import create_tools

llm = ChatOpenAI(model="gpt-4o")
tools = create_tools()
agent = create_react_agent(llm, tools)
```

</TabItem>
</Tabs>

## Step 6: Enable the context store

The [context store](/ai-agents/platform/context-store) makes a subset of your data available in Airbyte-managed storage, enabling low-latency search operations. Without it, search queries require your agent to paginate through lists, growing the context window and hitting rate limits.

**Enable the context store if your agent needs to search or filter data.** If your agent only needs direct lookups (`get` by ID, `list`), you can skip this.

1. In Agent Engine, click **Connectors**.
2. Enable **Enable Airbyte-managed Context Store for agent search**.

After enabling, Airbyte populates the store from your connected sources. This takes time depending on data volume. Once populated, your connectors automatically gain a `search` action:

<Tabs>
<TabItem value="python" label="Python" default>

```python
# The search action is available automatically after enabling the context store.
# Your agent can use it through the same tool interface.
result = await github.execute("issues", "search", {
    "query": {"filter": {"eq": {"state": "open"}}},
    "limit": 10
})
```

</TabItem>
<TabItem value="api" label="API">

```bash
curl -X POST 'https://api.airbyte.ai/api/v1/integrations/connectors/<connector_id>/execute' \
  -H 'Authorization: Bearer <application_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "entity": "issues",
    "action": "search",
    "params": {
      "query": {"filter": {"eq": {"state": "open"}}},
      "limit": 10
    }
  }'
```

</TabItem>
</Tabs>

You don't need to change your tool registration. The `@Connector.tool_utils` decorator automatically includes the `search` action in the generated tool description when it's available.

## Step 7: Go to production

### Secure your credentials

In development, a `.env` file is fine. In production, use a secrets manager (like AWS Secrets Manager, HashiCorp Vault, or your platform's equivalent) to store your Airbyte client ID and client secret. Your third-party API credentials are already secured in Agent Engine.

### Handle token expiration

- **Python SDK**: Token refresh is automatic. The SDK handles it transparently during normal operation.
- **API**: Application tokens expire after 15 minutes. Scoped tokens expire after 20 minutes. Your backend must request new tokens before they expire.

### Error handling

Wrap connector operations in error handling. Connectors can fail due to rate limiting, expired credentials, or API outages.

```python
async def safe_execute(connector, entity, action, params=None):
    try:
        return await connector.execute(entity, action, params or {})
    except Exception as e:
        return {"error": str(e), "entity": entity, "action": action}
```

### Observability

For production agents, add tracing to monitor tool calls and agent behavior. The [agent-engine-samples](https://github.com/airbytehq/agent-engine-samples) repository demonstrates integration with LangSmith for tracing.

## Best practices summary

- **Use hosted mode for production.** Open source mode is for development and testing.
- **Use auto-generated tool descriptions.** Override only when the LLM demonstrably misuses a tool.
- **Create one customer per logical scope.** For internal use, a single customer like `internal-ops` is usually sufficient.
- **Start with direct mode.** Add replication only when you have a concrete need.
- **Enable the context store for search.** If your agent filters or searches data, the context store reduces latency and token usage significantly.
- **Use dependency injection for multi-connector agents.** It keeps code organized and testable as you scale.

## Next steps

- Browse the [connector catalog](/ai-agents/connectors/) to find more data sources for your agent.
- Learn about [executing operations](/ai-agents/platform/execute) for detailed coverage of entities, actions, and pagination.
- Explore the [context store](/ai-agents/platform/context-store) for search-heavy workloads.
