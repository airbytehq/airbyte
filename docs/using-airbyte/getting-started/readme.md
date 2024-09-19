---
products: all
---

# Airbyte Overview

Airbyte is an open-source data integration platform designed to help you consolidate data from various sources into your data warehouses, lakes, and databases.

Whether you're part of a large organization managing complex data pipelines or an individual analyst consolidating data for a personal project, Airbyte can work for you! We offer flexibility and scalability that's easy to tailor to your specific needs, from one-off jobs to enterprise-grade solutions. 

There are two options to consider to run Airbyte: 
- **Airbyte Cloud** (recommended): allows you to focus on moving data while we take care of managing the infrastructure. 
- **Self-Managed Airbyte**: can be deployed either locally or in an infrastructure you've set up. Our Self-Managed solution can be used as a free Community product or implemented with support of Enterprise operations. 

:::tip
If you have already deployed Airbyte or you've signed up to use Airbyte Cloud, and you're familiar with [Airbyte's core concepts](../../using-airbyte/core-concepts/), jump ahead to [Building Connections](../../cloud/managing-airbyte-cloud/configuring-connections.md).
:::

## Airbyte Cloud

To use Airbyte Cloud, [sign up](https://cloud.airbyte.io/signup) with your email address, Google login, or GitHub login. Upon signing up, you'll be taken to your workspace. There, you can collaborate with team members and share resources across your team under a single billing account.

Airbyte Cloud offers a 14-day free trial that begins after your first successful sync. You can find more details about Airbyte Cloud for practitioners and teams, as well as a tool for evaluating costs on our [pricing page](https://www.airbyte.com/pricing).

To start setting up a data pipeline, see how to [set up a source](./add-a-source.md).

## Self-Managed Community (OSS) 

When self-managing Airbyte, your data never leaves your premises. You can use our [OSS Quickstart](oss-quickstart.md) to get started immediately by deploying locally using abctl. 

:::tip
If you're trying Airbyte out for the first time, we'd recommend you sign up for the [Airbyte Cloud trial](https://cloud.airbyte.io/signup) or deploy OSS locally.
:::

To deploy Airbyte in production, Airbyte recommends deploying on [Kubernetes via Helm](../../deploying-airbyte/on-kubernetes-via-helm.md). 

## Self-Managed Enterprise

Airbyte Self-Managed Enterprise is the most robust way to run Airbyte yourself. With this option, you'll have access to all 300+ pre-built connectors and data will never  need to leave your environment. Enterprise setup means that Airbyte becomes self-serve in your organization with new tools to manage multiple users, and the ability to set up multiple teams using Airbyte all in one place.

:::tip
To start with Self-Managed Enterprise, you'll need a license key. [Talk to sales](https://airbyte.com/company/talk-to-sales) to get started with Enterprise. For more details, review our [Enterprise setup guide](/enterprise-setup/README.md).
:::