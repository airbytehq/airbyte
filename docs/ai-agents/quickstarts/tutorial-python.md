---
sidebar_label: "Python SDK tutorial"
sidebar_position: 1
---

# Agent connector tutorial: Python SDK

In this tutorial, you'll create a new Python project with uv, add a Pydantic AI agent, equip it to use one of Airbyte's agent connectors, and use natural language to explore your data. This tutorial uses GitHub, but if you don't have a GitHub account, you can use one of Airbyte's other agent connectors and perform different operations.

Using the Python SDK is more time-consuming than the Connector MCP server, but affords you the most control over the context you send to your agent.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AI tools. You can complete it in about 15 minutes.

The tutorial assumes you have basic knowledge of the following tools, but most software engineers shouldn't struggle with anything that follows.

- Python and package management with uv
- Pydantic AI
- GitHub, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.13 or later
- [uv](https://github.com/astral-sh/uv)
- A [GitHub personal access token](https://github.com/settings/tokens). For this tutorial, a classic token with `repo` scope is sufficient.
- An [OpenAI API key](https://platform.openai.com/api-keys). This tutorial uses OpenAI, but Pydantic AI supports other LLM providers if you prefer.

## Part 1: Create a new Python project

In this tutorial you initialize a basic Python project to work in. However, if you have an existing project you want to work with, feel free to use that instead.

1. Create a new project using uv:

   ```bash
   uv init my-ai-agent --app
   cd my-ai-agent
   ```

   This creates a project with the following structure:

   ```text
   my-ai-agent/
   ├── .gitignore
   ├── .python-version
   ├── README.md
   ├── main.py
   └── pyproject.toml
   ```

2. Create an `agent.py` file for your agent definition:

   ```bash
   touch agent.py
   ```

You create `.env` and `uv.lock` files in later steps, so don't worry about them yet.

## Part 2: Install dependencies

Install the GitHub connector and Pydantic AI. This tutorial uses OpenAI as the LLM provider, but Pydantic AI supports many other providers.

```bash
uv add airbyte-agent-github pydantic-ai
```

This command installs:

- `airbyte-agent-github`: The Airbyte agent connector for GitHub, which provides type-safe access to GitHub's API.
- `pydantic-ai`: The AI agent framework, which includes support for multiple LLM providers including OpenAI, Anthropic, and Google.

The GitHub connector also includes `python-dotenv`, which you can use to load environment variables from a `.env` file.

:::note
If you want a smaller installation with only OpenAI support, you can use `pydantic-ai-slim[openai]` instead of `pydantic-ai`. See the [Pydantic AI installation docs](https://ai.pydantic.dev/install/) for more options.
:::

## Part 3: Import Pydantic AI and the GitHub agent connector

Add the following imports to `agent.py`:

```python title="agent.py"
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from airbyte_agent_github import GithubConnector
from airbyte_agent_github.models import GithubAuthConfig
```

These imports provide:

- `os`: Access environment variables for your GitHub token and LLM API key.
- `load_dotenv`: Load environment variables from your `.env` file.
- `Agent`: The Pydantic AI agent class that orchestrates LLM interactions and tool calls.
- `GithubConnector`: The Airbyte agent connector that provides type-safe access to GitHub's API.
- `GithubAuthConfig`: The authentication configuration for the GitHub connector.

## Part 4: Add a .env file with your secrets

1. Create a `.env` file in your project root and add your secrets to it. Replace the placeholder values with your actual credentials.

    ```text title=".env"
    GITHUB_ACCESS_TOKEN=your-github-personal-access-token
    OPENAI_API_KEY=your-openai-api-key
    ```

    :::warning
    Never commit your `.env` file to version control. If you do this by mistake, rotate your secrets immediately.
    :::

2. Add the following line to `agent.py` after your imports to load the environment variables:

    ```python title="agent.py"
    load_dotenv()
    ```

    This makes your secrets available via `os.environ`. Pydantic AI automatically reads `OPENAI_API_KEY` from the environment, and you'll use `os.environ["GITHUB_ACCESS_TOKEN"]` to configure the connector in the next section.

## Part 5: Configure your connector and agent

Now that your environment is set up, add the following code to `agent.py` to create the GitHub connector and Pydantic AI agent.

### Define the connector

Define the agent connector for GitHub. It authenticates using your personal access token.

```python title="agent.py"
connector = GithubConnector(
    auth_config=GithubAuthConfig(
        access_token=os.environ["GITHUB_ACCESS_TOKEN"]
    )
)
```

### Define the agent

Create a Pydantic AI agent with a system prompt that describes its purpose:

```python title="agent.py"
agent = Agent(
    "openai:gpt-4o",
    system_prompt=(
        "You are a helpful assistant that can access GitHub repositories, issues, "
        "and pull requests. Use the available tools to answer questions about "
        "GitHub data. Be concise and accurate in your responses."
    ),
)
```

- The `"openai:gpt-4o"` string specifies the model to use. You can use a different model by changing the model string. For example, use `"openai:gpt-4o-mini"` to lower costs, or see the [Pydantic AI models documentation](https://ai.pydantic.dev/models/) for other providers like Anthropic or Google.
- The `system_prompt` parameter tells the LLM what role it should play and how to behave.

## Part 6: Add tools to your agent

Tools let your agent fetch real data from GitHub using Airbyte's agent connector. Without tools, the agent can only respond based on its training data. By registering connector operations as tools, the agent can decide when to call them based on natural language questions.

Add the following code to `agent.py`.

```python title="agent.py"
# Tool to list issues in a repository
@agent.tool_plain
async def list_issues(owner: str, repo: str, limit: int = 10) -> str:
    """List open issues in a GitHub repository."""
    result = await connector.issues.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
    return str(result.data)


# Tool to list pull requests in a repository
@agent.tool_plain
async def list_pull_requests(owner: str, repo: str, limit: int = 10) -> str:
    """List open pull requests in a GitHub repository."""
    result = await connector.pull_requests.list(owner=owner, repo=repo, states=["OPEN"], per_page=limit)
    return str(result.data)
```

The `@agent.tool_plain` decorator registers each function as a tool the agent can call. The docstring becomes the tool's description, which helps the LLM understand when to use it. The function parameters become the tool's input schema, so the LLM knows what arguments to provide.

With these two tools, your agent can answer questions about issues, pull requests, or both. For example, it can compare open issues against pending PRs to identify which issues might be resolved soon.

## Part 7: Run your project

Now that your agent is configured with tools, update `main.py` and run your project.

1. Update `main.py`. This code creates a simple chat interface in your command line tool and allows your agent to remember your conversation history between prompts.

    ```python title="main.py"
    import asyncio
    from agent import agent

    async def main():
        print("GitHub Agent Ready! Ask questions about GitHub repositories.")
        print("Type 'quit' to exit.\n")

        history = None

        while True:
            prompt = input("You: ")
            if prompt.lower() in ('quit', 'exit', 'q'):
                break
            result = await agent.run(prompt, message_history=history)
            history = result.all_messages()  # Call the method
            print(f"\nAgent: {result.output}\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

2. Run the project.

    ```bash
    uv run main.py
    ```

### Chat with your agent

The agent waits for your input. Once you prompt it, the agent decides which tools to call based on your question, fetches the data from GitHub, and returns a natural language response. Try prompts like:

- "List the 10 most recent open issues in airbytehq/airbyte"
- "What are the 10 most recent pull requests that are still open in airbytehq/airbyte?"
- "Are there any open issues that might be fixed by a pending PR?"

The agent has basic message history within each session, and you can ask followup questions based on its responses.

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **HTTP 401 errors**: Your `GITHUB_ACCESS_TOKEN` is invalid or expired. Generate a new token and update your `.env` file.
- **HTTP 403 errors**: Your `GITHUB_ACCESS_TOKEN` doesn't have the required scopes. Ensure your token has `repo` scope for accessing repository data.
- **OpenAI errors**: Verify your `OPENAI_API_KEY` is valid, has available credits, and won't exceed rate limits.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with uv
- Add Pydantic AI and Airbyte's GitHub agent connector to your project
- Configure environment variables and authentication
- Add tools to your agent using the GitHub connector
- Run your project and use natural language to interact with GitHub data

## Next steps

- Add more tools and agent connectors to your project. For GitHub, you can wrap additional operations (like search, comments, or commits) as tools. Explore other agent connectors in the [Airbyte agent connectors catalog](https://github.com/airbytehq/airbyte-agent-connectors) to give your agent access to more services.
- Consider how you might like to expand your agent's capabilities. For example, you might want to trigger effects like sending a Slack message or an email based on the agent's findings. You aren't limited to the capabilities of Airbyte's agent connectors. You can use other libraries and integrations to build an increasingly robust agent ecosystem.
