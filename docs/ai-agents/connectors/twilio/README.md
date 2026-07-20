# Twilio

The Twilio agent connector is a Python package that equips AI agents to interact with Twilio through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Twilio REST API. Provides read and write access to core Twilio resources including accounts, calls, messages, recordings, conferences, incoming phone numbers, usage records, addresses, queues, transcriptions, and outgoing caller IDs. Write operations include sending SMS/MMS messages, placing outbound calls, and provisioning phone numbers. Uses HTTP Basic authentication with Account SID and Auth Token.


## Example prompts

The Twilio connector is optimized to handle prompts like these.

- List all calls from the last 7 days
- Show me recent inbound SMS messages
- List all active phone numbers on my account
- Show me details for a specific call
- List all recordings
- Show me conference calls
- List usage records for my account
- Show me all queues
- List outgoing caller IDs
- Show me addresses on my account
- List transcriptions
- Send an SMS message to +15558675310 saying 'Hello from Twilio!'
- Place an outbound call to +15558675310 with the message 'Your appointment is confirmed'
- Provision a new phone number with area code 415
- Send a WhatsApp message to +15558675310
- Send an MMS with an image to +15558675310
- What are my top 10 most expensive calls this month?
- How many SMS messages did I send vs receive in the last 30 days?
- Summarize my usage costs by category
- Which phone numbers have the most incoming calls?
- Show me all failed messages and their error codes
- What is the average call duration for outbound calls?

## Unsupported prompts

The Twilio connector isn't currently able to handle prompts like these.

- Delete a recording
- Delete a phone number
- Delete a message
- Create a new queue

## Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Accounts | [List](./REFERENCE.md#accounts-list), [Get](./REFERENCE.md#accounts-get), [Context Store Search](./REFERENCE.md#accounts-context-store-search) |
| Calls | [List](./REFERENCE.md#calls-list), [Create](./REFERENCE.md#calls-create), [Get](./REFERENCE.md#calls-get), [Context Store Search](./REFERENCE.md#calls-context-store-search) |
| Messages | [List](./REFERENCE.md#messages-list), [Create](./REFERENCE.md#messages-create), [Get](./REFERENCE.md#messages-get), [Context Store Search](./REFERENCE.md#messages-context-store-search) |
| Incoming Phone Numbers | [List](./REFERENCE.md#incoming-phone-numbers-list), [Create](./REFERENCE.md#incoming-phone-numbers-create), [Get](./REFERENCE.md#incoming-phone-numbers-get), [Context Store Search](./REFERENCE.md#incoming-phone-numbers-context-store-search) |
| Recordings | [List](./REFERENCE.md#recordings-list), [Get](./REFERENCE.md#recordings-get), [Context Store Search](./REFERENCE.md#recordings-context-store-search) |
| Conferences | [List](./REFERENCE.md#conferences-list), [Get](./REFERENCE.md#conferences-get), [Context Store Search](./REFERENCE.md#conferences-context-store-search) |
| Usage Records | [List](./REFERENCE.md#usage-records-list), [Context Store Search](./REFERENCE.md#usage-records-context-store-search) |
| Addresses | [List](./REFERENCE.md#addresses-list), [Get](./REFERENCE.md#addresses-get), [Context Store Search](./REFERENCE.md#addresses-context-store-search) |
| Queues | [List](./REFERENCE.md#queues-list), [Get](./REFERENCE.md#queues-get), [Context Store Search](./REFERENCE.md#queues-context-store-search) |
| Transcriptions | [List](./REFERENCE.md#transcriptions-list), [Get](./REFERENCE.md#transcriptions-get), [Context Store Search](./REFERENCE.md#transcriptions-context-store-search) |
| Outgoing Caller Ids | [List](./REFERENCE.md#outgoing-caller-ids-list), [Get](./REFERENCE.md#outgoing-caller-ids-get), [Context Store Search](./REFERENCE.md#outgoing-caller-ids-context-store-search) |


## Twilio API docs

See the official [Twilio API reference](https://www.twilio.com/docs/usage/api).

## Interfaces

Use the Twilio connector through the Airbyte Agent CLI, the Python SDK, or the API.

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
  "name": "twilio"
}'
```

Describe the connector to see its supported entities and actions:

```bash
airbyte-agent connectors describe --json '{
  "workspace": "<your_workspace_name>",
  "name": "twilio"
}'
```

Execute an action:

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "twilio",
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

The `connect()` factory returns a fully typed `TwilioConnector` and reads `AIRBYTE_CLIENT_ID` / `AIRBYTE_CLIENT_SECRET` from the environment:


The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

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
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Twilio Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

mcp = FastMCP("Twilio Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `TwilioConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

@tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TwilioConnector.tool_utils(framework="openai_agents")
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Twilio Assistant", tools=[twilio_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk import connect
from airbyte_agent_sdk.connectors.twilio import TwilioConnector

connector = connect("twilio", workspace_name="<your_workspace_name>")

mcp = FastMCP("Twilio Agent")

@mcp.tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


Or pass credentials explicitly (equivalent, useful when you're not loading them from the environment):


**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
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
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
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
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Twilio Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.types import AirbyteAuthConfig

connector = TwilioConnector(
    auth_config=AirbyteAuthConfig(
        workspace_name="<your_workspace_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

mcp = FastMCP("Twilio Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```


##### Open source

In open source mode, you provide API credentials directly to the connector.

The recommended pattern is `build_connector_tools`, which gives the agent three tools bound to this connector: `inspect_connector`, `read_skill_docs`, and `execute`. The agent can inspect the connector, read only the skill-doc section it needs, and then execute:

```text
inspect_connector() -> read_skill_docs() -> read_skill_docs(section="...") -> execute(entity, action, params)
```

**Pydantic AI**

```python title="Pydantic AI"
from airbyte_agent_sdk import build_connector_tools
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

tools = build_connector_tools(connector, framework="pydantic_ai")
agent = Agent("openai:gpt-4o", tools=tools.as_list())
```

**LangChain**

```python title="LangChain"
from airbyte_agent_sdk import build_connector_tools
from langchain_core.tools import StructuredTool
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
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
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

tools = build_connector_tools(connector, framework="openai_agents")
openai_tools = [function_tool(tool, strict_mode=False) for tool in tools.as_list()]

agent = Agent(name="Twilio Assistant", tools=openai_tools)
```

**FastMCP**

```python title="FastMCP"
from airbyte_agent_sdk import build_connector_tools
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

mcp = FastMCP("Twilio Agent")

for tool in build_connector_tools(connector, framework="mcp").as_list():
    mcp.tool(tool)
```

###### Legacy alternatives

These examples are kept for existing integrations. For new agents, use `build_connector_tools` above. The legacy `TwilioConnector.tool_utils` pattern loads the connector's full generated catalog into one broad `execute` tool description instead of letting the agent read skill docs on demand.

**Pydantic AI**

```python title="Pydantic AI"
from pydantic_ai import Agent
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

agent = Agent("openai:gpt-4o")

@agent.tool_plain
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

**LangChain**

```python title="LangChain"
from langchain_core.tools import tool
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

@tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    # connector.execute returns a Pydantic envelope for typed actions; fall back to raw data otherwise.
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```

**OpenAI Agents**

```python title="OpenAI Agents"
from agents import Agent, function_tool
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

# strict_mode=False because `params: dict` is permissive and the default strict
# JSON schema rejects objects with additionalProperties.
@function_tool(strict_mode=False)
@TwilioConnector.tool_utils(framework="openai_agents")
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result

agent = Agent(name="Twilio Assistant", tools=[twilio_execute])
```

**FastMCP**

```python title="FastMCP"
from fastmcp import FastMCP
from airbyte_agent_sdk.connectors.twilio import TwilioConnector
from airbyte_agent_sdk.connectors.twilio.models import TwilioAuthConfig

connector = TwilioConnector(
    auth_config=TwilioAuthConfig(
        account_sid="<Your Twilio Account SID (starts with AC)>",
        auth_token="<Your Twilio Auth Token>"
    )
)

mcp = FastMCP("Twilio Agent")

@mcp.tool
@TwilioConnector.tool_utils
async def twilio_execute(entity: str, action: str, params: dict | None = None):
    """Execute Twilio connector operations."""
    result = await connector.execute(entity, action, params or {})
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result
```


## Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

## IP allow list

If your organization restricts access to specific IPs, add the [Airbyte Agents IP addresses](https://docs.airbyte.com/ai-agents/admin/ip-allowlist) to your allow list.

## Version information

**Connector version:** 1.0.4