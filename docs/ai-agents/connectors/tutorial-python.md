---
sidebar_label: "Python SDK tutorial"
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Get started with direct connectors: Python SDK

In this tutorial, you'll create a new Python project, install and run a Pydantic AI agent with one of Airbyte's direct connectors, and learn to use natural language to explore your data. This tutorial uses GitHub, but if you don't have a GitHub account, you can use one of Airbyte's other direct connectors and perform different operations.

Using the Python SDK is more time-consuming than the Connector MCP server, but affords you the most control over how you use direct connectors.

## Overview

This tutorial is for AI engineers and other technical users who work with data and AIs. It assumes you have basic knowledge of the following.

- Python
- Pydantic AI
- GitHub, or a different third-party service you want to connect to

## Before you start

Before you begin this tutorial, ensure you have the following.

- [Python](https://www.python.org/downloads/) version 3.10 or later
- [uv](https://github.com/astral-sh/uv)
- A [GitHub personal access token](https://github.com/settings/tokens). For this tutorial, a classic token with `repo` scope is sufficient.
- An [OpenAI API key](https://platform.openai.com/api-keys). This tutorial uses OpenAI, but Pydantic AI supports other LLM providers.

## Create a new Python project

For simplicity, in this tutorial you scaffold a basic Python project to work in. However, if you have an existing project you want to work with, feel free to use that instead.

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

By the end of this tutorial, your project will have the following structure:

```text
my-ai-agent/
├── .env
├── .gitignore
├── .python-version
├── README.md
├── agent.py
├── main.py
├── pyproject.toml
└── uv.lock
```

The `.env` file and `uv.lock` file are created in later steps.

## Install dependencies

Install the GitHub connector and Pydantic AI. This tutorial uses OpenAI as the LLM provider, but Pydantic AI supports many other providers.

```bash
uv add airbyte-ai-github pydantic-ai
```

This command installs:

- `airbyte-ai-github`: The Airbyte direct connector for GitHub, which provides type-safe access to GitHub's API.
- `pydantic-ai`: The AI agent framework, which includes support for multiple LLM providers including OpenAI, Anthropic, and Google.

The GitHub connector also includes `python-dotenv`, which you'll use to load environment variables from your `.env` file.

:::note
If you want a smaller installation with only OpenAI support, you can use `pydantic-ai-slim[openai]` instead of `pydantic-ai`. See the [Pydantic AI installation docs](https://ai.pydantic.dev/install/) for more options.
:::

## Import Pydantic AI and the GitHub direct connector

Add the following imports to `agent.py`:

```python title="agent.py"
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from airbyte_ai_github import GithubConnector
from airbyte_ai_github.models import GithubAuthConfig
```

These imports provide:

- `os`: Access environment variables for your GitHub token and LLM API key.
- `load_dotenv`: Load environment variables from your `.env` file.
- `Agent`: The Pydantic AI agent class that orchestrates LLM interactions and tool calls.
- `GithubConnector`: The Airbyte direct connector that provides type-safe access to GitHub's API.
- `GithubAuthConfig`: The authentication configuration for the GitHub connector.

:::note
You'll add more code to `agent.py` in the following sections. The `main.py` file will be updated in the [Run your project](#run-your-project) section.
:::

## Add a .env file with your secret values

Create a `.env` file in your project root to store your API keys:

```text title=".env"
GITHUB_ACCESS_TOKEN=your-github-personal-access-token
OPENAI_API_KEY=your-openai-api-key
```

Replace the placeholder values with your actual credentials.

:::warning
Never commit your `.env` file to version control. The `.gitignore` file created by `uv init` already excludes `.env` files.
:::

Next, add the following line to `agent.py` after your imports to load the environment variables:

```python title="agent.py"
load_dotenv()
```

This makes your secrets available via `os.environ`. Pydantic AI automatically reads `OPENAI_API_KEY` from the environment, and you'll use `os.environ["GITHUB_ACCESS_TOKEN"]` to configure the connector in the next section.

## Configure your GitHub connector and agent

Now that your environment is set up, add the following code to `agent.py` to create the GitHub connector and Pydantic AI agent.

### Define the connector

The GitHub connector authenticates using your personal access token:

```python title="agent.py"
connector = GithubConnector(
    auth_config=GithubAuthConfig(
        access_token=os.environ["GITHUB_ACCESS_TOKEN"]
    )
)
```

### Create the agent

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

The `system_prompt` parameter tells the LLM what role it should play and how to behave. The `"openai:gpt-4o"` string specifies the model to use.

:::note
You can use a different model by changing the model string. For example, use `"openai:gpt-4o-mini"` for lower cost, or see the [Pydantic AI models documentation](https://ai.pydantic.dev/models/) for other providers like Anthropic or Google.
:::

## Add tools to your agent

Tools let your agent fetch real data from GitHub. Without tools, the agent can only respond based on its training data. By registering connector operations as tools, the agent can decide when to call them based on natural language questions.

Add the following code to `agent.py`:

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

## Run your project

Now that your agent is configured with tools, update `main.py` to run it:

```python title="main.py"
import asyncio

from agent import agent


async def main():
    print("GitHub Agent Ready! Ask questions about GitHub repositories.")
    print("Type 'quit' to exit.\n")

    while True:
        prompt = input("You: ")
        if prompt.lower() in ('quit', 'exit', 'q'):
            break
        result = await agent.run(prompt)
        print(f"\nAgent: {result.output}\n")


if __name__ == "__main__":
    asyncio.run(main())
```

Run your project with:

```bash
uv run main.py
```

The agent waits for your input, then decides which tools to call based on your question, fetches the data from GitHub, and returns a natural language response. Try prompts like:

- "List the open issues in airbytehq/airbyte"
- "What pull requests are open in airbytehq/airbyte?"
- "Are there any open issues that might be fixed by a pending PR?"

### Troubleshooting

If your agent fails to retrieve GitHub data, check the following:

- **HTTP 401 errors**: Your `GITHUB_ACCESS_TOKEN` is invalid or expired. Generate a new token and update your `.env` file.
- **HTTP 403 errors**: Your token doesn't have the required scopes. Ensure your token has `repo` scope for accessing repository data.
- **OpenAI errors**: Verify your `OPENAI_API_KEY` is valid and has available credits.

## Summary

In this tutorial, you learned how to:

- Set up a new Python project with `uv`
- Install Pydantic AI and the GitHub direct connector
- Configure environment variables and authentication
- Add tools to your agent using the GitHub connector
- Run your project and use natural language to interact with GitHub data

## Next steps

- - Add more tools and direct connectors to your project. For GitHub, you can wrap additional operations (like search, comments, or commits) as tools. Explore other direct connectors in the [Airbyte AI connectors catalog](https://github.com/airbytehq/airbyte-ai-connectors) to give your agent access to more services.
- Consider how you might like to expand your agent's capabilities. For example, you might want to trigger effects like sending a Slack message or an email. You aren't limited to the capabilities of Airbyte's direct connectors. You can use other libraries and integrations to build a more robust agent.
