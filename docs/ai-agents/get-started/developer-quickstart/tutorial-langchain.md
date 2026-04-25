---
sidebar_label: "LangChain"
sidebar_position: 2
---

# Agent connector tutorial: LangChain

In this tutorial, you'll create a new Python project with uv, add a LangChain agent, equip it with one of Airbyte's agent connectors, and use natural language to explore your data. This tutorial uses GitHub, but if you don't have a GitHub account you can swap in any other agent connector and perform different operations.

Your agent executes through Airbyte. Airbyte Agents owns the OAuth apps, stores your third-party tokens, and refreshes them for you. Your Python code only ever sees your Airbyte client ID and client secret.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AI tools. You can complete it in about 15 minutes.

The tutorial assumes you have basic knowledge of the following tools, but most software engineers shouldn't struggle with anything that follows.

- Python and package management with uv
- LangChain and LangGraph
- GitHub, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.13 or later
- [uv](https://github.com/astral-sh/uv)
- An [Airbyte Agents account](https://app.airbyte.ai). You can sign up for free.
- Your Airbyte API credentials. Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app. See [Manage your user profile](../../admin/profile) for details.
- A GitHub connector added to your Airbyte Agents workspace. Add one of these two ways:
    - **Web app (recommended)**: Go to [Credentials](https://app.airbyte.ai/credentials) in the Airbyte Agents web app, add a GitHub connector, and authenticate it with a [GitHub personal access token](https://github.com/settings/tokens) (a classic token with `repo` scope is sufficient for this tutorial) or OAuth. See [Add a connector](../../interfaces/ui/add-connector) for details.
    - **API**: Create a connector with `POST /api/v1/integrations/connectors` and store your GitHub credentials. See [Add a connector](../../interfaces/api/add-connector) for details.
- An [OpenAI API key](https://platform.openai.com/api-keys). This tutorial uses OpenAI, but LangChain supports other LLM providers if you prefer.

## Part 1: Create a new Python project

In this tutorial you initialize a basic Python project to work in. However, if you have an existing project you want to work with, feel free to use that instead.

Create a new project using uv:

```bash
uv init my-langchain-agent --app
cd my-langchain-agent
```

This creates a project with the following structure:

```text
my-langchain-agent/
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
└── README.md
```

You create `.env` and `uv.lock` files in later steps, so don't worry about them yet.

## Part 2: Install dependencies

Install the Airbyte agent SDK, LangChain with OpenAI support, and LangGraph for the agent runtime:

```bash
uv add airbyte-agent-sdk langchain langchain-openai langgraph python-dotenv
```

This command installs:

- `airbyte-agent-sdk`: The Airbyte Agents Python SDK, which ships every connector as a typed submodule.
- `langchain`: The LangChain framework core.
- `langchain-openai`: LangChain's OpenAI integration for chat models.
- `langgraph`: The LangGraph agent runtime, which provides a `create_react_agent` function for building tool-calling agents.
- `python-dotenv`: A library you can use to load environment variables from a `.env` file.

## Part 3: Import LangChain and the GitHub agent connector

1. Create an `agent.py` file for your agent definition:

    ```bash
    touch agent.py
    ```

2. Add the following imports to `agent.py`:

    ```python title="agent.py"
    import json

    from dotenv import load_dotenv
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    from airbyte_agent_sdk import connect
    from airbyte_agent_sdk.connectors.github import GithubConnector
    ```

    These imports provide:

    - `json`: Serialize connector results for the LangChain tool return value.
    - `load_dotenv`: Load environment variables from your `.env` file.
    - `tool`: LangChain's decorator for converting a function into a tool.
    - `ChatOpenAI`: LangChain's OpenAI chat model integration.
    - `create_react_agent`: LangGraph's function for creating a ReAct agent that can call tools.
    - `connect`: The Airbyte agent SDK entry point. One call returns a typed connector bound to your workspace.
    - `GithubConnector`: The connector class. You reference it when decorating the tool so the SDK can describe the connector's entities and actions to the agent.

## Part 4: Add a .env file with your secrets

1. Create a `.env` file in your project root and add your secrets to it. Replace the placeholder values with your actual credentials.

    ```text title=".env"
    AIRBYTE_CLIENT_ID=your-airbyte-client-id
    AIRBYTE_CLIENT_SECRET=your-airbyte-client-secret
    OPENAI_API_KEY=your-openai-api-key
    ```

    Copy `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the [Profile page](https://app.airbyte.ai/profile) in the Airbyte Agents web app.

    :::warning
    Never commit your `.env` file to version control. If you do this by mistake, rotate your secrets immediately.
    :::

2. Add the following line to `agent.py` after your imports to load the environment variables:

    ```python title="agent.py"
    load_dotenv()
    ```

    This makes your secrets available via `os.environ`. LangChain's `ChatOpenAI` automatically reads `OPENAI_API_KEY` from the environment, and the agent SDK picks up `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the environment in the next step.

## Part 5: Configure your connector and agent

Now that your environment is set up, add the following code to `agent.py` to create the GitHub connector and LangChain agent.

### Define the connector

Connect to GitHub through your Airbyte Agents workspace:

```python title="agent.py"
github = connect("github")
```

One line does four things for you:

- Reads `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` from the environment.
- Defaults to the `"default"` workspace, which is where the web app stores credentials unless you change it.
- Returns a typed `GithubConnector` bound to the authenticated GitHub connector you added earlier.
- Routes every `github.execute(...)` call through Airbyte's hosted API, which holds the GitHub OAuth tokens and refreshes them for you.

You never register an OAuth app, copy a GitHub token into your code, or write token-refresh logic.

If you want to connect to a different workspace or pass credentials explicitly, use `connect("github", workspace_name="my-workspace", client_id=..., client_secret=...)` or pass an `AirbyteAuthConfig`. See the [SDK reference](https://github.com/airbytehq/airbyte-agent-sdk) for details.

### Define the tool

Rather than one tool per GitHub endpoint, the Airbyte agent SDK exposes the entire GitHub API through a single `execute(entity, action, params)` entry point. The `@GithubConnector.tool_utils` decorator fills in the entity and action catalog as the tool description, so the agent knows what's available without you writing a schema.

```python title="agent.py"
@tool
@GithubConnector.tool_utils
async def github_execute(entity: str, action: str, params: dict | None = None) -> str:
    """Execute GitHub connector operations."""
    result = await github.execute(entity, action, params or {})
    return json.dumps(result, default=str)
```

The decorator stack is the whole tool definition. No per-action `docstring`, no `GITHUB_LIST_COMMITS` or `GITHUB_GET_PR` sprawl, one entry point that covers the full connector. `@GithubConnector.tool_utils` appends the full entity and action catalog to the tool description, and caps oversized responses. As the connector grows, the tool signature stays the same.

Each `execute` call returns a structured result with `data` (the records) and `meta` (pagination cursors). LangChain tools return strings, so this tutorial serializes the whole result with `json.dumps` so the agent can reason about both the records and the pagination state.

### Define the agent

Create a LangChain chat model and a LangGraph ReAct agent with a system prompt that describes its purpose:

```python title="agent.py"
llm = ChatOpenAI(model="gpt-4o")

agent = create_react_agent(
    llm,
    [github_execute],
    prompt=(
        "You are a helpful assistant that can access GitHub data through the "
        "github_execute tool. Be concise and accurate."
    ),
)
```

- `ChatOpenAI(model="gpt-4o")` creates an OpenAI chat model. You can use a different model by changing the model string. For example, use `"gpt-4o-mini"` to lower costs. LangChain also supports [other providers](https://python.langchain.com/docs/integrations/chat/) like Anthropic and Google.
- `create_react_agent` creates a ReAct agent that reasons about which tools to call based on the user's input.
- The `prompt` parameter is where you encode any API idiosyncrasies the model can't see in the tool schema. The Airbyte agent SDK already exposes entity names, actions, and enum values through the tool description, so the prompt only needs to carry domain constraints (pagination defaults, date formats, preferred streams) as your agent grows.

## Part 6: Run your project

Now that your agent is configured with tools, update `main.py` and run your project.

1. Update `main.py`. This code creates a simple chat interface in your command line tool and allows your agent to remember your conversation history between prompts.

    ```python title="main.py"
    import asyncio
    from agent import agent

    async def main():
        print("GitHub Agent Ready! Ask questions about GitHub repositories.")
        print("Type 'quit' to exit.\n")

        history = []

        while True:
            prompt = input("You: ")
            if prompt.lower() in ("quit", "exit", "q"):
                break
            history.append({"role": "user", "content": prompt})
            result = await agent.ainvoke({"messages": history})
            response = result["messages"][-1].content
            history = result["messages"]
            print(f"\nAgent: {response}\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

2. Run the project.

    ```bash
    uv run main.py
    ```

### Chat with your agent

The agent waits for your input. Once you prompt it, the agent decides which entity and action to call based on your question, asks Airbyte to execute it, and returns a natural language response. Try prompts like:

- "List the 10 most recent open issues in airbytehq/airbyte"
- "What are the 10 most recent pull requests that are still open in airbytehq/airbyte?"
- "Are there any open issues that might be fixed by a pending PR?"

The agent has basic message history within each session, and you can ask followup questions based on its responses.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **HTTP 401/403 errors from Airbyte**: Verify that `AIRBYTE_CLIENT_ID` and `AIRBYTE_CLIENT_SECRET` are copied correctly from your [Profile page](https://app.airbyte.ai/profile).
- **"No connector found" or "connector not configured"**: Make sure you've added a GitHub connector in the [Credentials](https://app.airbyte.ai/credentials) page of the Airbyte Agents web app. `connect("github")` defaults to the `"default"` workspace; if you added the connector to a different workspace, pass `workspace_name="your-workspace-name"` to `connect()`.
- **HTTP 401/403 errors from GitHub**: The GitHub token or OAuth credentials stored in your connector are invalid or missing required scopes. Open your GitHub connector in the web app and reauthenticate with a valid token that has `repo` scope.
- **Empty `data=[]` responses from filtered queries**: Most GitHub filters use case-sensitive values. Confirm the agent is sending uppercase values (for example, `states=["OPEN"]` rather than `states=["open"]`). The system prompt in this tutorial nudges the model to do that by default.
- **OpenAI errors**: Verify your `OPENAI_API_KEY` is valid, has available credits, and won't exceed rate limits.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add LangChain, LangGraph, and Airbyte's GitHub agent connector to your project
- Configure environment variables for your Airbyte Agents credentials
- Wire up a single tool that covers the entire GitHub API
- Build a ReAct agent with LangGraph and use natural language to interact with GitHub data through Airbyte

## Next steps

- **Add another connector.** The same `connect(...)` + `execute(...)` pattern covers the full [Airbyte agent connectors catalog](../../connectors). Add Slack, Stripe, Salesforce, or any other connector in the web app, then call `slack = connect("slack")` in your agent and register a second tool with another `@tool` / `@SlackConnector.tool_utils` stack. Your agent now reads GitHub and posts to Slack with no additional OAuth setup.
- **Use write actions.** Connectors expose create, update, and post actions alongside the read ones. Ask the agent to file an issue, comment on a PR, or send a Slack message, and `execute` carries the write through with the stored OAuth token.
- **Let your AI assistant scaffold the next agent.** The Airbyte agent SDK ships skills for Claude Code and Codex that carry the patterns above, so you can ask your assistant to build a new agent without retyping them. See the [airbyte-agent-sdk repository](https://github.com/airbytehq/airbyte-agent-sdk) for installation instructions.
- **Reach the same connectors from any MCP client.** Airbyte Agents exposes the same connectors through a hosted MCP endpoint that works with Claude Code, Cursor, and ChatGPT. See the [FastMCP tutorial](./tutorial-fastmcp) for a local-server variant you can run yourself.
