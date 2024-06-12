---
displayed_sidebar: docs
---

# Welcome to Airbyte Docs

## What is Airbyte?

Airbyte is an open-source data movement infrastructure for building extract and load (EL) data pipelines. It is designed for versatility, scalability, and ease-of-use.

There are three major components to know in Airbyte:

1. **The connector catalog**
   - **350+ pre-built connectors**: Airbyte’s connector catalog comes “out-of-the-box” with over 350 pre-built connectors. These connectors can be used to start replicating data from a source to a destination in just a few minutes.
   - **No-Code Connector Builder**: You can easily extend Airbyte’s functionality to support your custom use cases through tools like the [No-Code Connector Builder](/connector-development/connector-builder-ui/overview).
2. **The platform:** Airbyte’s platform provides all the horizontal services required to configure and scale data movement operations, available as [cloud-managed](https://airbyte.com/product/airbyte-cloud) or [self-managed](https://airbyte.com/product/airbyte-enterprise).
3. **The user interface:** Airbyte features a UI, [**PyAirbyte**](/using-airbyte/pyairbyte/getting-started) (Python library), [**API**](/api-documentation), and [**Terraform Provider**](/terraform-documentation) to integrate with your preferred tooling and approach to infrastructure management.

Airbyte is suitable for a wide range of data integration use cases, including AI data infrastructure and EL(T) workloads. Airbyte is also [embeddable](https://airbyte.com/product/powered-by-airbyte) within your own application or platform to power your product.

<Arcade id="0k75Pa9c9EvrJb8zFsuU" title="Airbyte Demo" paddingBottom="calc(61.416666666666664% + 41px)" />

## For Airbyte Cloud users

Browse the [connector catalog](/integrations/) to find the connector you want. In case the connector is not yet supported on Airbyte Cloud, consider using [Airbyte Open Source](#for-airbyte-open-source-users).

Next, check out the [step-by-step tutorial](/using-airbyte/getting-started) to sign up for Airbyte Cloud, understand Airbyte [concepts](/using-airbyte/core-concepts), and run your first sync.

## For Airbyte Open Source users

Browse the [connector catalog](/integrations/) to find the connector you want. If the connector is not yet supported on Airbyte Open Source, [build your own connector](/connector-development/).

Next, check out the [Airbyte Open Source QuickStart](/deploying-airbyte/quickstart). Then learn how to [deploy](/deploying-airbyte/quickstart) and [manage](/operator-guides/upgrading-airbyte) Airbyte Open Source in your cloud infrastructure.

## For Airbyte contributors

To contribute to Airbyte code, connectors, and documentation, refer to our [Contributing Guide](/contributing-to-airbyte/).

[![GitHub stars](https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000)](https://GitHub.com/airbytehq/airbyte/stargazers/) [![License](https://img.shields.io/static/v1?label=license&message=MIT&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md) [![License](https://img.shields.io/static/v1?label=license&message=ELv2&color=brightgreen)](https://github.com/airbytehq/airbyte/tree/a9b1c6c0420550ad5069aca66c295223e0d05e27/LICENSE/README.md)
