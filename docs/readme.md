---
displayed_sidebar: docs
---

# Welcome to Airbyte Docs

## What is Airbyte?

Airbyte is an open-source data movement infrastructure designed for versatility, scalability, and ease-of-use.Use it to build extract and load (EL) data pipelines.

Airbyte is suitable for a wide range of data integration use cases, including AI data infrastructure and EL(T) workloads. You can also [embed](https://airbyte.com/product/powered-by-airbyte) Airbyte within your own application or platform to power your product.

There are three options to choose from when using Airbyte: 
- [Airbyte Cloud](https://airbyte.com/product/airbyte-cloud) (recommended for a fully managed solution) 
- Self-Hosted Community (free to use on your own infrastructure)
- [Self-Hosted Enterprise](https://airbyte.com/product/airbyte-enterprise) (offers the flexibility of using your own infrastructure with added support and SLAs)

Refer to our [feature comparison page](https://airbyte.com/product/features) as you decide which option is right for you.

Understanding the following three major components of Airbyte will help as you get started:

1. **The connector catalog**
   - **350+ pre-built connectors**: Airbyte’s connector catalog comes “out-of-the-box” with over 350 pre-built connectors. You can use these connectors to start replicating data from a source to a destination in just a few minutes.
   - **No-Code Connector Builder**: You can easily extend Airbyte’s functionality to support your custom use cases with the [No-Code Connector Builder](https://docs.airbyte.com/connector-development/connector-builder-ui/overview).
2. **The platform:** Airbyte’s platform provides all the horizontal services required to configure and scale data movement operations.
3. **The user interface:** Airbyte offers several ways to interact with the platform: a UI, [**PyAirbyte**](https://docs.airbyte.com/pyairbyte) (Python library), [**API**](https://docs.airbyte.com/api-documentation), and [**Terraform Provider**](https://docs.airbyte.com/terraform-documentation) to integrate with your preferred tooling and approach to infrastructure management.

<Arcade id="0k75Pa9c9EvrJb8zFsuU" title="Airbyte Demo" />

## For Airbyte Cloud users

Browse the [connector catalog](/integrations/) to find the connectors you want. If a connector you would like to use is not yet supported on Airbyte Cloud, consider using [Airbyte Open Source](#for-airbyte-open-source-users).

Next, check out the [step-by-step tutorial](/using-airbyte/getting-started) to sign up for Airbyte Cloud, understand Airbyte [concepts](/using-airbyte/core-concepts), and run your first sync.

## For Airbyte Open Source users

Browse the [connector catalog](/integrations/) to find the connector you want. If the connector you're looking for is not yet supported on Airbyte Open Source, you can [build your own connector](/connector-development/).

Next, check out the [Airbyte Open Source QuickStart](/deploying-airbyte/local-deployment). Then learn how to [deploy](/deploying-airbyte/local-deployment) and [manage](/operator-guides/upgrading-airbyte) Airbyte Open Source in your cloud infrastructure.

## For Airbyte contributors

Refer to our [Contributing Guide](/contributing-to-airbyte/) for information on how you can contribute to Airbyte code, connectors, and documentation.

[![GitHub stars](https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000)](https://GitHub.com/airbytehq/airbyte/stargazers/) [![License](https://img.shields.io/static/v1?label=license&message=MIT&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md) [![License](https://img.shields.io/static/v1?label=license&message=ELv2&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md)
