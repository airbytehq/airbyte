# Orb

The Orb agent connector is a Python package that equips AI agents to interact with Orb through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Orb is a usage-based billing platform that enables businesses to implement flexible pricing models,
track customer usage, and manage subscriptions. This connector provides access to customers,
subscriptions, plans, and invoices for billing analytics and customer management.


## Example prompts

The Orb connector is optimized to handle prompts like these.

- Show me all my customers in Orb
- List all active subscriptions
- What plans are available?
- Show me recent invoices
- Show me details for a recent customer
- What is the status of a recent subscription?
- Show me the pricing details for a plan
- Confirm the Stripe ID linked to a customer
- What is the payment provider ID for a customer?
- List all invoices for a specific customer
- List all subscriptions for customer XYZ
- Show all active subscriptions for a specific customer
- What subscriptions does customer \{external_customer_id\} have?
- Pull all invoices from the last month
- Show invoices created after \{date\}
- List all paid invoices for customer \{customer_id\}
- What invoices are in draft status?
- Show all issued invoices for subscription \{subscription_id\}

## Unsupported prompts

The Orb connector isn't currently able to handle prompts like these.

- Create a new customer in Orb
- Update subscription details
- Delete a customer record
- Send an invoice to a customer
- Filter subscriptions by plan name (must filter client-side after listing)
- Pull customers billed for specific products (must examine invoice line_items client-side)

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Customers | [List](./REFERENCE.md#customers-list), [Get](./REFERENCE.md#customers-get), [Context Store Search](./REFERENCE.md#customers-context-store-search) |
| Subscriptions | [List](./REFERENCE.md#subscriptions-list), [Get](./REFERENCE.md#subscriptions-get), [Context Store Search](./REFERENCE.md#subscriptions-context-store-search) |
| Plans | [List](./REFERENCE.md#plans-list), [Get](./REFERENCE.md#plans-get), [Context Store Search](./REFERENCE.md#plans-context-store-search) |
| Invoices | [List](./REFERENCE.md#invoices-list), [Get](./REFERENCE.md#invoices-get), [Context Store Search](./REFERENCE.md#invoices-context-store-search) |


## Orb API docs

See the official [Orb API reference](https://docs.withorb.com/api-reference).

## SDK installation

```bash
uv pip install airbyte-agent-sdk
```

## SDK usage

Connectors can run in hosted or open source mode.

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `OrbConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.orb import OrbConnector

connector = connect("orb", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.orb import OrbConnector

connector = connect("orb", workspace_name="<your_workspace_name>")

@tool
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.orb import OrbConnector

connector = connect("orb", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@OrbConnector.tool_utils(framework="openai_agents")
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Orb Assistant", tools=[orb_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.orb import OrbConnector

connector = connect("orb", workspace_name="<your_workspace_name>")

mcp = FastMCP("Orb Agent")

@mcp.tool
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OrbConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OrbConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@tool
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OrbConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@OrbConnector.tool_utils(framework="openai_agents")
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Orb Assistant", tools=[orb_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = OrbConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Orb Agent")

@mcp.tool
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

### Open source

In open source mode, you provide API credentials directly to the connector.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.connectors.orb.models import OrbAuthConfig

connector = OrbConnector(
    auth_config=OrbAuthConfig(
        api_key="<Your Orb API key>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.connectors.orb.models import OrbAuthConfig

connector = OrbConnector(
    auth_config=OrbAuthConfig(
        api_key="<Your Orb API key>"
    )
)

@tool
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.connectors.orb.models import OrbAuthConfig

connector = OrbConnector(
    auth_config=OrbAuthConfig(
        api_key="<Your Orb API key>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@OrbConnector.tool_utils(framework="openai_agents")
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Orb Assistant", tools=[orb_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.orb import OrbConnector
from airbyte_agent_sdk.connectors.orb.models import OrbAuthConfig

connector = OrbConnector(
    auth_config=OrbAuthConfig(
        api_key="<Your Orb API key>"
    )
)

mcp = FastMCP("Orb Agent")

@mcp.tool
@OrbConnector.tool_utils
async def orb_execute(entity: str, action: str, params: dict | None = None):
    """Execute Orb connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## Version information

**Connector version:** 0.1.8
