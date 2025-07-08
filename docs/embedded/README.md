---
products: embedded
---

# Airbyte Embedded

[Airbyte Embedded](https://airbyte.com/ai) provides product and software teams the tools and services to move data to provide context for AI applications. Embedded provides the following:

- **MCP Server**: App developers looking to utilize PyAirbyte to generate pipelines in code can follow the steps below to utilize the PyAirbyte MCP server. 
- **Workspaces & Onboarding Widget**: App development teams who have signed up for Airbyte Embedded and are looking to get started onboarding customers using the Embed Widget can follow the get started guide at the bottom of this page, which will step you through a complete sample onboarding app.


## PyAirbyte MCP

The PyAirbyte remote MCP server provides the ability for application developers to generate a data pipeline in Python using a single prompt. It is currently designed to work within Cursor, and broader support in the near future.

To add the PyAirbyte MCP open Cursor and navigate to Settings > Tools & Integrations, and tap New MCP Sever. Add the following json snippet. This file tells Cursor which remote MCP servers to connect to and what credentials to pass along.

Paste the following into your `mcp.json` file:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key"
      }
    }
  }
}
```

Make sure to replace `<your-openai-api-key>` with your actual key from the [OpenAI platform](https://platform.openai.com/account/api-keys).

Save the file. Cursor will automatically detect the MCP server and display **pyairbyte-mcp** as an available MCP tool with a green dot indicating that it has found the available tools.

Within your Cursor project, start a new chat. In the input box, type the following prompt:

```bash
create a data pipeline from source-faker to destination-snowflake
```

The MCP server will process your prompt and respond by generating all the necessary Python code to extract data from `faker` and load it into `Snowflake`. We suggest you prefix your source and destination with `source-` and `destination-` to ensure specificity when the MCP server performs a embedded source on the Airbyte Connector registry. Connectors for sources and destinations may have the same name, but different configuration parameters.

In a few moments, your pipeline will be created, typically in a file called `pyairbyte_pipeline.py`. In addition, the MCP server will generate complete instructions on how to use the server and configure required parameters using a  `.env` file that includes environment variables you’ll need to fill in.

Create a `.env` file and populate it with your source parameters and Snowflake connection details, per generated instructions. For example:

```env
AIRBYTE_DESTINATION__SNOWFLAKE__HOST=your_account.snowflakecomputing.com
AIRBYTE_DESTINATION__SNOWFLAKE__USERNAME=your_user
AIRBYTE_DESTINATION__SNOWFLAKE__PASSWORD=your_password
AIRBYTE_DESTINATION__SNOWFLAKE__DATABASE=your_db
AIRBYTE_DESTINATION__SNOWFLAKE__SCHEMA=your_schema
AIRBYTE_DESTINATION__SNOWFLAKE__WAREHOUSE=your_warehouse
```

## Embedded Workspaces & Widget

Once your Organization is enabled via Airbyte Embedded, you can begin onboarding customers via the Embed Widget. The Get Started Guide walks you through how to configure a React.js serverless app for the onboarding app. You can download the code for the onboarding app [via GitHub](https://github.com/airbytehq/embedded-sampleweb-reactjs). If you prefer to develop in Node.js, please use [this sample app](https://github.com/airbytehq/embedded-sampleweb-nodejs) instead. Regardless of web framework you choose, the pre-requisites required for initial set up are the same.
