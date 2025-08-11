---
products: embedded
---

# AI Agents
Airbyte provides multiple tools to help you connect customer data to AI and LLMs

- **Airbyte Embedded Widget**: App development teams who have signed up for Airbyte Embedded and are looking to get started onboarding customers using the Embed Widget can follow the get started guide at the bottom of this page, which will step you through a complete sample onboarding app.
- **Proxy Requests**: Connect safely to Customer APIs using Airbyte's Authentication Proxies.
- **PyAirbyte MCP**: App developers looking to utilize PyAirbyte to generate pipelines in code can follow the steps below to utilize the PyAirbyte MCP server. 


## Airbyte Embedded

[Airbyte Embedded](https://airbyte.com/ai) provides product and software teams the tools and services to move data to provide context for AI applications. Embedded provides the following:

Once your Organization is enabled via Airbyte Embedded, you can begin onboarding customers via the Embed Widget. The Get Started Guide walks you through how to configure a React.js serverless app for the onboarding app. You can download the code for the onboarding app [via GitHub](https://github.com/airbytehq/embedded-sampleweb-reactjs). If you prefer to develop in Node.js, please use [this sample app](https://github.com/airbytehq/embedded-sampleweb-nodejs) instead. Regardless of web framework you choose, the pre-requisites required for initial set up are the same.


## Proxy Requests
[Proxy Requests](./proxy-requests/README.md) provides the ability for application developers call endpoints on behalf of a Customer to retrieve data for use in LLMs and Agents. It support structured (API) and unstructured (files) data.

:::warning
The Airbyte Proxy feature is in alpha, which means it is still in active development and may include backward-incompatbile changes. [Share feedback and requests directly with us](mailto:sonar@airbyte.io).
:::


## PyAirbyte MCP

[The PyAirbyte remote MCP server](./pyairbyte-mcp/README.md) provides the ability for application developers to generate a data pipeline in Python using a single prompt. 