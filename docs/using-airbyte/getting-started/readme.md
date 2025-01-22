import Tabs from "@theme/Tabs";
import TabItem from "@theme/TabItem";

# Airbyte Overview

Airbyte is an open-source data integration platform to help you consolidate data from various sources into your data warehouses, lakes, and databases.

Whether you're part of a large organization managing complex data pipelines or an individual analyst consolidating data for a personal project, Airbyte can work for you! We offer flexibility and scalability that's easy to tailor to your specific needs, from one-off jobs to enterprise solutions.

## Airbyte Products

Airbyte is available as a Self-Managed or Cloud product, depending on your needs.

### Self-Managed options

<Grid columns="2">

<CardWithIcon title="Self-Managed Enterprise" description="Highly available, secure data movement for your entire organization. To start with Self-Managed Enterprise, you need a license key. For more details, read the enterprise setup guide." ctaText="Enterprise Setup" ctaLink="../../enterprise-setup" icon="fa-lock" />

<CardWithIcon title="Self-Managed Community" description="Our open-source version of Airbyte. Deploy locally or in your own infrastructure. Get started immediately and keep your data on your premises." ctaText="Quickstart" ctaLink="oss-quickstart" icon="fa-download" />

</Grid>

### Cloud options

<Grid columns="2">

<CardWithIcon title="Cloud" description="A Cloud-native version of Airbyte that provides a fully managed experience for data replication. Focus on moving data while Airbyte manages the infrastructure. Free 14-day trial." ctaText="Sign Up for Cloud" ctaLink="https://cloud.airbyte.com/signup" icon="fa-cloud" />

<CardWithIcon title="Cloud Teams" description="For organizations
looking to scale efficiently. Role based access control, single sign on, and more ensure Cloud is a robust solution that can grow with your team." ctaText="Talk to Sales" ctaLink="https://airbyte.com/company/talk-to-sales" icon="fa-lock" />

</Grid>

## Ways to work with Airbyte

No matter your skill level, there's a way to use Airbyte that's appropriate for you.

### User interface

Self-Managed and Cloud versions of Airbyte come with a carefully-crafted user interface that walks you through setting up connections and automating syncs. This is a great choice if you're not a developer, aren't concerned about version control, or you're just seeing what Airbyte can do for you.

### API and Python SDK {#api-sdk}

These are great choices for developers who want to automate the way you work with Airbyte and use version control to preserve a history of changes.

- Airbyte's [API documentation](https://reference.airbyte.com) gives you programmatic access to Airbyte with code snippets in all common languages.
- Airbyte's [Python SDK](https://github.com/airbytehq/airbyte-api-python-sdk) lets you programmatically control your Airbyte instance with Python.

### Terraform

You might want to think of Airbyte and its connectors as infrastructure. Our [Terraform provider](../../terraform-documentation) ensures you can deploy and manage sources and destinations with Terraform, the same way you manage your existing infrastructure.

### PyAirbyte

If you want to use Python to move data, our Python library, [PyAirbyte](../pyairbyte/getting-started.mdx), might be the best fit for you. It's a good choice if you're using Jupyter Notebook or iterating on an early prototype for a large data project and don't need to run a server.

:::note
PyAirbyte isn't an SDK for managing Airbyte. If that's what you're looking for, use the [API or Python SDK](#api-sdk).
:::

## Build your own connectors

Airbyte began as an open-source product. This is vital to Airbyte's vision of data movement. There are seemingly infinite data sources in the world, and only through community contribution can we address that long tail of data sources.

If you don't see the data source you need in our collection, [you can build one](../../connector-development/). Airbyte comes with no-code, low-code, and programmatic builder options. If you're interested in giving back to the community, documenting your connector and publishing it in the [Marketplace](../../integrations) will help others like you move data in the future.

