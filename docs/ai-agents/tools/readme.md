# Calling tools

Tools are external capabilities an AI agent can invoke. They allow agents to perceive, decide, and act beyond conversational UIs.

## What tools do and why you need them

Large language models, by default, lack real-time knowledge, are stateless, and cannot act and verify facts. This places severe limits on their capabilities. Tools solve this problem by expanding the capabilities of an LLM. Tools are callable functions, services, and interfaces that an AI agent can use to:

- Retrieve information it doesn't have
- Perform computations or transformations
- Interact with external systems
- Trigger side-effects, like sending emails, updating databases, and triggering workflows

When you expose a connector as a tool for AI agents, the agent needs to understand what entities and actions are available, what parameters each action requires, and how to paginate through results. Without this information in the tool description, agents make incorrect API calls or require extra discovery calls to understand the API.

## How to call tools

Airbyte agent connectors provide two approaches for defining tools: manual docstrings for fine-grained control, and auto-generated descriptions for comprehensive coverage with minimal code.

### Manual docstrings

You can manually define individual tools with hand-written docstrings. This approach gives you precise control over what operations are exposed and how they're described to the agent.

```python
from pydantic_ai import Agent
from airbyte_agent_github import GithubConnector

agent = Agent("openai:gpt-4o")
connector = GithubConnector(auth_config=...)

@agent.tool_plain
async def list_issues(owner: str, repo: str, limit: int = 10) -> str:
    """List open issues in a GitHub repository."""
    result = await connector.issues.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
    return str(result.data)
```

The docstring becomes the tool's description, which helps the LLM understand when to use it. The function parameters become the tool's input schema, so the LLM knows what arguments to provide.

This approach works well when you want to expose only specific operations or need custom parameter handling. However, it requires writing and maintaining docstrings for each tool, and the agent only knows about the operations you explicitly define.

### Auto-generated descriptions

For comprehensive tool coverage, use the `@Connector.describe` decorator. This decorator reads the connector's metadata and automatically generates a detailed docstring that includes all available entities, actions, parameters, and response structures.

```python
from pydantic_ai import Agent
from airbyte_agent_github import GithubConnector

agent = Agent("openai:gpt-4o")
connector = GithubConnector(auth_config=...)

@agent.tool_plain
@GithubConnector.describe
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute operations on GitHub."""
    return await connector.execute(entity, action, params or {})
```

The decorator automatically expands the docstring to include all available entities and actions, their required and optional parameters, response structure details, and pagination guidance. This gives the LLM everything it needs to correctly call the connector without additional discovery calls.

## Introspection capabilities

Beyond the `describe` decorator, connectors provide programmatic introspection methods for runtime discovery.

### list_entities()

Returns structured data about all available entities, their actions, and parameters:

```python
entities = connector.list_entities()
for entity in entities:
    print(f"{entity['entity_name']}: {entity['available_actions']}")
    # Output: customers: ['list', 'get', 'search']
```

Each entity description includes the entity name, a description, available actions, and detailed parameter information for each action including parameter names, types, whether they're required, and their location (path, query, or body).

### entity_schema()

Returns the JSON schema for a specific entity, useful for understanding the structure of returned data:

```python
schema = connector.entity_schema("customers")
if schema:
    print(f"Customer properties: {list(schema.get('properties', {}).keys())}")
```

## Decorator ordering

When using the `describe` decorator with agent frameworks like Pydantic AI or FastMCP, decorator order matters. The `@Connector.describe` decorator must be the **inner** decorator (closest to the function definition) because frameworks capture docstrings at decoration time.

Correct ordering:

```python
@agent.tool_plain        # Outer: framework decorator captures __doc__
@GithubConnector.describe  # Inner: sets __doc__ before framework sees it
async def github_execute(entity: str, action: str, params: dict | None = None):
    ...
```

If you reverse the order, the framework captures the original docstring before `describe` has a chance to expand it, and the agent won't see the auto-generated documentation.

## Examples

### Pydantic AI with auto-generated descriptions

```python
from pydantic_ai import Agent
from airbyte_agent_stripe import StripeConnector
from airbyte_agent_stripe.models import StripeAuthConfig

connector = StripeConnector(
    auth_config=StripeAuthConfig(api_key=os.environ["STRIPE_API_KEY"])
)

agent = Agent(
    "openai:gpt-4o",
    system_prompt="You are a helpful assistant that can access Stripe data."
)

@agent.tool_plain
@StripeConnector.describe
async def stripe_execute(entity: str, action: str, params: dict | None = None):
    """Execute operations on Stripe."""
    return await connector.execute(entity, action, params or {})
```

### Multiple connectors

You can register multiple connectors as separate tools, each with its own auto-generated description:

```python
from airbyte_agent_github import GithubConnector
from airbyte_agent_hubspot import HubspotConnector

github = GithubConnector(auth_config=...)
hubspot = HubspotConnector(auth_config=...)

@agent.tool_plain
@GithubConnector.describe
async def github_execute(entity: str, action: str, params: dict | None = None):
    """Execute operations on GitHub."""
    return await github.execute(entity, action, params or {})

@agent.tool_plain
@HubspotConnector.describe
async def hubspot_execute(entity: str, action: str, params: dict | None = None):
    """Execute operations on HubSpot."""
    return await hubspot.execute(entity, action, params or {})
```

The agent can then decide which connector to use based on the user's question and the tool descriptions.
