---
products: embedded
---

# Overview

The PyAirbyte remote MCP server provides the ability for application developers to generate a data pipeline in Python using a single prompt. It is currently designed to work within Cursor, and broader support in the near future.

To add the PyAirbyte MCP open Cursor and navigate to Settings > Tools & Integrations, and tap New MCP Sever. Add the following json snippet. This file tells Cursor which remote MCP servers to connect to and what credentials to pass along.

Paste the following into your `mcp.json` file:

```json
{
  "mcpServers": {
    "pyairbyte-mcp": {
      "url": "https://pyairbyte-mcp-7b7b8566f2ce.herokuapp.com/mcp",
      "env": {
        "OPENAI_API_KEY": "<your-openai-api-key>"
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