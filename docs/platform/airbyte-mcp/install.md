---
products: cloud
---

# Connect Airbyte MCP to your agent

:::info Private beta
Airbyte MCP is in private beta. Features and tools may change. It's available to Airbyte Cloud organizations enrolled in the beta. Self-managed versions of Airbyte aren't supported during the beta.
:::

Airbyte MCP is a hosted, remote MCP server. You don't need to install anything. Give your MCP client this URL and sign in with your Airbyte Cloud account.

```text
https://mcp.airbyte.com/mcp
```

## Prerequisites

- An [Airbyte Cloud](https://cloud.airbyte.com) account in an organization enrolled in the private beta.
- An MCP client that supports remote MCP servers with OAuth and the Streamable HTTP transport.
- To read data directly from sources and destinations, an organization admin must [enable the Context layer](../context-layer/manage-access.md). You can use Airbyte MCP to manage pipelines without it.

## Sign in

The first time your client connects, it opens the Airbyte Cloud sign-in page in your browser. Sign in with the account you use for Airbyte Cloud and grant access.

If your organization uses [single sign-on](/platform/access-management/sso), select **Sign in with SSO** and enter your **Company identifier**. This is the same identifier you enter after you select **Continue with SSO** on the Airbyte Cloud sign-in page. If you don't know it, ask your Airbyte organization admin.

If you belong to more than one workspace, Airbyte MCP uses your default workspace. Ask your agent to list your workspaces or switch to a different one at any time.

## Add Airbyte MCP to your client

Expand your client below for setup instructions.

<details>
<summary>ChatGPT web</summary>

ChatGPT connects to remote MCP servers as custom apps in developer mode. Developer mode is available on ChatGPT Business, Enterprise, and education plans, and workspace admins control who can use it. For details, see [Developer mode and MCP apps in ChatGPT](https://help.openai.com/en/articles/12584461).

1. In [ChatGPT](https://chatgpt.com), confirm developer mode is on for your account. Go to **Settings** > **Apps** > **Advanced settings**.

2. Go to **Settings** > **Apps** and click **Create**.

3. Enter a name, like `Airbyte`, and enter the MCP server URL: `https://mcp.airbyte.com/mcp`.

4. Choose OAuth authentication.

5. Click **Scan Tools**. When prompted, sign in to Airbyte Cloud and grant access.

6. Click **Create**.

7. In a new conversation, add the Airbyte app and ask ChatGPT to use it. For example, _"Use Airbyte to list my connections."_

</details>

<details>
<summary>ChatGPT desktop</summary>

The ChatGPT desktop app uses the apps you add to your ChatGPT account. Follow the **ChatGPT web** instructions to add Airbyte MCP in your browser, then start a new conversation in the desktop app and add the Airbyte app.

</details>

<details>
<summary>Claude web</summary>

Claude connects to remote MCP servers as custom connectors. For details, see [Get started with custom connectors using remote MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).

1. In [Claude](https://claude.ai), go to **Customize** > **Connectors**.

2. Click **+** next to **Connectors**, then select **Add custom connector**.

3. Enter a name, like `Airbyte`, and enter the URL: `https://mcp.airbyte.com/mcp`.

4. Click **Add**, then click **Connect**.

5. Sign in to Airbyte Cloud and grant access.

On Team and Enterprise plans, an owner must first add the custom connector in **Organization settings** > **Connectors**. After that, each member finds it in **Customize** > **Connectors** and clicks **Connect**.

</details>

<details>
<summary>Claude Desktop</summary>

Custom connectors you add on Claude web are also available in Claude Desktop. Follow the **Claude web** instructions in Claude Desktop or in your browser. Claude connects to Airbyte MCP from the cloud, so you don't need to edit a local configuration file.

</details>

<details>
<summary>Claude Code</summary>

1. Run the following command in your terminal.

   ```bash
   claude mcp add --transport http airbyte https://mcp.airbyte.com/mcp
   ```

2. Run Claude Code with `claude`.

3. Type `/mcp`, select **airbyte**, then select **Authenticate**. Your browser opens.

4. Sign in to Airbyte Cloud and grant access.

5. Return to Claude Code and start using Airbyte MCP.

</details>

<details>
<summary>VS Code</summary>

[Click to install in VS Code](https://vscode.dev/redirect?url=vscode%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D), or set it up manually.

To install from the command line, run:

```bash
code --add-mcp '{"name":"airbyte","type":"http","url":"https://mcp.airbyte.com/mcp"}'
```

To install with a configuration file, add this to `.vscode/mcp.json` in your workspace, or run **MCP: Open User Configuration** from the Command Palette to edit your user configuration.

```json
{
  "servers": {
    "airbyte": {
      "type": "http",
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

VS Code detects that the server requires OAuth and opens your browser. Sign in to Airbyte Cloud and grant access. Airbyte MCP's tools are then available in Copilot Chat.

</details>

<details>
<summary>VS Code Insiders</summary>

[Click to install in VS Code Insiders](https://insiders.vscode.dev/redirect?url=vscode-insiders%3Amcp%2Finstall%3F%257B%2522name%2522%253A%2522airbyte%2522%252C%2522type%2522%253A%2522http%2522%252C%2522url%2522%253A%2522https%253A%252F%252Fmcp.airbyte.com%252Fmcp%2522%257D), or set it up manually.

To install from the command line, run:

```bash
code-insiders --add-mcp '{"name":"airbyte","type":"http","url":"https://mcp.airbyte.com/mcp"}'
```

To install with a configuration file, add this to `.vscode/mcp.json` in your workspace, or run **MCP: Open User Configuration** from the Command Palette to edit your user configuration.

```json
{
  "servers": {
    "airbyte": {
      "type": "http",
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

VS Code Insiders detects that the server requires OAuth and opens your browser. Sign in to Airbyte Cloud and grant access. Airbyte MCP's tools are then available in Copilot Chat.

</details>

<details>
<summary>Cursor</summary>

[Click to install in Cursor](cursor://anysphere.cursor-deeplink/mcp/install?name=airbyte&config=eyJ1cmwiOiJodHRwczovL21jcC5haXJieXRlLmNvbS9tY3AifQ%3D%3D), or add this to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

In **Cursor Settings** > **Tools and MCP**, find **airbyte** and click **Connect**. Sign in to Airbyte Cloud and grant access.

</details>

<details>
<summary>Other clients</summary>

Airbyte MCP works with any client that supports remote MCP servers with OAuth and the Streamable HTTP transport. Use this server URL:

```text
https://mcp.airbyte.com/mcp
```

Many clients accept a JSON configuration like this. Key names vary by client, so check your client's documentation.

```json
{
  "mcpServers": {
    "airbyte": {
      "url": "https://mcp.airbyte.com/mcp"
    }
  }
}
```

When your client first connects, it detects that the server requires OAuth. It may open your browser automatically, or you may need to click a button to start sign-in. Sign in to Airbyte Cloud and grant access.

</details>

## Connect without a browser

<details>
<summary>Authenticate with an Airbyte application</summary>

Automated agents, scripts, and CI jobs can't complete a browser sign-in. Instead, they can authenticate with an Airbyte application.

1. [Create an application and get an access token](/platform/using-airbyte/configuring-api-access). The application acts with the permissions of the user who created it, so consider using a service account.

2. Send the access token in the `Authorization` header of every request to Airbyte MCP.

   ```json
   {
     "mcpServers": {
       "airbyte": {
         "url": "https://mcp.airbyte.com/mcp",
         "headers": {
           "Authorization": "Bearer <ACCESS_TOKEN>"
         }
       }
     }
   }
   ```

3. Optional: to choose a workspace or organization other than your default, add the `X-Airbyte-Workspace-Id` or `X-Airbyte-Organization-Id` header.

Access tokens expire after 15 minutes. Your agent needs to request a new token before the current one expires.

</details>

## Next steps

- See what your agent can do in [Airbyte MCP tools](tools.md).
- Ask an organization admin to [enable the Context layer](../context-layer/manage-access.md) so your agent can read data directly from sources and destinations.
