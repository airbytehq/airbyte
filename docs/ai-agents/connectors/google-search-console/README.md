# Google-Search-Console

The Google-Search-Console agent connector is a Python package that equips AI agents to interact with Google-Search-Console through strongly typed, well-documented tools. It's ready to use directly in your Python app, in an agent framework, or exposed through an MCP.

Connector for the Google Search Console API. Provides access to website search performance data including clicks, impressions, CTR, and average position. Supports listing verified sites, sitemaps, and querying search analytics data broken down by date, country, device, page, and query dimensions.


## Example questions

The Google-Search-Console connector is optimized to handle prompts like these.

- List all my verified sites in Search Console
- Show me the sitemaps for my website
- Get search analytics by date for the last 7 days
- Show search performance broken down by country
- What devices are people using to find my site?
- Which pages get the most clicks?
- What queries bring the most traffic to my site?
- Which country has the highest CTR for my site?
- What are my top 10 search queries by impressions?
- Compare mobile vs desktop click-through rates
- Which pages have the worst average position?
- Show me search performance trends over the last month

## Unsupported questions

The Google-Search-Console connector isn't currently able to handle prompts like these.

- Submit a new sitemap
- Add a new site to Search Console
- Remove a site from Search Console
- Inspect a URL's index status
- Request indexing for a page

## Installation

```bash
uv pip install airbyte-agent-google-search-console
```

## Usage

Connectors can run in open source or hosted mode.

### Open source

In open source mode, you provide API credentials directly to the connector.

```python
from airbyte_agent_google_search_console import GoogleSearchConsoleConnector
from airbyte_agent_google_search_console.models import GoogleSearchConsoleAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=GoogleSearchConsoleAuthConfig(
        client_id="<The client ID of your Google Search Console developer application.>",
        client_secret="<The client secret of your Google Search Console developer application.>",
        refresh_token="<The refresh token for obtaining new access tokens.>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

### Hosted

In hosted mode, API credentials are stored securely in Airbyte Cloud. You provide your Airbyte credentials instead. 
If your Airbyte client can access multiple organizations, also set `organization_id`.

This example assumes you've already authenticated your connector with Airbyte. See [Authentication](AUTH.md) to learn more about authenticating. If you need a step-by-step guide, see the [hosted execution tutorial](https://docs.airbyte.com/ai-agents/quickstarts/tutorial-hosted).

```python
from airbyte_agent_google_search_console import GoogleSearchConsoleConnector, AirbyteAuthConfig

connector = GoogleSearchConsoleConnector(
    auth_config=AirbyteAuthConfig(
        customer_name="<your_customer_name>",
        organization_id="<your_organization_id>",  # Optional for multi-org clients
        airbyte_client_id="<your-client-id>",
        airbyte_client_secret="<your-client-secret>"
    )
)

@agent.tool_plain # assumes you're using Pydantic AI
@GoogleSearchConsoleConnector.tool_utils
async def google_search_console_execute(entity: str, action: str, params: dict | None = None):
    return await connector.execute(entity, action, params or {})
```

## Full documentation

### Entities and actions

This connector supports the following entities and actions. For more details, see this connector's [full reference documentation](REFERENCE.md).

| Entity | Actions |
|--------|---------|
| Sites | [List](./REFERENCE.md#sites-list), [Get](./REFERENCE.md#sites-get), [Search](./REFERENCE.md#sites-search) |
| Sitemaps | [List](./REFERENCE.md#sitemaps-list), [Get](./REFERENCE.md#sitemaps-get), [Search](./REFERENCE.md#sitemaps-search) |
| Search Analytics By Date | [List](./REFERENCE.md#search-analytics-by-date-list), [Search](./REFERENCE.md#search-analytics-by-date-search) |
| Search Analytics By Country | [List](./REFERENCE.md#search-analytics-by-country-list), [Search](./REFERENCE.md#search-analytics-by-country-search) |
| Search Analytics By Device | [List](./REFERENCE.md#search-analytics-by-device-list), [Search](./REFERENCE.md#search-analytics-by-device-search) |
| Search Analytics By Page | [List](./REFERENCE.md#search-analytics-by-page-list), [Search](./REFERENCE.md#search-analytics-by-page-search) |
| Search Analytics By Query | [List](./REFERENCE.md#search-analytics-by-query-list), [Search](./REFERENCE.md#search-analytics-by-query-search) |
| Search Analytics All Fields | [List](./REFERENCE.md#search-analytics-all-fields-list), [Search](./REFERENCE.md#search-analytics-all-fields-search) |


### Authentication

For all authentication options, see the connector's [authentication documentation](AUTH.md).

### Google-Search-Console API docs

See the official [Google-Search-Console API reference](https://developers.google.com/webmaster-tools/v1/api_reference_index).

## Version information

- **Package version:** 0.1.8
- **Connector version:** 1.0.1
- **Generated with Connector SDK commit SHA:** 09ed4945e89bf743be8a0f0d596ae77c99526607
- **Changelog:** [View changelog](https://github.com/airbytehq/airbyte-agent-connectors/blob/main/connectors/google-search-console/CHANGELOG.md)