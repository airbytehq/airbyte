# Linkedin-Ads

The Linkedin-Ads agent connector is a Python package that equips AI agents to interact with Linkedin-Ads through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the LinkedIn Ads Marketing API. Provides access to ad accounts, campaigns, campaign groups, creatives, conversions, and ad analytics data. Supports OAuth 2.0 and direct access token authentication. Use this connector to retrieve advertising performance metrics, manage campaign structures, and monitor creative assets across your LinkedIn advertising accounts.


## Example prompts

The Linkedin-Ads connector is optimized to handle prompts like these.

- List all my LinkedIn ad accounts
- Show me all campaigns in my ad account
- List all campaign groups
- Show me the creatives for my campaigns
- List all conversions configured for my ad accounts
- Show me account users for my LinkedIn ads accounts
- Show me campaign analytics for my LinkedIn ad campaigns
- Show me creative analytics for my ad creatives
- Which campaigns have the highest click-through rate?
- What is the total ad spend across all campaigns this month?
- Show me campaigns with status ACTIVE
- Which creatives have the most impressions?
- Compare campaign performance by cost type

## Unsupported prompts

The Linkedin-Ads connector isn't currently able to handle prompts like these.

- Create a new campaign
- Update campaign budgets
- Delete an ad creative
- Pause a campaign

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Create](./REFERENCE.md#accounts-create), [Get](./REFERENCE.md#accounts-get), [Update](./REFERENCE.md#accounts-update), [Delete](./REFERENCE.md#accounts-delete), [Context Store Search](./REFERENCE.md#accounts-context-store-search), [Context Store SQL Query](./REFERENCE.md#accounts-context-store-sql-query) |
| Account Users | [List](./REFERENCE.md#account-users-list), [Update](./REFERENCE.md#account-users-update), [Create](./REFERENCE.md#account-users-create), [Delete](./REFERENCE.md#account-users-delete), [Context Store Search](./REFERENCE.md#account-users-context-store-search), [Context Store SQL Query](./REFERENCE.md#account-users-context-store-sql-query) |
| Campaigns | [List](./REFERENCE.md#campaigns-list), [Create](./REFERENCE.md#campaigns-create), [Get](./REFERENCE.md#campaigns-get), [Update](./REFERENCE.md#campaigns-update), [Delete](./REFERENCE.md#campaigns-delete), [Context Store Search](./REFERENCE.md#campaigns-context-store-search), [Context Store SQL Query](./REFERENCE.md#campaigns-context-store-sql-query) |
| Campaign Groups | [List](./REFERENCE.md#campaign-groups-list), [Create](./REFERENCE.md#campaign-groups-create), [Get](./REFERENCE.md#campaign-groups-get), [Update](./REFERENCE.md#campaign-groups-update), [Delete](./REFERENCE.md#campaign-groups-delete), [Context Store Search](./REFERENCE.md#campaign-groups-context-store-search), [Context Store SQL Query](./REFERENCE.md#campaign-groups-context-store-sql-query) |
| Creatives | [List](./REFERENCE.md#creatives-list), [Create](./REFERENCE.md#creatives-create), [Get](./REFERENCE.md#creatives-get), [Update](./REFERENCE.md#creatives-update), [Delete](./REFERENCE.md#creatives-delete), [Context Store Search](./REFERENCE.md#creatives-context-store-search), [Context Store SQL Query](./REFERENCE.md#creatives-context-store-sql-query) |
| Conversions | [List](./REFERENCE.md#conversions-list), [Create](./REFERENCE.md#conversions-create), [Get](./REFERENCE.md#conversions-get), [Update](./REFERENCE.md#conversions-update), [Context Store Search](./REFERENCE.md#conversions-context-store-search), [Context Store SQL Query](./REFERENCE.md#conversions-context-store-sql-query) |
| Conversion Events | [Create](./REFERENCE.md#conversion-events-create) |
| Campaign Conversions | [Create](./REFERENCE.md#campaign-conversions-create), [Delete](./REFERENCE.md#campaign-conversions-delete) |
| Ad Campaign Analytics | [List](./REFERENCE.md#ad-campaign-analytics-list), [Context Store Search](./REFERENCE.md#ad-campaign-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-campaign-analytics-context-store-sql-query) |
| Ad Creative Analytics | [List](./REFERENCE.md#ad-creative-analytics-list), [Context Store Search](./REFERENCE.md#ad-creative-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-creative-analytics-context-store-sql-query) |
| Ad Impression Device Analytics | [List](./REFERENCE.md#ad-impression-device-analytics-list), [Context Store Search](./REFERENCE.md#ad-impression-device-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-impression-device-analytics-context-store-sql-query) |
| Ad Member Company Analytics | [List](./REFERENCE.md#ad-member-company-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-company-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-company-analytics-context-store-sql-query) |
| Ad Member Company Size Analytics | [List](./REFERENCE.md#ad-member-company-size-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-company-size-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-company-size-analytics-context-store-sql-query) |
| Ad Member Country Analytics | [List](./REFERENCE.md#ad-member-country-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-country-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-country-analytics-context-store-sql-query) |
| Ad Member Industry Analytics | [List](./REFERENCE.md#ad-member-industry-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-industry-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-industry-analytics-context-store-sql-query) |
| Ad Member Job Function Analytics | [List](./REFERENCE.md#ad-member-job-function-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-job-function-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-job-function-analytics-context-store-sql-query) |
| Ad Member Job Title Analytics | [List](./REFERENCE.md#ad-member-job-title-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-job-title-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-job-title-analytics-context-store-sql-query) |
| Ad Member Region Analytics | [List](./REFERENCE.md#ad-member-region-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-region-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-region-analytics-context-store-sql-query) |
| Ad Member Seniority Analytics | [List](./REFERENCE.md#ad-member-seniority-analytics-list), [Context Store Search](./REFERENCE.md#ad-member-seniority-analytics-context-store-search), [Context Store SQL Query](./REFERENCE.md#ad-member-seniority-analytics-context-store-sql-query) |
| Lead Forms | [List](./REFERENCE.md#lead-forms-list), [Context Store Search](./REFERENCE.md#lead-forms-context-store-search), [Context Store SQL Query](./REFERENCE.md#lead-forms-context-store-sql-query) |
| Lead Form Responses | [List](./REFERENCE.md#lead-form-responses-list), [Context Store Search](./REFERENCE.md#lead-form-responses-context-store-search), [Context Store SQL Query](./REFERENCE.md#lead-form-responses-context-store-sql-query) |


## Linkedin-Ads API docs

See the official [Linkedin-Ads API reference](https://learn.microsoft.com/en-us/linkedin/marketing/).

## Interfaces

Use the Linkedin-Ads connector through the Airbyte Agent CLI, the Python SDK, or the API.

### CLI

Install the CLI:

```bash
curl -fsSL https://airbyte.ai/install.sh | bash
```

Authenticate with Airbyte:

```bash
airbyte-agent login
```

Create the connector. The CLI opens the hosted setup flow:

```bash
airbyte-agent connectors create --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "linkedin-ads",
  "entity": "accounts",
  "action": "list"
}'
```

### Python SDK

#### Installation

```bash
uv pip install airbyte-agent-sdk
```

#### Usage

Connectors can run in hosted or open source mode.

##### Hosted

In hosted mode, API credentials are stored securely in Airbyte Agents. You provide your Airbyte credentials instead.
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/get-started/developer-quickstart/).

The `connect()` factory returns a fully typed `LinkedinAdsConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Linkedin-Ads Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

mcp = FastMCP("Linkedin-Ads Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `LinkedinAdsConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="linkedin_ads_inspect",
    docs_tool="linkedin_ads_read_docs",
)
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@LinkedinAdsConnector.agent_tool(framework="pydantic_ai")
async def linkedin_ads_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@LinkedinAdsConnector.agent_tool(framework="pydantic_ai")
async def linkedin_ads_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

@LinkedinAdsConnector.agent_tool(
    inspect_tool="linkedin_ads_inspect",
    docs_tool="linkedin_ads_read_docs",
)
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@LinkedinAdsConnector.agent_tool()
async def linkedin_ads_inspect():
    return await connector.inspect_connector()

@LinkedinAdsConnector.agent_tool()
async def linkedin_ads_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (linkedin_ads_inspect, linkedin_ads_read_docs, linkedin_ads_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `LinkedinAdsConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `LinkedinAdsConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

@tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@LinkedinAdsConnector.tool_utils(framework="openai_agents")
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Linkedin-Ads Assistant", tools=[linkedin_ads_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector

connector = connect("linkedin-ads", workspace_name="<your_workspace_name>")

mcp = FastMCP("Linkedin-Ads Agent")

@mcp.tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Linkedin-Ads Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = LinkedinAdsConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Linkedin-Ads Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

Pass section IDs verbatim as the outline lists them, prefix included (`actions.<entity>.<action>`, not `<entity>.<action>`); anything else returns an error the agent has to recover from.

The builder names its tools `inspect_connector`, `read_skill_docs`, and `execute`, so the tool sets for more than one connector collide when registered on the same agent. Renaming the callables at registration avoids the collision, but the generated `execute` guidance still names `inspect_connector` and `read_skill_docs`, pointing the model at the wrong tools. Use the `agent_tool` pattern below instead: it weaves your own names into that guidance.

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

tools = build_connector_tools(connector, framework="langchain")
langchain_tools = [
    StructuredTool.from_function(
        coroutine=tool,
        name=tool.__name__,
        description=tool.__doc__,
    )
    for tool in tools.as_list()
]
```

**OpenAI Agents**

```python title="OpenAI Agents"
from airbyte_agent_sdk import build_connector_tools
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Linkedin-Ads Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

mcp = FastMCP("Linkedin-Ads Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Custom tool bodies

When you need custom tool bodies — or a framework without native support — use `LinkedinAdsConnector.agent_tool`. Register execute, inspect, and docs together so the agent can fetch connector guidance progressively. Pass the framework explicitly when it has a supported failure strategy:

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.agent_tool(
    framework="pydantic_ai",
    inspect_tool="linkedin_ads_inspect",
    docs_tool="linkedin_ads_read_docs",
)
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@agent.tool_plain
@LinkedinAdsConnector.agent_tool(framework="pydantic_ai")
async def linkedin_ads_inspect():
    return await connector.inspect_connector()

@agent.tool_plain
@LinkedinAdsConnector.agent_tool(framework="pydantic_ai")
async def linkedin_ads_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)
```

Use the same three-function pattern with `framework="langchain"`, `"openai_agents"`, or `"mcp"` and that framework's registration decorator. Each value translates connector failures into the framework's own signal:

| `framework=` | Tool failures surface as |
|--------------|--------------------------|
| `"pydantic_ai"` | `pydantic_ai.ModelRetry` |
| `"langchain"` | `langchain_core.tools.ToolException` (set `handle_tool_error=True` to feed it back to the model) |
| `"openai_agents"` | the failure message returned to the model as the tool result |
| `"mcp"` | `fastmcp.exceptions.ToolError` |
| `"none"` (default) | `airbyte_agent_sdk.AirbyteToolError` |

On a framework the SDK does not support natively — or in a raw LLM dispatch loop — omit `framework=` and handle `AirbyteToolError` yourself:

```python title="No framework"
from airbyte_agent_sdk import AirbyteToolError
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

@LinkedinAdsConnector.agent_tool(
    inspect_tool="linkedin_ads_inspect",
    docs_tool="linkedin_ads_read_docs",
)
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})

@LinkedinAdsConnector.agent_tool()
async def linkedin_ads_inspect():
    return await connector.inspect_connector()

@LinkedinAdsConnector.agent_tool()
async def linkedin_ads_read_docs(section: str | None = None):
    return await connector.read_skill_docs(section)

# Advertise all three to the model, using each function's docstring as its description.
handlers = {
    fn.__name__: fn
    for fn in (linkedin_ads_inspect, linkedin_ads_read_docs, linkedin_ads_execute)
}

# `tool_name` and `tool_args` come from the model's tool call in your dispatch loop.
try:
    tool_result = await handlers[tool_name](**tool_args)
except AirbyteToolError as err:
    tool_result = str(err)  # hand the message back to the model as an errored tool result
```

Each function's docstring carries the guidance the model needs, so pass it through as the tool description wherever you register it.

###### Legacy alternatives

These examples are kept for existing integrations. The deprecated `LinkedinAdsConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand. For new code, use `build_connector_tools` or `LinkedinAdsConnector.agent_tool` above.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

@tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@LinkedinAdsConnector.tool_utils(framework="openai_agents")
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Linkedin-Ads Assistant", tools=[linkedin_ads_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.linkedin_ads import LinkedinAdsConnector
from airbyte_agent_sdk.connectors.linkedin_ads.models import LinkedinAdsAccessTokenAuthenticationAuthConfig

connector = LinkedinAdsConnector(
    auth_config=LinkedinAdsAccessTokenAuthenticationAuthConfig(
        access_token="<The access token generated for your developer application>"
    )
)

mcp = FastMCP("Linkedin-Ads Agent")

@mcp.tool
@LinkedinAdsConnector.tool_utils
async def linkedin_ads_execute(entity: str, action: str, params: dict | None = None):
    """Execute Linkedin-Ads connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.2.0