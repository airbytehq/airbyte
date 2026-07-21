---
products: enterprise-flex
sidebar_label: Get started
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Get started with Enterprise Flex

Any Airbyte Cloud environment can upgrade to Enterprise Flex. To learn more about upgrading, [talk to sales](https://airbyte.com/company/talk-to-sales).

You'll likely use a combination of managed and self-managed data planes. Since Airbyte sets up managed data planes for you, they're preferable when they're an option. Limit the use of self-managed data planes only to those connections that require your self-managed infrastructure.

## Determine which regions you need

Think about the data you need to sync and your data sovereignty and compliance requirements. Generally, these are things you want to consider:

- What data you want to sync, where it's stored today, and where you want it to be stored after syncing.
- Your national, sub-national, industry, and organization compliance and privacy requirements.
- Your data sovereignty needs.
- Your organization's security posture and data handling policies.

Based on this assessment, you should collect a list of how many, and which, regions you need.

## Create a workspace for each region

Each workspace uses a single region, so create one workspace for each region. A good starting pattern is to create one managed workspace for non-sensitive data without compliance and sovereignty requirements, and an additional workspace for each region your connections need to run in. For example, create one Workspace to handle U.S. data, one Workspace to handle Australian data, etc.

## Managed data planes

Managed data planes need no additional infrastructure. Begin adding sources, destinations, and connections in your workspace at your convenience.

## Self-managed data planes

The following diagram illustrates a typical Enterprise Flex deployment running a self-managed data plane.

![Airbyte Enterprise Flex Architecture Diagram](./img/enterprise-flex-architecture.png)

You can deploy a self-managed data plane in Airbyte two ways.

- **Deploy with Helm**: A more traditional Kubernetes deployment using the [Helm](https://helm.sh/) package manager. This method deploys your data plane to a Kubernetes cluster like an Amazon EKS cluster. It's the right choice for teams that have in-house Kubernetes expertise. [**Deploy with Helm >**](data-plane)

- **Deploy with Airbox**: Airbox is Airbyte's utility for simplified, single-node data plane deployments, like on a virtual machine. This utility abstracts away most of the nuance of a Kubernetes deployment. It's the right choice for teams with limited Kubernetes expertise. [**Deploy with Airbox >**](data-plane-util)

### Limitations and considerations

- While data planes process data in their respective regions, some metadata remains in the control plane.

    - Airbyte stores Cursor and Primary Key data in the control plane regardless of data plane location. If you have data that you can't store in the control plane, don't use it as a cursor or primary key.

- The Connector Builder processes all data through the control plane, regardless of workspace settings. This limitation applies to the development and testing phase only; published connectors respect workspace data residency settings during syncs.

- If you want to run multiple data planes in the same region for higher availability, both must be part of the same region in Airbyte and use the same secrets manager to ensure connection credentials are the same.

- Data planes and the control plane must be configured to use the same secrets manager.

    - This ensures that when you enter credentials in the UI, they are written to the secrets manager and available to the data plane when running syncs.

- Data planes must be able to communicate with the control plane.

- Data planes only send requests to the control plane and never require inbound requests.
