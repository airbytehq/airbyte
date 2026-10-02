---
products: all
---

# Airbyte platform

import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

Airbyte is an open source data integration and activation platform. It helps you consolidate data from hundreds of sources into your data warehouses, data lakes, and databases. Then, it helps you move data from those locations into the operational tools where work happens, like CRMs, marketing platforms, and support systems.

Whether you're part of a large organization managing complex data pipelines or an individual analyst consolidating data, Airbyte works for you. Airbyte offers flexibility and scalability that's easy to tailor to your specific needs, from one-off jobs to enterprise solutions.

## Airbyte plans

Airbyte is available as a self-managed, hybrid, or fully managed cloud solution. [Compare plans and pricing >](https://airbyte.com/pricing)

### Self-managed plans

<Grid columns="2">

<CardWithIcon title="Self-Managed Enterprise" description="Highly available, secure data movement for your entire organization. Keep your data sovereign and on your premises with self-managed data planes" ctaText="Enterprise setup" ctaLink="/platform/enterprise-setup" icon="fa-lock" />

<CardWithIcon title="Core" description="Our free and open-source version of Airbyte. Deploy locally or in your own infrastructure. Get started immediately and keep your data on your premises." ctaText="Quickstart" ctaLink="using-airbyte/getting-started/oss-quickstart" icon="fa-download" />

</Grid>

### Cloud and hybrid plans

<Grid columns="3">

<CardWithIcon title="Standard" description="A cloud solution that provides a fully managed experience for data replication. Focus on moving data while Airbyte manages the infrastructure. Free 30-day trial." ctaText="Sign up" ctaLink="https://cloud.airbyte.com/signup" icon="fa-cloud" />

<CardWithIcon title="Pro" description="A cloud solution for organizations looking to scale efficiently. Role based access control, single sign on, and more ensure Pro is a robust solution that can grow with your team." ctaText="Talk to Sales" ctaLink="https://airbyte.com/company/talk-to-sales" icon="fa-lock" />

<CardWithIcon title="Enterprise Flex" description="An enterprise-grade, hybrid solution with for organizatons seeking the convenience of a fully managed solution with separate data planes for compliance and data sovereignty." ctaText="Learn more" ctaLink="enterprise-flex" icon="fa-lock" />

</Grid>

## Ways to work with Airbyte

Once your Airbyte instance is up and running, there's a way to use Airbyte that's appropriate for any skill level.

### User interface

Self-managed and cloud plans come with a carefully-crafted user interface that walks you through setting up connections and automating syncs. This is a great choice if you're not a developer, aren't concerned about version control, or you're just seeing what Airbyte can do for you.

### API and Python SDK {#api-sdk}

These are great choices for developers who want to automate the way you work with Airbyte and use version control to preserve a history of changes.

- Airbyte's [API documentation](https://reference.airbyte.com) gives you programmatic access to Airbyte with code snippets in all common languages.
- Airbyte's [Python SDK](https://github.com/airbytehq/airbyte-api-python-sdk) lets you programmatically control your Airbyte instance with Python.

### Terraform

Many people think of Airbyte and its connectors as infrastructure. Our [Terraform provider](/developers/terraform-documentation) ensures you can deploy and manage sources and destinations with Terraform, the same way you manage your other infrastructure today.

### PyAirbyte

If you want to use Python to move data, our Python library, [PyAirbyte](/developers/pyairbyte), might be the best fit for you. It's a good choice if you're using Jupyter Notebook or iterating on an early prototype for a large data project and don't need to run a server. PyAirbyte isn't an SDK for managing Airbyte. If that's what you're looking for, use the [API or Python SDK](#api-sdk).

## Why Airbyte?

Teams and organizations need efficient and timely data access to an ever-growing list of data sources. In-house data pipelines are brittle and costly to build and maintain. Airbyte's unique open source approach enables your data stack to adapt as your data needs evolve.

- **Wide connector availability:** Airbyte's connector catalog comes "out-of-the-box" with over 600 pre-built connectors. These connectors can be used to start replicating data from a source to a destination in just a few minutes.
- **Long-tail connector coverage:** You can easily extend Airbyte's capability to support your custom use cases through Airbyte's [No-Code Connector Builder](/platform/connector-development/connector-builder-ui/overview).
- **Robust platform** provides horizontal scaling required for large-scale data movement operations, available as [Cloud-managed](https://airbyte.com/product/airbyte-cloud) or [Self-managed](https://airbyte.com/product/airbyte-enterprise).
- **Accessible User Interfaces** through the UI, [**PyAirbyte**](/developers/pyairbyte) (Python library), [**API**](/developers/api-documentation), and [**Terraform Provider**](/developers/terraform-documentation) to integrate with your preferred tooling and approach to infrastructure management.

Airbyte is suitable for a wide range of data integration use cases, including AI data infrastructure and EL(T) workloads. Airbyte is also [embeddable](https://airbyte.com/product/powered-by-airbyte) within your own app or platform to power your product.

## Contribute

Airbyte is an open source product. This is vital to Airbyte's vision of data movement. The world has seemingly infinite data sources, and only through community collaboration can we address that long tail of data sources.

If you don't see the data source you need in Airbyte's collection, [you can build one](/platform/connector-development/). Airbyte comes with no-code, low-code, and programmatic builder options. If you're interested in giving back to the community, documenting your connector and publishing it in the [Marketplace](/integrations/) will help others like you move data in the future.
