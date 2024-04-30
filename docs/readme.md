---
displayed_sidebar: docs
---

import OctaviaComic from './assets/docs/after-xkcd-airbyte-2.jpg'

import AirbyteGif from './assets/docs/airbyte_product.gif'

# Welcome to Airbyte Docs

## What is Airbyte?

Airbyte is an open-source data movement infrastructure for building extract and load (EL) data
pipelines. It is designed for versatility, scalability, and ease-of-use.

There are three major components to know in Airbyte:

1. **The connector catalog**
   - **350+ pre-built connectors**: Airbyte’s connector catalog comes “out-of-the-box” with over 350
     pre-built connectors. These connectors can be used to start replicating data from a source to a
     destination in just a few minutes.
   - **No-Code Connector Builder**: You can easily extend Airbyte’s functionality to support your
     custom use cases through tools like the
     [No-Code Connector Builder](/connector-development/connector-builder-ui/overview).
2. **The platform:** Airbyte’s platform provides all the horizontal services required to configure
   and scale data movement operations, available as
   [cloud-managed](https://airbyte.com/product/airbyte-cloud) or
   [self-managed](https://airbyte.com/product/airbyte-enterprise).
3. **The user interface:** Airbyte features a UI,
   [**PyAirbyte**](/using-airbyte/pyairbyte/getting-started) (Python library),
   [**API**](/api-documentation), and [**Terraform Provider**](/terraform-documentation) to
   integrate with your preferred tooling and approach to infrastructure management.

Airbyte is suitable for a wide range of data integration use cases, including AI data infrastructure
and EL(T) workloads. Airbyte is also [embeddable](https://airbyte.com/product/powered-by-airbyte)
within your own application or platform to power your product.

<div align="center" >
   <img src={AirbyteGif} alt="Airbyte Product GIF" width="800" height="470" />
</div>

## Why an open-source data movement infrastructure?

Today, teams and organizations require efficient and timely data access to an ever-growing list of
data sources. In-house data pipelines are brittle and costly to build and maintain. How many times
have we been in this situation?

<div align="center" >
   <img src={OctaviaComic} alt="Octavia Comic" width="700" height="700"/>
</div>

Closed-source solutions are inflexible, and will always often still require complimentary in-house
solutions. So at this point, investing in such solutions is just postponing the moment you’ll pile
up very costly data pipeline technical debts. Is there a way to have a scalable and efficient data
movement infrastructure that will enable your data team to be successful? That’s why we created
Airbyte.

## Getting Started

There are 4 products to Airbyte:

1. [Airbyte Open-Source](/category/deploy-airbyte): Check out the
   [Airbyte Open Source QuickStart](/using-airbyte/getting-started). Then learn how to
   [deploy](/deploying-airbyte/local-deployment) and [manage](/operator-guides/upgrading-airbyte)
   Airbyte Open Source in your cloud infrastructure.
2. [Airbyte Cloud](http://cloud.airbyte.com/signup): Cloud is the fastest way to start syncing your
   data in minutes.
3. [Airbyte Enterprise](https://airbyte.com/product/airbyte-enterprise): Own your data
   infrastructure, with advanced features and premium support.
4. [Powered by Airbyte](https://reference.airbyte.com/reference/powered-by-airbyte?_gl=1*2lrnqy*_gcl_au*MTM1OTY1NTMzNi4xNzEyNjIwMDY3):
   White-label Airbyte to offer data integration features for your end users.

## Resources

If you want to learn more:

- [Build vs. Buy your data pipelines](https://build-vs-buy.airbyte.com/)
- [Industry’s survey on the best data infrastructure tools](https://state-of-data.com/)
- [How Airbyte Powers Datadog’s Self-Serve Analytics Tool](https://airbyte.com/success-stories/datadog)
