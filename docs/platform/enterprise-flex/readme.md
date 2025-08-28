---
products: enterprise-flex
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Enterprise Flex

Airbyte Enterprise Flex is a hybrid solution that consists of a fully managed Cloud control plane that supports separate data planes that run in your own infrastructure. It's ideal for organizations with data sovereignty and compliance requirements who need to carefully manage data movement while also minimizing the time and effort needed to self-manage Airbyte.

## Overview

Many organizations collect data in all types of operational systems from users around the world. However, you might face strict requirements around how you can process and store data, as well as who can access it. These requirements comes in many forms.

- **Compliance**: GDPR (European Union), PIPEDA (Canada), HIPAA (USA), APPs (Australia), PIPL (China), and other frameworks govern the management of data, and can punish non-compliance with significant financial penalties.

- **Data sovereignty**: When sensitive data crosses borders, it can be subject to prying eyes and foreign regulations it isn't meant for. Keeping data within a specific country or geographical region helps ensure privacy and control over that data.

- **Security and operational policies**: Some data, like trade secrets or sensitive industry information, is so valuable that external exposure could present a major incident.

While these requirements are critical, organizations also have finite time and expertise. Managing these operational and compliance requirements with more infrastructure often means increased maintenance commitments, higher spend, and greater complexity.

Enterprise Flex addresses these needs by offering fully managed Cloud workspaces (a control plane) that connect to separate data planes you manage in your own infrastructure. You can also use fully managed data planes for less sensitive data that doesn't need to remain in your own infrastructure. Each Cloud workspace uses one region and data plane, so a single Airbyte instance with multiple workspaces is an ideal way to segregate data and connections.

Enterprise Flex also offers other enterprise-grade abilities.

| Feature             | Description                                                                                                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User Management     | Enable multiple users to concurrently move data from a single Airbyte deployment.                                                                                       |
| Single Sign-On      | Manage user access to Airbyte from your Okta, Azure Entra ID or OIDC-compatible identity provider.                                                                      |
| Multiple Workspaces | Manage multiple isolated projects or teams on a single Airbyte deployment.                                                                                              |
| Role-Based Access   | Manage user permissions and access across workspaces from a single pane of glass.                                                                                       |
| Column Hashing      | Protect sensitive information by hashing personally identifiable information (PII) as it moves through your pipelines.                                                  |
| External Secrets    | Bring your own secrets manager to securely reference your credentials for data sources and destinations.                                                                |
| Audit trail logs    | Store user and platform activity in your own bucket to maintain compliance while using Airbyte .                                                                        |
| Support with SLAs   | [Priority assistance](https://docs.airbyte.com/operator-guides/contact-support/#airbyte-enterprise-self-hosted-support) with deploying, managing and upgrading Airbyte. |

### Enterprise Flex versus Cloud Teams

Enterprise Flex includes all features that are standard in Cloud Teams with the additional capabilities of running self-managed data planes, referencing your own secrets manager, and storing audit logs.

## An example hybrid deployment

Every organization's precise needs differ, so you can implement Enterprise Flex in the way that suits you best. In this example, you have three workspaces. 

- Workspace 1 contains non-sensitive data and uses Airbyte's fully managed European region.

- Workspaces 2 and 3, which contain sensitive data from the United States and Australia, run on your own infrastructure. Only metadata ever reaches the control plane.

![In this example, you have three workspaces. Workspace 1 contains non-sensitive data and uses Airbyte's fully managed European workspace. Workspaces 2 and 3, which contain sensitive data from the United States and Australia, run on your own infrastructure. Only metadata ever reaches the control plane.](img/flex-enterprise-example.png)

## Getting started

Any Airbyte Cloud enviornment can be easily upgraded to Enterprise Flex. To learn more about upgrading to Enterprise Flex, [talk to sales](https://airbyte.com/company/talk-to-sales).

### Infrastructure Prerequisites

You may choose to run a self-managed data plane while using Airbyte Enterprise Flex. **If you are not using any self-managed data planes, then no additional infrastructure is required to begin creating connections and running syncs.**

For a production-ready deployment of self-managed data planes, various infrastructure components are required. We recommend deploying to Amazon EKS or Google Kubernetes Engine. The following diagram illustrates a typical Airbyte Enterpris Flex deployment running a self-managed data plane:

![Airbyte Enterprise Flex Architecture Diagram](./img/enterprise-flex-architecture.png)

| Component                | Recommendation                                                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kubernetes Cluster       | Amazon EKS cluster running on EC2 instances in [2 or more availability zones](https://docs.aws.amazon.com/eks/latest/userguide/disaster-recovery-resiliency.html) on a minimum of 6 nodes. |
| External Secrets Manager | [Amazon Secrets Manager](/platform/operator-guides/configuring-airbyte#secrets) for storing connector 
| Object Storage (Optional)| [Amazon S3 bucket](#configuring-external-logging) with a directory for log storage.                                                                         |

- Self-managed [data planes](https://docs.airbyte.com/platform/enterprise-flex/data-planes) require a Kubernetes cluster to run on. We recommend deploying to Amazon EKS or Google Kubernetes Engine.

A few notes on Kubernetes cluster provisioning for Airbyte Self-Managed Enterprise:

- We support Amazon Elastic Kubernetes Service (EKS) on EC2 or Google Kubernetes Engine (GKE) on Google Compute Engine (GCE). Improved support for Azure Kubernetes Service (AKS) is coming soon.
- While we support GKE Autopilot, we do not support Amazon EKS on Fargate.

We require you to install and configure the following Kubernetes tooling:

1. Install `helm` by following [these instructions](https://helm.sh/docs/intro/install/)
2. Install `kubectl` by following [these instructions](https://kubernetes.io/docs/tasks/tools/).
3. Configure `kubectl` to connect to your cluster by using `kubectl use-context my-cluster-name`:

<details>
<summary>Configure kubectl to connect to your cluster</summary>

<Tabs>
<TabItem value="Amazon EKS" label="Amazon EKS" default>

1. Configure your [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) to connect to your project.
2. Install [eksctl](https://eksctl.io/introduction/).
3. Run `eksctl utils write-kubeconfig --cluster=$CLUSTER_NAME` to make the context available to kubectl.
4. Use `kubectl config get-contexts` to show the available contexts.
5. Run `kubectl config use-context $EKS_CONTEXT` to access the cluster with kubectl.

</TabItem>

<TabItem value="GKE" label="GKE">

1. Configure `gcloud` with `gcloud auth login`.
2. On the Google Cloud Console, the cluster page will have a "Connect" button, with a command to run locally: `gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE_NAME --project $PROJECT_NAME`.
3. Use `kubectl config get-contexts` to show the available contexts.
4. Run `kubectl config use-context $EKS_CONTEXT` to access the cluster with kubectl.

</TabItem>
</Tabs>

</details>

We also require you to create a Kubernetes namespace for your Airbyte deployment:

```
kubectl create namespace airbyte
```

### Limitations and considerations

- While data planes process data in their respective regions, some metadata remains in the control plane.
- Airbyte stores Cursor and Primary Key data in the control plane regardless of data plane location. If you have data that you can't store in the control plane, don't use it as a cursor or primary key.
- The Connector Builder processes all data through the control plane, regardless of workspace settings. This limitation applies to the development and testing phase only; published connectors respect workspace data residency settings during syncs.
- If you want to run multiple data planes in the same region for higher availability, both must be part of the same region in Airbyte and use the same secrets manager to ensure connection credentials are the same.